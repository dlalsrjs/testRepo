from django import forms
from .models import JapanesePhoto, KoreanPhoto, JapanesePhotoImage, KoreanPhotoImage
from persons.models import JapaneseActor, KoreanPerson
from core.models import JapanesePhotoTag, KoreanPhotoTag

class JapanesePhotoForm(forms.ModelForm):
    actors_str = forms.CharField(label="출연 배우 (쉼표로 구분)", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    tags_str = forms.CharField(label="태그 (쉼표로 구분)", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    # 여러 파일을 받기 위한 필드이지만, 위젯에서는 multiple을 제거합니다.
    # HTML 템플릿에서 input 태그에 직접 multiple 속성을 부여하여 처리합니다.
    new_images = forms.ImageField(label="새 이미지 추가", required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = JapanesePhoto
        fields = ['description', 'year', 'url', 'actors_str', 'tags_str']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['actors_str'].initial = ', '.join(a.name for a in self.instance.actors.all())
            self.fields['tags_str'].initial = ', '.join(t.name for t in self.instance.tags.all())

    def save_related_data(self, instance, files):
        # 배우 정보 저장
        actor_names = [name.strip() for name in self.cleaned_data.get('actors_str', '').split(',') if name.strip()]
        instance.actors.clear()
        for name in actor_names:
            actor, _ = JapaneseActor.objects.get_or_create(name=name)
            instance.actors.add(actor)

        # 태그 정보 저장
        tag_names = [name.strip() for name in self.cleaned_data.get('tags_str', '').split(',') if name.strip()]
        instance.tags.clear()
        for name in tag_names:
            tag, _ = JapanesePhotoTag.objects.get_or_create(name=name)
            instance.tags.add(tag)

        # 새 이미지 저장 (뷰에서 request.FILES.getlist('new_images')로 파일을 받아 전달)
        if files:
            for f in files:
                JapanesePhotoImage.objects.create(photo_set=instance, image=f)

class KoreanPhotoForm(forms.ModelForm):
    persons_str = forms.CharField(label="출연 인물 (쉼표로 구분)", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    tags_str = forms.CharField(label="태그 (쉼표로 구분)", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    # 여기도 동일하게 위젯에서 multiple 속성을 제거합니다.
    new_images = forms.ImageField(label="새 이미지 추가", required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = KoreanPhoto
        fields = ['description', 'year', 'url', 'persons_str', 'tags_str']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['persons_str'].initial = ', '.join(p.name for p in self.instance.persons.all())
            self.fields['tags_str'].initial = ', '.join(t.name for t in self.instance.tags.all())

    def save_related_data(self, instance, files):
        # 인물 정보 저장
        person_names = [name.strip() for name in self.cleaned_data.get('persons_str', '').split(',') if name.strip()]
        instance.persons.clear()
        for name in person_names:
            person, _ = KoreanPerson.objects.get_or_create(name=name)
            instance.persons.add(person)

        # 태그 정보 저장
        tag_names = [name.strip() for name in self.cleaned_data.get('tags_str', '').split(',') if name.strip()]
        instance.tags.clear()
        for name in tag_names:
            tag, _ = KoreanPhotoTag.objects.get_or_create(name=name)
            instance.tags.add(tag)

        # 새 이미지 저장 (뷰에서 request.FILES.getlist('new_images')로 파일을 받아 전달)
        if files:
            for f in files:
                KoreanPhotoImage.objects.create(photo_set=instance, image=f)