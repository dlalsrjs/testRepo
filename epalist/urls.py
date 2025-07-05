"""
URL configuration for epalist project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings # MEDIA_URL, MEDIA_ROOT 사용을 위해 추가
from django.conf.urls.static import static # MEDIA_URL, MEDIA_ROOT 사용을 위해 추가
from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', core_views.home, name='home'), # 메인 화면 URL (루트 경로)
    path('persons/', include('persons.urls')), # persons 앱의 URL을 포함
    path('videos/', include('videos.urls')),   # videos 앱의 URL을 포함
    path('core/', include('core.urls')), # core 앱의 URL을 포함 (태그 목록 등을 보여줄 수 있습니다)
    # 필요하다면 여기에 기본 랜딩 페이지를 추가할 수 있습니다. 예: path('', some_view, name='home')
]

# 개발 환경에서 미디어 파일(이미지 등)을 서빙하기 위한 설정
# DEBUG = True 일 때만 작동합니다.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)