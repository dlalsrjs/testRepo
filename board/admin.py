# /board/admin.py
from django.contrib import admin
from .models import Post, Category
from django_summernote.admin import SummernoteModelAdmin

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Post)
class PostAdmin(SummernoteModelAdmin):
    list_display = ('title', 'category', 'created_at')
    list_filter = ('category',)
    search_fields = ('title', 'content')
    summernote_fields = ('content',)