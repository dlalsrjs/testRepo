# videos/urls.py
from django.urls import path
from . import views

app_name = 'videos'

urlpatterns = [
    path('japanese_works/', views.japanese_work_list, name='japanese_work_list'),
    path('korean_videos/', views.korean_video_list, name='korean_video_list'),
    path('local_videos/', views.local_video_list, name='local_video_list'),
    path('japanese_works/<int:pk>/edit/', views.edit_japanese_work, name='edit_japanese_work'),
    path('korean_videos/<int:pk>/edit/', views.edit_korean_video, name='edit_korean_video'),
    path('local_videos/<uuid:pk>/edit/', views.edit_local_video, name='edit_local_video'),

    # ----------- 삭제 URL 추가 -----------
    path('japanese_works/<int:pk>/delete/', views.delete_japanese_work, name='delete_japanese_work'),
    path('korean_videos/<int:pk>/delete/', views.delete_korean_video, name='delete_korean_video'),
    path('local_videos/<uuid:pk>/delete/', views.delete_local_video, name='delete_local_video'),

    path('check-duplicate-url/', views.check_duplicate_url, name='check_duplicate_url'),
]