# epalist/epalist/utils.py
import re
import requests
import os
from django.core.files import File
# from django.core.files.temp import NamedTemporaryFile
import tempfile

def get_youtube_thumbnail_url(video_url):
    """
    유튜브 영상 또는 쇼츠 URL에서 썸네일 이미지 URL을 추출합니다.
    """
    if not video_url:
        return None

    # 정규 표현식 수정: 비디오 ID를 명확하게 하나의 그룹으로 캡처
    # 가장 일반적인 youtube.com/watch?v=, youtu.be/, youtube.com/embed/, youtube.com/shorts/
    youtube_regex = (
        r'(?:https?://)?(?:www\.)?'  # Optional protocol and www.
        '(?:youtube\.com|youtu\.be|youtube-nocookie\.com)/' # Domain
        '(?:watch\?v=|embed/|v/|shorts/|)' # Optional path segments for video ID
        '([a-zA-Z0-9_-]{11})' # Group 1: This is the 11-character video ID
        '(?:.*)?' # Optional trailing characters (like playlist ID, etc.)
    )
    match = re.match(youtube_regex, video_url)

    if match:
        video_id = match.group(1) # <-- 이제 Group 1이 비디오 ID가 됩니다.
        # 고화질 썸네일 (maxresdefault)
        return f"http://img.youtube.com/vi/{video_id}/maxresdefault.jpg" # 썸네일 공식 도메인 재확인 및 변경
    return None

def convert_to_standard_youtube_url(video_url):
    """
    유튜브 쇼츠 URL을 표준 YouTube (watch?v=) URL로 변환합니다.
    """
    if not video_url:
        return None

    # 이 함수도 get_youtube_thumbnail_url과 동일한 비디오 ID 추출 로직 사용
    youtube_regex_for_conversion = (
        r'(?:https?://)?(?:www\.)?'
        '(?:youtube\.com|youtu\.be|youtube-nocookie\.com)/'
        '(?:watch\?v=|embed/|v/|shorts/|)'
        '([a-zA-Z0-9_-]{11})' # Group 1: video ID
        '(?:.*)?'
    )
    match_conv = re.match(youtube_regex_for_conversion, video_url)
    if match_conv:
        video_id_conv = match_conv.group(1) # <-- 이제 Group 1이 비디오 ID가 됩니다.
        return f"https://img.youtube.com/vi/3{video_id_conv}"
    
    return video_url

def download_image_to_model_field(image_url, model_instance, field_name, file_name_prefix="thumbnail"):
    if not image_url:
        return False

    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()

        content_type = response.headers.get('Content-Type', '')
        ext = '.jpg'
        if 'image/jpeg' in content_type:
            ext = '.jpg'
        elif 'image/png' in content_type:
            ext = '.png'
        elif 'image/gif' in content_type:
            ext = '.gif'
        elif 'image/webp' in content_type:
            ext = '.webp'
        elif 'image/avif' in content_type:
            ext = '.avif'
        else:
            url_path = image_url.split('?')[0]
            if '.' in url_path:
                ext = os.path.splitext(url_path)[1]

        # !!! 이 부분을 수정합니다: tempfile.NamedTemporaryFile 사용 !!!
        # NamedTemporaryFile의 'delete' 인자는 Django 버전에 따라 호환성 문제가 있을 수 있으므로
        # Python 표준 라이브러리의 tempfile을 사용하고 수동으로 파일을 삭제합니다.
        img_temp = tempfile.NamedTemporaryFile(delete=False) # delete=False로 설정하여 바로 삭제되지 않도록
        img_temp.write(response.content)
        img_temp.flush()
        
        # 임시 파일의 경로를 사용하여 Django File 객체 생성
        # File.open(mode='rb')는 파일의 시작으로 포인터를 재설정합니다.
        image_file = File(open(img_temp.name, 'rb'))

        try:
            field = getattr(model_instance, field_name)
            field.save(f"{file_name_prefix}_{model_instance.pk}{ext}", image_file)
            return True
        finally:
            # 작업 완료 후 임시 파일을 수동으로 닫고 삭제
            image_file.close()
            img_temp.close()
            os.unlink(img_temp.name) # 파일 삭제
            
    except requests.exceptions.RequestException as e:
        print(f"이미지 다운로드 실패: {e}")
        return False
    except Exception as e:
        print(f"이미지 저장 중 오류 발생: {e}") # 이 메시지가 출력된 것입니다.
        return False