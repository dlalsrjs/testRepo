# videos/models.py

from django.db import models
from django.contrib.postgres.fields import ArrayField
from persons.models import JapaneseActor, KoreanPerson
from core.models import JapaneseWorkTag, KoreanVideoTheme, KoreanVideoTag
import uuid

# 새로 만든 유틸리티 함수 임포트
from epalist.utils import get_youtube_thumbnail_url, download_image_to_model_field


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

    # save 메서드 오버라이드
    def save(self, *args, **kwargs):
        # 이미지가 없고, URLs가 존재하며 첫 번째 URL이 유튜브 영상일 경우
        if not self.image and self.urls and self.urls[0]:
            youtube_thumbnail_url = get_youtube_thumbnail_url(self.urls[0])
            if youtube_thumbnail_url:
                # 썸네일 다운로드 시도
                # save()가 호출될 때 self.pk는 이미 있을 수 있으므로 (업데이트 시)
                # download_image_to_model_field 내에서 save()가 호출되도록 하면
                # 여기서는 별도로 self.pk 존재 여부를 신경 쓸 필요가 없습니다.
                # 단, download_image_to_model_field에서 save()가 호출되어야 함.
                # (download_image_to_model_field는 ImageField.save()를 호출하므로 괜찮음)
                downloaded = download_image_to_model_field(youtube_thumbnail_url, self, 'image', file_name_prefix="youtube_work_thumbnail")
                if downloaded:
                    # 썸네일이 성공적으로 할당되었으므로,
                    # 아래의 super().save()에서 변경사항이 DB에 반영됩니다.
                    pass

        super().save(*args, **kwargs) # 최종 저장

class KoreanVideo(models.Model):
    urls = ArrayField(models.URLField(), verbose_name="URLs") # null=False로 필수 필드
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

    # save 메서드 오버라이드
    def save(self, *args, **kwargs):
        # 이미지가 없고, URLs가 존재하며 첫 번째 URL이 유튜브 영상일 경우
        if not self.image and self.urls and self.urls[0]:
            youtube_thumbnail_url = get_youtube_thumbnail_url(self.urls[0])
            if youtube_thumbnail_url:
                downloaded = download_image_to_model_field(youtube_thumbnail_url, self, 'image', file_name_prefix="youtube_video_thumbnail")
                if downloaded:
                    pass

        super().save(*args, **kwargs) # 최종 저장

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