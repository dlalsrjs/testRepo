# videos/management/commands/fill_missing_thumbnails.py

import sys
from django.core.management.base import BaseCommand
from django.db.models import Q
from videos.models import JapaneseWork, KoreanVideo
from epalist.utils import get_youtube_thumbnail_url, get_tiktok_thumbnail_url, download_image_to_model_field

class Command(BaseCommand):
    help = '썸네일이 없거나, 이미지 파일이 실제로 존재하지 않는 경우 썸네일을 다시 채웁니다.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('===== 썸네일 검사 및 채우기 시작 (최종 버전) ====='))

        self.fill_for_model(JapaneseWork, "작품")
        self.fill_for_model(KoreanVideo, "영상")

        self.stdout.write(self.style.SUCCESS('===== 모든 작업 완료 ====='))

    def fill_for_model(self, model, model_name):
        """
        주어진 모델의 모든 항목을 검사하여 썸네일이 필요한 경우 채웁니다.
        """
        all_items = model.objects.all()
        total_count = all_items.count()
        
        self.stdout.write(f"\n▶ 전체 {model_name} 데이터 {total_count}개 검사 시작...")
        
        items_to_process = []
        for item in all_items:
            # [핵심 로직] 이미지 필드가 비어있거나, 필드에 값은 있지만 실제 파일이 없는 경우를 확인
            if not item.image or not item.image.storage.exists(item.image.name):
                items_to_process.append(item)

        if not items_to_process:
            self.stdout.write(self.style.SUCCESS(f"  └ 모든 {model_name} 데이터에 유효한 썸네일이 존재합니다."))
            return

        self.stdout.write(self.style.WARNING(f"▶ 총 {len(items_to_process)}개의 {model_name} 데이터에 썸네일 재생성이 필요합니다. 처리 시작..."))
        
        success_count = 0
        fail_count = 0

        for item in items_to_process:
            # URL 목록이 비어있는 경우를 안전하게 처리
            if not item.urls or not item.urls[0]:
                continue
            
            url = item.urls[0]
            thumbnail_url = None
            file_prefix = ""
            crop_needed = False

            if 'youtube.com' in url or 'youtu.be' in url:
                thumbnail_url = get_youtube_thumbnail_url(url)
                file_prefix = f"youtube_{model_name}_thumbnail"
                crop_needed = True
            elif 'tiktok.com' in url:
                thumbnail_url = get_tiktok_thumbnail_url(url)
                file_prefix = f"tiktok_{model_name}_thumbnail"
                crop_needed = False
            else:
                continue

            if thumbnail_url:
                try:
                    # 다운로드 전에 기존 이미지 파일을 삭제하여 덮어쓰기 문제를 방지합니다.
                    if item.image:
                        item.image.delete(save=False)

                    downloaded = download_image_to_model_field(
                        thumbnail_url, item, 'image',
                        file_name_prefix=file_prefix, crop=crop_needed
                    )
                    if downloaded:
                        item.save(update_fields=['image'])
                        self.stdout.write(self.style.SUCCESS(f"  - 성공: ID {item.pk}"))
                        success_count += 1
                    else:
                        self.stdout.write(self.style.WARNING(f"  - 다운로드 실패: ID {item.pk} (URL: {thumbnail_url})"))
                        fail_count += 1
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"  - 오류 발생: ID {item.pk}, 오류: {e}"))
                    fail_count += 1
        
        self.stdout.write(f"\n▶ {model_name} 처리 완료 (성공: {success_count}개, 실패: {fail_count}개)")
