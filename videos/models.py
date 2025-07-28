# videos/models.py

from django.db import models
from django.contrib.postgres.fields import ArrayField
from persons.models import JapaneseActor, KoreanPerson
from core.models import JapaneseWorkTag, KoreanVideoTheme, KoreanVideoTag
import uuid

from epalist.utils import get_youtube_thumbnail_url, get_tiktok_thumbnail_url, download_image_to_model_field


class JapaneseWork(models.Model):
    product_number = models.CharField(max_length=100, unique=True, verbose_name="품번")
    urls = ArrayField(models.URLField(), null=True, blank=True, verbose_name="URLs")
    actors = models.ManyToManyField(JapaneseActor, blank=True, verbose_name="출연 배우 목록")
    tags = models.ManyToManyField(JapaneseWorkTag, blank=True, verbose_name="태그 목록")
    release_year = models.IntegerField(null=True, blank=True, verbose_name="출시연도")
    rating = models.TextField(null=True, blank=True, verbose_name="평가")
    work_hardness = models.IntegerField(null=True, blank=True, verbose_name="작품 하드함") # 1~5 범위 숫자
    image = models.ImageField(upload_to='works/japanese_works/', null=True, blank=True, verbose_name="이미지")

    class Meta:
        verbose_name = "일본 작품"
        verbose_name_plural = "일본 작품들"

    def __str__(self):
        return self.product_number
    
    def save(self, *args, **kwargs):
        is_new = self._state.adding
        if is_new:
            super().save(*args, **kwargs)

        if not self.image and self.urls and self.urls[0]:
            url = self.urls[0]
            thumbnail_url = None
            crop_needed = False
            
            # [최종 수정] 어떤 형태의 유튜브 주소든 인식하도록 조건문 개선
            if 'youtube.com' in url or 'youtu.be' in url:
                thumbnail_url = get_youtube_thumbnail_url(url)
                file_prefix = "youtube_work_thumbnail"
                crop_needed = True
            elif 'tiktok.com' in url:
                thumbnail_url = get_tiktok_thumbnail_url(url)
                file_prefix = "tiktok_work_thumbnail"

            if thumbnail_url:
                downloaded = download_image_to_model_field(
                    thumbnail_url, self, 'image',
                    file_name_prefix=file_prefix, crop=crop_needed
                )
                if downloaded:
                    super().save(force_update=True)
                    return
        if not is_new:
            super().save(*args, **kwargs)


class KoreanVideo(models.Model):
    urls = ArrayField(models.URLField(), verbose_name="URLs")
    persons = models.ManyToManyField(KoreanPerson, blank=True, verbose_name="출연 인물 목록")
    themes = models.ManyToManyField(KoreanVideoTheme, blank=True, verbose_name="주제")
    tags = models.ManyToManyField(KoreanVideoTag, blank=True, verbose_name="태그 목록")
    date = models.DateField(null=True, blank=True, verbose_name="당시 날짜")
    description = models.TextField(null=True, blank=True, verbose_name="설명")
    image = models.ImageField(upload_to='videos/korean_videos/', null=True, blank=True, verbose_name="이미지")
    edited = models.BooleanField(default=False, verbose_name="편집 여부")
    
    class Meta:
        verbose_name = "한국 영상"
        verbose_name_plural = "한국 영상들"

    def __str__(self):
        if self.urls:
            return f"한국 영상: {self.urls[0]}..."
        return f"한국 영상: {self.id}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        if is_new:
            super().save(*args, **kwargs)

        if not self.image and self.urls and self.urls[0]:
            url = self.urls[0]
            thumbnail_url = None
            crop_needed = False

            # [최종 수정] 어떤 형태의 유튜브 주소든 인식하도록 조건문 개선
            if 'youtube.com' in url or 'youtu.be' in url:
                thumbnail_url = get_youtube_thumbnail_url(url)
                file_prefix = "youtube_video_thumbnail"
                crop_needed = True
            elif 'tiktok.com' in url:
                thumbnail_url = get_tiktok_thumbnail_url(url)
                file_prefix = "tiktok_video_thumbnail"

            if thumbnail_url:
                downloaded = download_image_to_model_field(
                    thumbnail_url, self, 'image',
                    file_name_prefix=file_prefix, crop=crop_needed
                )
                if downloaded:
                    super().save(force_update=True)
                    return
        if not is_new:
            super().save(*args, **kwargs)


class LocalVideo(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="UUID")
    persons = models.ManyToManyField('persons.KoreanPerson', blank=True, verbose_name="인물 목록")
    description = models.TextField(null=True, blank=True, verbose_name="설명")
    image = models.ImageField(upload_to='local_videos/', null=True, blank=True, verbose_name="이미지")

    class Meta:
        verbose_name = "로컬 영상"
        verbose_name_plural = "로컬 영상들"
        ordering = ['-uuid']

    def __str__(self):
        return str(self.uuid)