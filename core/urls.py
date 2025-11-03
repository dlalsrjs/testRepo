# epalist/core/urls.py
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # 상세 용량 정보를 위한 URL 패턴 추가
    path('size_details/<str:model_name>/', views.size_details, name='size_details'),

    path('japanese_work_tags/', views.japanese_work_tag_list, name='japanese_work_tag_list'),
    path('korean_person_tags/', views.korean_person_tag_list, name='korean_person_tag_list'),
    path('korean_video_themes/', views.korean_video_theme_list, name='korean_video_theme_list'),
    path('korean_video_tags/', views.korean_video_tag_list, name='korean_video_tag_list'),

    path('japanese_work_tags/<int:pk>/edit/', views.edit_japanese_work_tag, name='edit_japanese_work_tag'),
    path('korean_person_tags/<int:pk>/edit/', views.edit_korean_person_tag, name='edit_korean_person_tag'),
    path('korean_video_themes/<int:pk>/edit/', views.edit_korean_video_theme, name='edit_korean_video_theme'),
    path('korean_video_tags/<int:pk>/edit/', views.edit_korean_video_tag, name='edit_korean_video_tag'),

    path('japanese_work_tags/<int:pk>/delete/', views.delete_japanese_work_tag, name='delete_japanese_work_tag'),
    path('korean_person_tags/<int:pk>/delete/', views.delete_korean_person_tag, name='delete_korean_person_tag'),
    path('korean_video_themes/<int:pk>/delete/', views.delete_korean_video_theme, name='delete_korean_video_theme'),
    path('korean_video_tags/<int:pk>/delete/', views.delete_korean_video_tag, name='delete_korean_video_tag'),
]