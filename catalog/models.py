from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date
import uuid

class Genre(models.Model):
	"""Model representing a book genre."""
	name = models.CharField(max_length=200, help_text='Enter a book genre (e.g. Science Fiction)')
	
	def __str__(self):
		""" String for representing the model object."""
		return self.name

class Book(models.Model):
	""" A model representing a book (but not a specific copy of a book)."""
	title = models.CharField(max_length=200)
	
	author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
	
	summary = models.TextField(max_length=1000, help_text='Enter a brief description of the book')
	isbn = models.CharField('ISBN', max_length=13, help_text='13 Character <a href="https://www.isbn-international.ord/content/what-isbn">ISBN number</a>')
	
	genre = models.ManyToManyField(Genre, help_text='Select a genre of this book')
	
	def __str__(self):
		"""String for representing the model object."""
		return self.title
		
	def get_absolute_url(self):
		"""Returns a url to access a detail record of this book."""
		return reverse('book-detail', args=[str(self.id)])
	
	def display_genre(self):
		"""Create a string for the Genre. This is required to display genre in Admin."""
		return ', '.join(genre.name for genre in self.genre.all()[:3])
	
	
		
	display_genre.short_description = 'Genre'
		
class BookInstance(models.Model):
	"""Model representing a specific copy of a book (i.e. that can be borrowed from the library)."""
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular book across whole library')
	book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True)
	imprint = models.CharField(max_length=200)
	due_back = models.DateField(null=True, blank=True)
	borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
	
	LOAN_STATUS = (
		('m', 'Maintenance'),
		('o', 'On loan'),
		('a', 'Available'),
		('r', 'Reserved'),
	)
	
	status = models.CharField(
		max_length=1,
		choices=LOAN_STATUS,
		blank=True,
		default='m',
		help_text='Book availability',
	)
	
	class Meta:
		ordering = ['due_back']
		permissions = (("can_mark_returned", "Set book as returned"),)
		
	@property
	def is_overdue(self):
		if self.due_back and date.today() > self.due_back:
			return True
		return False
	
	def __str__(self):
		"""String for representing the Model object."""
		return f'{self.id} ({self.book.title})' 
		
class Author(models.Model):
	"""Model representing an author."""
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	date_of_birth = models.DateField(null=True, blank=True)
	date_of_death = models.DateField('died', null=True, blank=True)
	
	class Meta:
		ordering = ['last_name', 'first_name']
		
	def get_absolute_url(self):
		"""Returns the url to access a particular author instance."""
		return reverse('author-detail', args=[str(self.id)])
		
	def __str__(self):
		"""String for representing the Model object."""
		return f'{self.last_name}, {self.first_name}'