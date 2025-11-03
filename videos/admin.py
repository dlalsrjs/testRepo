# videos/admin.py

from django.contrib import admin
from .models import JapaneseWork, KoreanVideo, LocalVideo

@admin.register(JapaneseWork)
class JapaneseWorkAdmin(admin.ModelAdmin):
    list_display = ('product_number', 'release_year', 'work_hardness', 'rating')
    search_fields = ('product_number', 'rating', 'actors__name', 'tags__name')
    list_filter = ('release_year', 'work_hardness')
    filter_horizontal = ('actors', 'tags')
    autocomplete_fields = ['actors']

    class Media:
        js = ('videos/url_validation.js',) # 이 줄을 추가합니다.

@admin.register(KoreanVideo)
class KoreanVideoAdmin(admin.ModelAdmin):
    list_display = ('get_first_url', 'date', 'edited')
    search_fields = ('urls', 'description', 'persons__name', 'themes__name', 'tags__name')
    list_filter = ('date', 'edited')
    filter_horizontal = ('persons', 'themes', 'tags')
    autocomplete_fields = ['persons']

    def get_first_url(self, obj):
        return obj.urls[0] if obj.urls else "No URL"
    get_first_url.short_description = '대표 URL'

    class Media:
        js = ('videos/url_validation.js',) # 이 줄을 추가합니다.

@admin.register(LocalVideo)
class LocalVideoAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'description')
    search_fields = ('uuid__icontains', 'description', 'persons__name')
    filter_horizontal = ('persons',)
    autocomplete_fields = ['persons']