# /board/forms.py
from django import forms
from .models import Post, Category
from django_summernote.widgets import SummernoteWidget

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'category', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'content': SummernoteWidget(),
        }
        labels = {
            'title': '제목',
            'category': '말머리',
            'content': '내용',
        }