from django.shortcuts import render
from catalog.models import Book, Author, BookInstance, Genre
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin

def index(request):
	"""View function for home page of site."""

	#Generate counts of some of the main objects
	num_books = Book.objects.all().count()
	num_instances = BookInstance.objects.all().count()
	
	# Available books (status = 'a')
	num_instances_available = BookInstance.objects.filter(status__exact='a').count()
	
	# The 'all()' is implied by default.
	num_authors = Author.objects.count()
	
	# filter genres and books that contain the specified word
	num_books_contain_action = Book.objects.filter(summary__icontains='action').count()
	num_genres_contain_action = Genre.objects.filter(name__icontains='action').count()
	
	# Number of visits to this view, as counted in the session variable.
	num_visits = request.session.get('num_visits', 0)
	request.session['num_visits'] = num_visits + 1
	
		
	context = {
		'num_books': num_books,
		'num_instances': num_instances,
		'num_instances_available': num_instances_available,
		'num_authors': num_authors,	
		'num_books_contain_action': num_books_contain_action,
		'num_genres_contain_action': num_genres_contain_action,
		'num_visits': num_visits,
	}
	
	# Render the HTML template index.html with the data in the context variable
	return render(request, 'index.html', context=context)


class BookListView(LoginRequiredMixin, generic.ListView):
	model = Book
	context_object_name = 'book_list'
	paginate_by = 4
	

class BookDetailView(LoginRequiredMixin, generic.DetailView):
	model = Book
	

class AuthorListView(LoginRequiredMixin, generic.ListView):
	model = Author
	paginate_by = 10
	

class AuthorDetailView(LoginRequiredMixin, generic.DetailView):
	model = Author
	
class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
	"""Generic class-based view listing books on loan to current user."""
	model = BookInstance
	template_name = 'catalog/bookinstance_list_borrowed_user.html'
	paginate_by = 10
	
	def get_queryset(self):
		return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')
		

class AllLoanedBooksListView(PermissionRequiredMixin, generic.ListView):
	"""Generic class-based view listing all books on loan to library members."""
	permission_required = 'catalog.can_mark_returned'
	model = BookInstance
	template_name = 'catalog/bookinstance_list_all_borrowed_books.html'
	paginate_by = 10
	
	def get_queryset(self):
		return BookInstance.objects.filter(status__exact='o').order_by('due_back')
		
		

import datetime

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from catalog.forms import RenewBookForm

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
	"""View function for renewing a secific BookInstance by librarian."""
	book_instance = get_object_or_404(BookInstance, pk=pk)
	
	# If this is a POST request then process the Form data
	if request.method == 'POST':
		
		#Create a form instance and populate it with data from the request (binding):
		form = RenewBookForm(request.POST)
		
		# Check if the form is valid:
		if form.is_valid():
			# process the data in form.cleaned_data as required (here we just write it to the model due_back field)
			book_instance.due_back = form.cleaned_data['renewal_date']
			book_instance.save()
			
			# Redirect to a new URL:
			return HttpResponseRedirect(reverse('all-borrowed'))
			
	
	# If this is a GET (or any other method) create the default forrm.
	else:
		proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
		form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})
		
	context = {
		'form': form,
		'book_instance': book_instance,
	}
	
	return render(request, 'catalog/book_renew_librarian.html', context)
	

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from catalog.models import Author

class AuthorCreate(CreateView):
	model = Author
	fields = '__all__'
	initial = {'date_of_death': '05/01/2018'}
	
class AuthorUpdate(UpdateView):
	model = Author
	fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
	
	
class AuthorDelete(DeleteView):
	model = Author
	success_url = reverse_lazy('authors')
	
	
class BookCreate(CreateView):
	model = Book
	fields = '__all__'
	
class BookUpdate(UpdateView):
	model = Book
	fields = '__all__'
	
class BookDelete(DeleteView):
	model = Book
	success_url = reverse_lazy('books')

	