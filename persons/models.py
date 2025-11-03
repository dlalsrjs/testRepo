from django.db import models
from django.contrib.postgres.fields import ArrayField # 텍스트 리스트를 위해
from core.models import KoreanPersonTag # 한국 인물 태그 불러오기

class JapaneseActor(models.Model):
    name = models.CharField(max_length=100, verbose_name="이름")
    other_names = ArrayField(models.CharField(max_length=200), null=True, blank=True, verbose_name="다른 이름")
    birth_year = models.IntegerField(null=True, blank=True, verbose_name="출생연도")
    debut_year = models.IntegerField(null=True, blank=True, verbose_name="데뷔연도")
    # 외모는 3글자 이내의 알파벳이므로 CharField에 max_length와 유효성 검사 추가 (나중에 Forms에서)
    looks = models.CharField(max_length=3, null=True, blank=True, verbose_name="외모")
    # 하드함은 1~5 범위의 숫자이므로 IntegerField에 유효성 검사 추가 (나중에 Forms에서)
    hardness = models.IntegerField(null=True, blank=True, verbose_name="하드함")
    description = models.TextField(null=True, blank=True, verbose_name="설명")
    image = models.ImageField(upload_to='actors/japanese_actors/', null=True, blank=True, verbose_name="이미지")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        verbose_name = "일본 배우"
        verbose_name_plural = "일본 배우들"

    def __str__(self):
        if self.birth_year:
            return f"{self.name} ({self.birth_year})"
        return self.name

class KoreanPerson(models.Model):
    name = models.CharField(max_length=100, verbose_name="이름")
    other_names = ArrayField(models.CharField(max_length=100), blank=True, null=True, verbose_name="다른 이름")
    birth_year = models.IntegerField(null=True, blank=True, verbose_name="출생 연도")
    image = models.ImageField(upload_to='persons/korean_persons/', null=True, blank=True, verbose_name="이미지")
    description = models.TextField(null=True, blank=True, verbose_name="설명")
    looks = models.CharField(max_length=10, null=True, blank=True, verbose_name="외모")
    tags = models.ManyToManyField('core.KoreanPersonTag', blank=True, verbose_name="태그")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        verbose_name = "한국 인물"
        verbose_name_plural = "한국 인물들"
        ordering = ['name']

    def __str__(self):
        # N+1 문제를 방지하기 위해 prefetch_related가 사용될 때 효율적으로 작동
        if hasattr(self, '_prefetched_objects_cache') and 'tags' in self._prefetched_objects_cache:
            tags = ", ".join([tag.name for tag in self.tags.all()])
        else:
            # prefetch되지 않은 경우, 필요 시 DB 쿼리 실행
            tags = ", ".join([tag.name for tag in self.tags.all()])

        if tags:
            return f"{self.name} [{tags}]"
        return self.name