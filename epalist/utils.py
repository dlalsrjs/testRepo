# epalist/epalist/utils.py
import re
import requests
import os
from django.core.files import File
import tempfile
from PIL import Image, ImageChops

def get_tiktok_thumbnail_url(video_url):
    """
    TikTok 동영상 URL에서 썸네일 이미지 URL을 추출합니다.
    TikTok은 oEmbed API를 사용하여 썸네일 정보를 제공합니다.
    """
    if not video_url or 'tiktok.com' not in video_url:
        return None

    try:
        # TikTok oEmbed API 엔드포인트
        oembed_url = f"https://www.tiktok.com/oembed?url={video_url}"
        response = requests.get(oembed_url)
        response.raise_for_status()  # HTTP 오류가 발생하면 예외를 발생시킴
        data = response.json()
        return data.get('thumbnail_url')
    except requests.exceptions.RequestException as e:
        print(f"TikTok oEmbed API 호출 실패: {e}")
        return None

def get_youtube_thumbnail_url(video_url):
    """
    유튜브 영상 또는 쇼츠 URL에서 썸네일 이미지 URL을 추출합니다.
    """
    if not video_url:
        return None
    
    # 문자열 앞에 r을 붙여서 raw string으로 만듭니다.
    youtube_regex = r'(?:https?://)?(?:www\.)?(?:youtube\.com|youtu\.be|youtube-nocookie\.com)/(?:watch\?v=|embed/|v/|shorts/|)([a-zA-Z0-9_-]{11})(?:.*)?'
    
    match = re.match(youtube_regex, video_url)

    if match:
        video_id = match.group(1)
        # 항상 고화질 썸네일을 요청합니다.
        return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
    return None

def crop_image(image):
    """
    Pillow 이미지를 받아 상하좌우의 검은 여백을 잘라냅니다.
    """
    bg = Image.new(image.mode, image.size, image.getpixel((0, 0)))
    diff = ImageChops.difference(image, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return image.crop(bbox)
    return image # 여백이 없는 경우 원본 반환

def download_image_to_model_field(image_url, model_instance, field_name, file_name_prefix="thumbnail", crop=False):
    if not image_url:
        return False

    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()

        # Pillow를 사용하여 이미지 열기
        img = Image.open(response.raw)

        if crop:
            img = crop_image(img)

        # 임시 파일에 이미지 저장
        temp_img_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        img.convert('RGB').save(temp_img_file, format='JPEG')
        temp_img_file.flush()

        image_file = File(open(temp_img_file.name, 'rb'))
        ext = '.jpg'

        try:
            field = getattr(model_instance, field_name)
            # 파일 이름에 pk가 없을 경우를 대비하여 uuid 또는 다른 고유값을 사용하도록 처리
            pk_or_uuid = getattr(model_instance, 'pk', getattr(model_instance, 'uuid', None))
            field.save(f"{file_name_prefix}_{pk_or_uuid}{ext}", image_file, save=False)
            return True
        finally:
            image_file.close()
            temp_img_file.close()
            os.unlink(temp_img_file.name)

    except requests.exceptions.RequestException as e:
        print(f"이미지 다운로드 실패: {e}")
        # maxresdefault.jpg가 없는 경우 hqdefault.jpg로 재시도
        if 'maxresdefault' in image_url:
            hq_url = image_url.replace('maxresdefault', 'hqdefault')
            print("고화질 썸네일 다운로드 실패, 표준 화질로 재시도합니다.")
            return download_image_to_model_field(hq_url, model_instance, field_name, file_name_prefix, crop)
        return False
    except Exception as e:
        print(f"이미지 저장 중 오류 발생: {e}")
        return False