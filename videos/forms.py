# videos/forms.py
from django import forms
from .models import JapaneseWork, KoreanVideo
# ManyToManyField에 연결될 모델들을 여기서 임포트할 필요가 없습니다. (queryset이 필요 없으므로)
# from persons.models import JapaneseActor, KoreanPerson
# from epalist.core.models import JapaneseWorkTag, KoreanVideoTheme, KoreanVideoTag

class JapaneseWorkForm(forms.ModelForm):
    urls = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '쉼표로 구분하여 URL 입력 (선택 사항)'}),
        required=False
    )
    
    # !!! 아래 ModelMultipleChoiceField 명시적 정의를 모두 제거합니다 !!!
    # actors = forms.ModelMultipleChoiceField(
    #     queryset=JapaneseActor.objects.all().order_by('name'),
    #     required=False
    # )
    # tags = forms.ModelMultipleChoiceField(
    #     queryset=JapaneseWorkTag.objects.all().order_by('name'),
    #     required=False
    # )

    class Meta:
        model = JapaneseWork
        fields = ['product_number', 'urls', 'actors', 'tags', 'release_year', 'rating', 'work_hardness', 'image']
        widgets = {
            'product_number': forms.TextInput(attrs={'class': 'form-control'}),
            'release_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '예: 2020'}),
            'rating': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'work_hardness': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5, 'placeholder': '1~5 사이 숫자'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            # 'actors', 'tags'는 위에서 명시적으로 정의한 필드가 없으므로 widgets에도 포함하지 않습니다.
            # Django가 ModelAdmin의 autocomplete_fields를 통해 위젯을 처리할 것입니다.
        }
    
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