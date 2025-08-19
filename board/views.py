# /board/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from .models import Post, Category
from .forms import PostForm
from django.db.models import Q

class PostListView(ListView):
    model = Post
    template_name = 'board/board_list.html'
    context_object_name = 'posts'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q', '')
        category_id = self.request.GET.get('category', '')

        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) | Q(content__icontains=q)
            )

        if category_id:
            queryset = queryset.filter(category__id=category_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['q'] = self.request.GET.get('q', '')
        context['selected_category'] = self.request.GET.get('category', '')
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = 'board/board_detail.html'

class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'board/board_form.html'
    success_url = reverse_lazy('board:post_list')

class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'board/board_form.html'

    def get_success_url(self):
        return reverse_lazy('board:post_detail', kwargs={'pk': self.object.pk})