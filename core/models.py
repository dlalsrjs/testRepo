from django.db import models

class JapaneseWorkTagType(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="유형명")

    class Meta:
        verbose_name = "일본 작품 태그 유형"
        verbose_name_plural = "일본 작품 태그 유형들"

    def __str__(self):
        return self.name
    
class JapaneseWorkTag(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="태그명")
    pumbeon = models.CharField(max_length=100, null=True, blank=True, verbose_name="품번")
    image = models.ImageField(upload_to='tags/japanese_work_tags/', null=True, blank=True, verbose_name="이미지")
    type = models.ForeignKey(
        JapaneseWorkTagType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="유형"
    )
    # '설명' 필드 추가
    description = models.TextField(null=True, blank=True, verbose_name="설명")

    class Meta:
        verbose_name = "일본 작품 태그"
        verbose_name_plural = "일본 작품 태그들"

    def __str__(self):
        return self.name

class KoreanPersonTag(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="태그명")
    image = models.ImageField(upload_to='tags/korean_person_tags/', null=True, blank=True, verbose_name="이미지")

    class Meta:
        verbose_name = "한국 인물 태그"
        verbose_name_plural = "한국 인물 태그들"

    def __str__(self):
        return self.name

class KoreanVideoTheme(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="태그명")
    image = models.ImageField(upload_to='tags/korean_video_themes/', null=True, blank=True, verbose_name="이미지")

    class Meta:
        verbose_name = "한국 영상 주제"
        verbose_name_plural = "한국 영상 주제들"

    def __str__(self):
        return self.name

class KoreanVideoTag(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="태그명")
    image = models.ImageField(upload_to='tags/korean_video_tags/', null=True, blank=True, verbose_name="이미지")

    class Meta:
        verbose_name = "한국 영상 태그"
        verbose_name_plural = "한국 영상 태그들"

    def __str__(self):
        return self.name