# persons/admin.py

from django.contrib import admin
from .models import JapaneseActor, KoreanPerson

@admin.register(JapaneseActor)
class JapaneseActorAdmin(admin.ModelAdmin):
    list_display = ('name', 'birth_year', 'debut_year', 'looks', 'hardness')
    # 검색 필드에 'birth_year' 추가
    search_fields = ('name', 'other_names', 'birth_year')
    list_filter = ('looks', 'hardness')

@admin.register(KoreanPerson)
class KoreanPersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'birth_year', 'looks', 'other_names_display')
    # 태그 이름으로도 검색할 수 있도록 'tags__name' 추가
    search_fields = ('name', 'description', 'looks', 'other_names', 'tags__name')
    list_filter = ('looks',)
    filter_horizontal = ('tags',)

    def other_names_display(self, obj):
        return ", ".join(obj.other_names) if obj.other_names else '-'
    other_names_display.short_description = '다른 이름'