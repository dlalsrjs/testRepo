from django.contrib import admin
from .models import (
    JapaneseWorkTag, JapaneseWorkTagType, # JapaneseWorkTagType 임포트
    KoreanPersonTag, KoreanVideoTag, KoreanVideoTheme
)

# JapaneseWorkTagType 모델을 위한 Admin 클래스 추가
@admin.register(JapaneseWorkTagType)
class JapaneseWorkTagTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(JapaneseWorkTag)
class JapaneseWorkTagAdmin(admin.ModelAdmin):
    # list_display와 search_fields에 'description' 추가
    list_display = ('name', 'pumbeon', 'type', 'description', 'image_preview')
    search_fields = ('name', 'pumbeon', 'type__name', 'description')
    list_filter = ('type',)
    autocomplete_fields = ('type',)

    def image_preview(self, obj):
        if obj.image:
            from django.utils.html import format_html
            return format_html('<img src="{}" width="100" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image Preview'

@admin.register(KoreanPersonTag)
class KoreanPersonTagAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(KoreanVideoTag)
class KoreanVideoTagAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(KoreanVideoTheme)
class KoreanVideoThemeAdmin(admin.ModelAdmin):
    search_fields = ('name',)