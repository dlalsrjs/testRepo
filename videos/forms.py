# videos/forms.py
from django import forms
from .models import JapaneseWork, KoreanVideo, LocalVideo
# ManyToManyField에 연결될 모델들을 여기서 임포트할 필요가 없습니다. (queryset이 필요 없으므로)
from persons.models import JapaneseActor
from core.models import JapaneseWorkTag

class JapaneseWorkForm(forms.ModelForm):
    urls = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '쉼표로 구분하여 URL 입력 (선택 사항)'}),
        required=False
    )
    # 배우와 태그를 텍스트로 입력받을 필드 추가
    actors_str = forms.CharField(
        label="출연 배우 (쉼표로 구분)",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    tags_str = forms.CharField(
        label="태그 (쉼표로 구분)",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = JapaneseWork
        # 기존 fields에서 'actors', 'tags'를 제외하고 새로운 필드 추가
        fields = ['product_number', 'urls', 'actors_str', 'tags_str', 'release_year', 'rating', 'work_hardness', 'image']
        widgets = {
            'product_number': forms.TextInput(attrs={'class': 'form-control'}),
            'release_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '예: 2020'}),
            'rating': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'work_hardness': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5, 'placeholder': '1~5 사이 숫자'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 폼이 인스턴스를 가질 때, 기존 배우와 태그 목록을 쉼표로 연결하여 보여줌
        if self.instance and self.instance.pk:
            self.fields['actors_str'].initial = ','.join([actor.name for actor in self.instance.actors.all()])
            self.fields['tags_str'].initial = ','.join([tag.name for tag in self.instance.tags.all()])

    def clean_urls(self):
        data = self.cleaned_data['urls']
        if not data:
            return None

        if isinstance(data, str):
            urls_list = [url.strip() for url in data.split(',') if url.strip()]
        elif isinstance(data, list):
            urls_list = [url.strip() for url in data if url.strip()]
        else:
            raise forms.ValidationError("올바른 URL 형식으로 입력해주세요. (쉼표로 구분)")

        if not urls_list:
            return None

        for url_item in urls_list:
            existing_works = JapaneseWork.objects.filter(urls__contains=[url_item])
            if self.instance and self.instance.pk:
                existing_works = existing_works.exclude(pk=self.instance.pk)
            
            if existing_works.exists():
                raise forms.ValidationError(f"'{url_item}' URL은 이미 다른 작품에 존재합니다.")
        
        return urls_list

    def save(self, commit=True):
        instance = super().save(commit=False)

        # commit=True일 때만 저장 로직 실행
        if commit:
            instance.save()

            # actors_str 필드의 텍스트를 파싱하여 배우(actor) 객체 연결
            actor_names = [name.strip() for name in self.cleaned_data.get('actors_str', '').split(',') if name.strip()]
            instance.actors.clear()
            for name in actor_names:
                actor, created = JapaneseActor.objects.get_or_create(name=name)
                instance.actors.add(actor)
            
            # tags_str 필드의 텍스트를 파싱하여 태그(tag) 객체 연결
            tag_names = [name.strip() for name in self.cleaned_data.get('tags_str', '').split(',') if name.strip()]
            instance.tags.clear()
            for name in tag_names:
                tag, created = JapaneseWorkTag.objects.get_or_create(name=name)
                instance.tags.add(tag)
        
        return instance

class KoreanVideoForm(forms.ModelForm):
    urls = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '쉼표로 구분하여 URL 입력 (필수)'}),
        required=True
    )
    
    # !!! 아래 ModelMultipleChoiceField 명시적 정의를 모두 제거합니다 !!!
    # persons = forms.ModelMultipleChoiceField(
    #     queryset=KoreanPerson.objects.all().order_by('name'),
    #     required=False
    # )
    # themes = forms.ModelMultipleChoiceField(
    #     queryset=KoreanVideoTheme.objects.all().order_by('name'),
    #     required=False
    # )
    # tags = forms.ModelMultipleChoiceField(
    #     queryset=KoreanVideoTag.objects.all().order_by('name'),
    #     required=False
    # )

    class Meta:
        model = KoreanVideo
        fields = ['urls', 'persons', 'themes', 'tags', 'date', 'description', 'image', 'edited']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'edited': forms.CheckboxInput(attrs={'class': 'form-check-input'})
            # 'persons', 'themes', 'tags'는 위에서 명시적으로 정의한 필드가 없으므로 widgets에도 포함하지 않습니다.
        }

    def clean_urls(self):
        data = self.cleaned_data['urls']
        if not data:
            raise forms.ValidationError("URL은 필수 항목입니다.")

        if isinstance(data, str):
            urls_list = [url.strip() for url in data.split(',') if url.strip()]
        elif isinstance(data, list):
            urls_list = [url.strip() for url in data if url.strip()]
        else:
            raise forms.ValidationError("올바른 URL 형식으로 입력해주세요. (쉼표로 구분)")

        if not urls_list:
            raise forms.ValidationError("URL은 필수 항목입니다.")

        for url_item in urls_list:
            existing_videos = KoreanVideo.objects.filter(urls__contains=[url_item])
            if self.instance and self.instance.pk:
                existing_videos = existing_videos.exclude(pk=self.instance.pk)
            
            if existing_videos.exists():
                raise forms.ValidationError(f"'{url_item}' URL은 이미 다른 영상에 존재합니다.")
        
        return urls_list
    
class LocalVideoForm(forms.ModelForm):
    class Meta:
        model = LocalVideo
        fields = ['persons', 'description', 'image']
        widgets = {
            'persons': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }