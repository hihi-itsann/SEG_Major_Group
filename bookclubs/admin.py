from django.contrib import admin
from .models import Book

# Register your models here.
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = [
        'ISBN','title', 'author', 'year_of_publication', 'publisher', 'image_url_s', 'image_url_m', 'image_url_l'
    ]
