from django.contrib import admin
from .models import JapanesePhoto, JapanesePhotoImage, KoreanPhoto, KoreanPhotoImage

class JapanesePhotoImageInline(admin.TabularInline):
    model = JapanesePhotoImage
    extra = 1

@admin.register(JapanesePhoto)
class JapanesePhotoAdmin(admin.ModelAdmin):
    inlines = [JapanesePhotoImageInline]
    list_display = ('id', 'description', 'year', 'created_at')
    search_fields = ('description', 'actors__name', 'tags__name')
    list_filter = ('year',)
    filter_horizontal = ('actors', 'tags')

class KoreanPhotoImageInline(admin.TabularInline):
    model = KoreanPhotoImage
    extra = 1

@admin.register(KoreanPhoto)
class KoreanPhotoAdmin(admin.ModelAdmin):
    inlines = [KoreanPhotoImageInline]
    list_display = ('id', 'description', 'year', 'created_at')
    search_fields = ('description', 'persons__name', 'tags__name')
    list_filter = ('year',)
    filter_horizontal = ('persons', 'tags')