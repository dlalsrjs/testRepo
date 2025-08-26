from django.urls import path
from . import views

app_name = 'photos'

urlpatterns = [
    path('japanese/', views.japanese_photo_list, name='japanese_photo_list'),
    path('korean/', views.korean_photo_list, name='korean_photo_list'),
    path('detail/<str:model_name>/<int:pk>/', views.photo_detail_json, name='photo_detail_json'),
    
    path('japanese/<int:pk>/edit/', views.edit_japanese_photo, name='edit_japanese_photo'),
    path('japanese/<int:pk>/delete/', views.delete_japanese_photo, name='delete_japanese_photo'),
    path('korean/<int:pk>/edit/', views.edit_korean_photo, name='edit_korean_photo'),
    path('korean/<int:pk>/delete/', views.delete_korean_photo, name='delete_korean_photo'),
]