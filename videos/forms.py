# videos/forms.py
from django import forms
# ManyToManyField에 연결될 모델들을 여기서 임포트할 필요가 없습니다. (queryset이 필요 없으므로)
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from .models import JapaneseWork, KoreanVideo, LocalVideo
from persons.models import JapaneseActor, KoreanPerson
from core.models import JapaneseWorkTag, KoreanVideoTheme, KoreanVideoTag

class JapaneseWorkForm(forms.ModelForm):
    actors_str = forms.CharField(label="출연 배우 (쉼표로 구분)", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    tags_str = forms.CharField(label="태그 (쉼표로 구분)", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    urls = forms.CharField(label="URL (쉼표로 구분)", widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)

    class Meta:
        model = JapaneseWork
        # ✨✨✨ 핵심 수정사항 1: fields 리스트에서 'urls'를 제거합니다. ✨✨✨
        fields = ['product_number', 'release_year', 'rating', 'work_hardness', 'image', 'actors_str', 'tags_str']
        widgets = {
            'product_number': forms.TextInput(attrs={'class': 'form-control'}),
            'release_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'rating': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'work_hardness': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    # (이하 __init__, clean_urls, save 메소드는 이전과 동일하게 유지합니다)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['actors_str'].initial = ', '.join(a.name for a in self.instance.actors.all())
            self.fields['tags_str'].initial = ', '.join(t.name for t in self.instance.tags.all())
            if self.instance.urls:
                self.fields['urls'].initial = ', '.join(self.instance.urls)

    def clean_urls(self):
        data = self.cleaned_data.get('urls', '')
        if not data: return []
        urls_list = [url.strip() for url in data.split(',') if url.strip()]
        validate = URLValidator()
        for url in urls_list:
            try: validate(url)
            except ValidationError: raise forms.ValidationError(f"'{url}'은(는) 유효한 URL 형식이 아닙니다.")
        return urls_list

    def save(self, commit=True):
        instance = super().save(commit=False)
        # ModelForm이 더 이상 처리하지 않으므로, 우리가 직접 urls 데이터를 저장합니다.
        instance.urls = self.cleaned_data.get('urls', [])
        if commit:
            instance.save()
            actor_names = [name.strip() for name in self.cleaned_data.get('actors_str', '').split(',') if name.strip()]
            instance.actors.clear()
            for name in actor_names:
                actor, _ = JapaneseActor.objects.get_or_create(name=name)
                instance.actors.add(actor)
            tag_names = [name.strip() for name in self.cleaned_data.get('tags_str', '').split(',') if name.strip()]
            instance.tags.clear()
            for name in tag_names:
                tag, _ = JapaneseWorkTag.objects.get_or_create(name=name)
                instance.tags.add(tag)
        return instance


class KoreanVideoForm(forms.ModelForm):
    urls = forms.CharField(label="URL (쉼표로 구분)", widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)
    persons_str = forms.CharField(label="인물 (쉼표로 구분)", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    themes_str = forms.CharField(label="주제 (쉼표로 구분)", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    tags_str = forms.CharField(label="태그 (쉼표로 구분)", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = KoreanVideo
        # ✨✨✨ 핵심 수정사항 2: fields 리스트에서 'urls'를 제거합니다. ✨✨✨
        fields = ['description', 'date', 'image', 'edited', 'persons_str', 'themes_str', 'tags_str']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'edited': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    # (이하 __init__, clean_urls, save 메소드는 이전과 동일하게 유지합니다)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['persons_str'].initial = ', '.join(p.name for p in self.instance.persons.all())
            self.fields['themes_str'].initial = ', '.join(t.name for t in self.instance.themes.all())
            self.fields['tags_str'].initial = ', '.join(t.name for t in self.instance.tags.all())
            if self.instance.urls:
                self.fields['urls'].initial = ', '.join(self.instance.urls)

    def clean_urls(self):
        data = self.cleaned_data.get('urls', '')
        if not data: raise forms.ValidationError("URL은 필수 항목입니다.")
        urls_list = [url.strip() for url in data.split(',') if url.strip()]
        if not urls_list: raise forms.ValidationError("URL은 필수 항목입니다.")
        validate = URLValidator()
        for url in urls_list:
            try: validate(url)
            except ValidationError: raise forms.ValidationError(f"'{url}'은(는) 유효한 URL 형식이 아닙니다.")
        return urls_list

    def save(self, commit=True):
        instance = super().save(commit=False)
        # ModelForm이 더 이상 처리하지 않으므로, 우리가 직접 urls 데이터를 저장합니다.
        instance.urls = self.cleaned_data.get('urls', [])
        if commit:
            instance.save()
            person_names = [name.strip() for name in self.cleaned_data.get('persons_str', '').split(',') if name.strip()]
            instance.persons.clear()
            for name in person_names:
                person, _ = KoreanPerson.objects.get_or_create(name=name)
                instance.persons.add(person)
            theme_names = [name.strip() for name in self.cleaned_data.get('themes_str', '').split(',') if name.strip()]
            instance.themes.clear()
            for name in theme_names:
                theme, _ = KoreanVideoTheme.objects.get_or_create(name=name)
                instance.themes.add(theme)
            tag_names = [name.strip() for name in self.cleaned_data.get('tags_str', '').split(',') if name.strip()]
            instance.tags.clear()
            for name in tag_names:
                tag, _ = KoreanVideoTag.objects.get_or_create(name=name)
                instance.tags.add(tag)
        return instance
    
class LocalVideoForm(forms.ModelForm):
    class Meta:
        model = LocalVideo
        fields = ['persons', 'description', 'image']
        widgets = {
            'persons': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }