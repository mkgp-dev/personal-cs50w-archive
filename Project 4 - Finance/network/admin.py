from django.contrib import admin
from .models import Post

# Clean
class Post_Custom(admin.ModelAdmin):
	list_display = ('user', 'content', 'created')
	search_fields = ('user', 'content')

# Debug
admin.site.register(Post, Post_Custom)