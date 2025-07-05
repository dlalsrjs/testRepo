# videos/management/commands/fill_missing_thumbnails.py
from django.core.management.base import BaseCommand, CommandError
from videos.models import JapaneseWork, KoreanVideo
from epalist.utils import get_youtube_thumbnail_url, download_image_to_model_field
from django.db.models import Q
from django.conf import settings # MEDIA_ROOT 경로를 가져오기 위해
import os # 파일 존재 여부 확인을 위해
import time

class Command(BaseCommand):
    help = 'URLs에 유튜브 링크가 있으나 이미지가 없거나 유효하지 않은 JapaneseWork 및 KoreanVideo 객체의 썸네일을 채웁니다.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('누락되거나 유효하지 않은 유튜브 썸네일 채우기 작업을 시작합니다...'))

        models_to_process = [
            (JapaneseWork, "일본 작품", "product_number", "youtube_work_thumbnail"),
            (KoreanVideo, "한국 영상", "pk", "youtube_video_thumbnail"),
        ]

        for Model, model_name, identifier_field, file_prefix in models_to_process:
            self.stdout.write(f'\n--- {model_name} 처리 시작 ---')
            
            # 모든 객체를 가져와서 개별적으로 이미지 유효성을 검사합니다.
            # image__isnull=True | image='' 로 1차 필터링하지만, 실제 파일 존재 여부도 확인해야 함.
            all_objects = Model.objects.all()
            total_checked_count = all_objects.count()
            self.stdout.write(f'총 {total_checked_count}개의 {model_name}을(를) 확인합니다.')
            
            filled_count = 0
            invalid_image_count = 0

            for obj in all_objects:
                identifier_value = getattr(obj, identifier_field)
                current_image_path = obj.image.path if obj.image else None
                image_exists_on_disk = False

                if current_image_path:
                    full_image_path = os.path.join(settings.MEDIA_ROOT, current_image_path.replace(settings.MEDIA_URL, '').lstrip('/'))
                    image_exists_on_disk = os.path.exists(full_image_path)
                
                # 조건: 이미지가 없거나 (DB에 NULL 또는 빈 문자열), DB에는 경로가 있으나 실제 파일이 존재하지 않는 경우
                is_image_missing_or_invalid = not obj.image or not obj.image.name or not image_exists_on_disk

                if is_image_missing_or_invalid:
                    invalid_image_count += 1
                    # 유효한 유튜브 URL이 있는지 확인
                    if obj.urls and obj.urls[0]:
                        youtube_thumbnail_url = get_youtube_thumbnail_url(obj.urls[0])
                        if youtube_thumbnail_url:
                            self.stdout.write(f'  - {model_name} {identifier_field}: {identifier_value}, URL: {obj.urls[0]}')
                            self.stdout.write(f'    현재 이미지 상태: {"없음" if not obj.image.name else "파일 없음"} (경로: {obj.image.name})')
                            self.stdout.write(f'    썸네일 다운로드 시도: {youtube_thumbnail_url}')
                            
                            try:
                                # 기존 이미지가 있다면 삭제
                                if obj.image and obj.image.name and image_exists_on_disk:
                                    obj.image.delete(save=False) # DB 필드는 삭제하지 않고 파일만 삭제
                                    self.stdout.write(f'    [정보] 기존 이미지 파일 "{obj.image.name}" 삭제 완료.')
                                
                                # ImageField를 다시 빈 상태로 설정하여 새로운 파일이 저장될 준비
                                obj.image = None # ImageField를 None으로 설정하여 초기화

                                downloaded = download_image_to_model_field(youtube_thumbnail_url, obj, 'image', file_name_prefix=file_prefix)
                                if downloaded:
                                    obj.refresh_from_db() # DB에서 객체 상태를 새로고침하여 최신 이미지 URL 반영
                                    self.stdout.write(self.style.SUCCESS(f'    [성공] 썸네일이 채워졌습니다. 새 이미지: {obj.image.url}'))
                                    filled_count += 1
                                else:
                                    self.stdout.write(self.style.WARNING(f'    [실패] 썸네일 다운로드에 실패했습니다. URL: {youtube_thumbnail_url}'))
                            except Exception as e:
                                self.stdout.write(self.style.ERROR(f'    [오류] 썸네일 저장 중 예외 발생: {e}'))
                            time.sleep(0.1) # 짧은 지연 (API 요청 제한 방지)
                        else:
                            self.stdout.write(f'  - {model_name} {identifier_field}: {identifier_value} (URLs에 유효한 유튜브 URL이 없습니다)')
                    else:
                        self.stdout.write(f'  - {model_name} {identifier_field}: {identifier_value} (URLs이 없거나 첫 번째 URL이 비어있습니다)')
                # else: # 이미지가 유효한 경우 (로그 출력 불필요)
                #     self.stdout.write(f'  - {model_name} {identifier_field}: {identifier_value} (이미지 유효함)')

            self.stdout.write(self.style.SUCCESS(f'{model_name} 썸네일 채우기 완료. 총 {invalid_image_count}개 확인, {filled_count}개 채워짐.'))
            self.stdout.write('') # 공백 줄

        self.stdout.write(self.style.SUCCESS('모든 작업이 완료되었습니다.'))