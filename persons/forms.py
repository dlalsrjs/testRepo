# persons/forms.py
from django import forms
from .models import JapaneseActor, KoreanPerson
# ManyToManyField에 연결될 모델 임포트
from core.models import KoreanPersonTag

class JapaneseActorForm(forms.ModelForm):
    class Meta:
        model = JapaneseActor
        fields = ['name', 'other_names', 'birth_year', 'debut_year', 'looks', 'hardness', 'description', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'other_names': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '쉼표로 구분하여 입력 (예: 이름1,이름2)'}),
            'birth_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '예: 1990'}),
            'debut_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '예: 2010'}),
            'looks': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '3글자 이내 알파벳 (예: SSS)'}),
            'hardness': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5, 'placeholder': '1~5 사이 숫자'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class KoreanPersonForm(forms.ModelForm):
    # 폼에서 다른 이름을 쉼표로 구분된 텍스트로 다루기 위해 CharField로 정의
    other_names_str = forms.CharField(
        label="다른 이름 (쉼표로 구분)",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = KoreanPerson
        fields = ['name', 'birth_year', 'looks', 'tags', 'description', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'looks': forms.TextInput(attrs={'class': 'form-control'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    # 폼 초기화 시, 리스트 형태의 other_names를 쉼표로 구분된 문자열로 변환
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.other_names:
            self.fields['other_names_str'].initial = ', '.join(self.instance.other_names)

    # 폼 저장 시, 쉼표로 구분된 문자열을 리스트로 변환하여 저장
    def save(self, commit=True):
        instance = super().save(commit=False)
        other_names_list = [name.strip() for name in self.cleaned_data['other_names_str'].split(',') if name.strip()]
        instance.other_names = other_names_list if other_names_list else None
        
        if commit:
            instance.save()
            self.save_m2m()
        return instance