# /board/models.py
from django.db import models
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="말머리")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "게시판 말머리"
        verbose_name_plural = "게시판 말머리들"

class Post(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="말머리")
    title = models.CharField(max_length=200, verbose_name="제목")
    content = models.TextField(verbose_name="내용")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('board:post_detail', args=[self.pk])

    class Meta:
        verbose_name = "게시글"
        verbose_name_plural = "게시글들"
        ordering = ['-created_at']