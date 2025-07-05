# epalist/core/forms.py
from django import forms
from .models import JapaneseWorkTag, KoreanPersonTag, KoreanVideoTheme, KoreanVideoTag

# 각 태그 모델에 대한 폼을 정의합니다.

class JapaneseWorkTagForm(forms.ModelForm):
    class Meta:
        model = JapaneseWorkTag
        # fields에 'description' 추가
        fields = ['name', 'pumbeon', 'type', 'description', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'pumbeon': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            # description 필드에 Textarea 위젯 적용
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class KoreanPersonTagForm(forms.ModelForm):
    class Meta:
        model = KoreanPersonTag
        fields = ['name', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class KoreanVideoThemeForm(forms.ModelForm):
    class Meta:
        model = KoreanVideoTheme
        fields = ['name', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class KoreanVideoTagForm(forms.ModelForm):
    class Meta:
        model = KoreanVideoTag
        fields = ['name', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }