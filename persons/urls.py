# persons/urls.py
from django.urls import path
from . import views

app_name = 'persons'

urlpatterns = [
    path('japanese_actors/', views.japanese_actor_list, name='japanese_actor_list'),
    path('korean_persons/', views.korean_person_list, name='korean_person_list'),
    path('japanese_actors/<int:pk>/edit/', views.edit_japanese_actor, name='edit_japanese_actor'),
    path('korean_persons/<int:pk>/edit/', views.edit_korean_person, name='edit_korean_person'),
    path('japanese_actors/<int:pk>/delete/', views.delete_japanese_actor, name='delete_japanese_actor'),
    path('korean_persons/<int:pk>/delete/', views.delete_korean_person, name='delete_korean_person'),

    # ----------- 새로운 리다이렉트 URL 추가 -----------
    path('japanese_actors/<int:pk>/works/', views.view_works_by_actor, name='view_works_by_actor'),
    path('korean_persons/<int:pk>/videos/', views.view_videos_by_person, name='view_videos_by_person'),
]