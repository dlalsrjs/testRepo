from django.db import models
from django.contrib.postgres.fields import ArrayField
from persons.models import JapaneseActor, KoreanPerson
from core.models import JapanesePhotoTag, KoreanPhotoTag

class JapanesePhoto(models.Model):
    description = models.TextField(null=True, blank=True, verbose_name="설명")
    actors = models.ManyToManyField(JapaneseActor, blank=True, verbose_name="출연 배우")
    year = models.IntegerField(null=True, blank=True, verbose_name="당시 연도")
    tags = models.ManyToManyField(JapanesePhotoTag, blank=True, verbose_name="태그")
    url = models.URLField(null=True, blank=True, verbose_name="URL")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "일본 사진"
        verbose_name_plural = "일본 사진들"
        ordering = ['-year', '-created_at']

    def __str__(self):
        return f"일본 사진첩 (ID: {self.pk})"

class JapanesePhotoImage(models.Model):
    photo_set = models.ForeignKey(JapanesePhoto, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='photos/japanese/')

    def __str__(self):
        return f"{self.photo_set_id}의 이미지"

class KoreanPhoto(models.Model):
    description = models.TextField(null=True, blank=True, verbose_name="설명")
    persons = models.ManyToManyField(KoreanPerson, blank=True, verbose_name="출연 인물")
    year = models.IntegerField(null=True, blank=True, verbose_name="당시 연도")
    tags = models.ManyToManyField(KoreanPhotoTag, blank=True, verbose_name="태그")
    url = models.URLField(null=True, blank=True, verbose_name="URL")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "한국 사진"
        verbose_name_plural = "한국 사진들"
        ordering = ['-year', '-created_at']

    def __str__(self):
        return f"한국 사진첩 (ID: {self.pk})"

class KoreanPhotoImage(models.Model):
    photo_set = models.ForeignKey(KoreanPhoto, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='photos/korean/')

    def __str__(self):
        return f"{self.photo_set_id}의 이미지"