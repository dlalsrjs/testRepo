# epalist/core/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse # JsonResponse와 HttpResponse 임포트
from django.db.models import Q
from django.views.decorators.http import require_POST, require_GET, require_http_methods # HTTP 메서드 데코레이터
from django.views.decorators.csrf import csrf_exempt # AJAX 테스트를 위해 일시적으로 사용 가능 (프로덕션에서는 csrf_token 사용 권장)
from .models import JapaneseWorkTag, KoreanPersonTag, KoreanVideoTheme, KoreanVideoTag
from persons.models import JapaneseActor, KoreanPerson
from videos.models import JapaneseWork, KoreanVideo
from .forms import JapaneseWorkTagForm, KoreanPersonTagForm, KoreanVideoThemeForm, KoreanVideoTagForm # 새로 정의한 폼 임포트
from django.core.paginator import Paginator
import os
import sys

# 모델의 모든 객체에 대한 DB 행 크기(추정치)를 계산하는 함수
def get_model_db_size(model_cls):
    total_bytes = 0
    # 간단한 추정을 위해, 각 필드의 파이썬 객체 크기를 합산
    for obj in model_cls.objects.all():
        row_size = 0
        for field in obj._meta.get_fields():
            # 관계 필드는 ID 저장을 위해 8바이트로 가정
            if field.is_relation:
                row_size += 8
            else:
                # 일반 필드는 getattr로 값을 가져와 메모리 크기 계산
                value = getattr(obj, field.name, None)
                if value is not None:
                    row_size += sys.getsizeof(value)
        total_bytes += row_size
    return total_bytes

# 파일 크기를 KB, MB, GB 등으로 변환하는 함수
def format_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    import math
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

# 모델의 이미지 필드 총 용량을 계산하는 함수
def get_model_image_size(model_cls):
    total_bytes = 0
    # 이미지 필드가 비어있지 않은 객체만 조회
    for obj in model_cls.objects.exclude(image__in=['', None]):
        try:
            # 파일 시스템에 실제 파일이 존재하고, 접근 가능할 때만 크기를 계산
            if obj.image and hasattr(obj.image, 'path') and os.path.exists(obj.image.path):
                total_bytes += obj.image.size
        except Exception:
            # 파일 경로 문제 등으로 오류 발생 시 무시
            pass
    return total_bytes

# [신규] 용량 상세 정보 제공 뷰
def size_details(request, model_name):
    model_map = {
        'japaneseactor': (JapaneseActor, "일본 배우"),
        'koreanperson': (KoreanPerson, "한국 인물"),
        'japanesework': (JapaneseWork, "일본 작품"),
        'koreanvideo': (KoreanVideo, "한국 영상"),
        'japaneseworktag': (JapaneseWorkTag, "일본 작품 태그"),
        'koreanpersontag': (KoreanPersonTag, "한국 인물 태그"),
        'koreanvideotheme': (KoreanVideoTheme, "한국 영상 주제"),
        'koreanvideotag': (KoreanVideoTag, "한국 영상 태그"),
    }
    
    model_class, model_title = model_map.get(model_name, (None, None))

    if not model_class:
        return HttpResponse("Invalid model name", status=404)

    # 이미지 파일 총 용량 계산
    image_size_bytes = get_model_image_size(model_class)
    # DB 행 추정 총 용량 계산
    db_size_bytes = get_model_db_size(model_class)
    # 두 용량의 합계
    total_size_bytes = image_size_bytes + db_size_bytes

    # 각 용량이 차지하는 비율 계산
    if total_size_bytes > 0:
        image_percentage = round((image_size_bytes / total_size_bytes) * 100, 1)
        db_percentage = 100 - image_percentage
    else:
        image_percentage = 0
        db_percentage = 0

    context = {
        'title': f"{model_title} 용량 구성",
        'image_size': format_size(image_size_bytes),
        'db_size': format_size(db_size_bytes),
        'total_size': format_size(total_size_bytes),
        'image_percentage': image_percentage,
        'db_percentage': db_percentage,
    }
    return render(request, 'core/size_details_modal.html', context)


def home(request):
    # 각 모델 클래스를 리스트로 관리
    all_models = [
        JapaneseActor, KoreanPerson, JapaneseWork, KoreanVideo,
        JapaneseWorkTag, KoreanPersonTag, KoreanVideoTheme, KoreanVideoTag
    ]
    
    # 모델 이름(소문자)을 키로 사용하는 딕셔너리 생성
    model_map_for_size = {model._meta.model_name: model for model in all_models}

    # 각 모델별 데이터 개수 계산
    counts = {
        'japanese_actors': JapaneseActor.objects.count(),
        'korean_persons': KoreanPerson.objects.count(),
        'japanese_works': JapaneseWork.objects.count(),
        'korean_videos': KoreanVideo.objects.count(),
        'japanese_work_tags': JapaneseWorkTag.objects.count(),
        'korean_person_tags': KoreanPersonTag.objects.count(),
        'korean_video_themes': KoreanVideoTheme.objects.count(),
        'korean_video_tags': KoreanVideoTag.objects.count(),
    }
    total_count = sum(counts.values())

    # 각 모델별 이미지 파일 용량 및 DB 용량 계산
    sizes_bytes = {name: get_model_image_size(cls) for name, cls in model_map_for_size.items()}
    db_sizes_bytes = {name: get_model_db_size(cls) for name, cls in model_map_for_size.items()}
    
    # 전체 이미지 용량 및 DB 용량 합계 계산
    total_image_size_bytes = sum(sizes_bytes.values())
    total_db_size_bytes = sum(db_sizes_bytes.values())
    grand_total_size_bytes = total_image_size_bytes + total_db_size_bytes

    # 전체 용량에 대한 비율 계산
    if grand_total_size_bytes > 0:
        total_image_percentage = round((total_image_size_bytes / grand_total_size_bytes) * 100, 1)
        total_db_percentage = 100 - total_image_percentage
    else:
        total_image_percentage = 0
        total_db_percentage = 0

    # 개별 용량을 사람이 읽기 좋은 형태로 변환
    sizes_formatted = {key: format_size(value) for key, value in sizes_bytes.items()}

    context = {
        'counts': counts,
        'total_count': total_count,
        'sizes': sizes_formatted,
        
        # 전체 용량 관련 context 추가
        'total_db_size': format_size(total_db_size_bytes),
        'total_image_size': format_size(total_image_size_bytes),
        'grand_total_size': format_size(grand_total_size_bytes),
        'total_db_percentage': total_db_percentage,
        'total_image_percentage': total_image_percentage,
    }
    return render(request, 'core/home.html', context)

def japanese_work_tag_list(request):
    query = request.GET.get('q', '')
    # type_query 추가
    type_query = request.GET.get('type', '')

    tags = JapaneseWorkTag.objects.all().order_by('name')

    if query:
        tags = tags.filter(name__icontains=query)
    
    # 유형 쿼리가 있으면 필터링
    if type_query:
        tags = tags.filter(type__name__icontains=type_query)

    paginator = Paginator(tags, 20)  # 한 페이지에 20개씩 표시
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'tags': page_obj,
        'query': query,
        'type_query': type_query, # context에 추가
    }
    return render(request, 'core/japanese_work_tag_list.html', context)

def korean_person_tag_list(request):
    tags = KoreanPersonTag.objects.all().order_by('name') # 정렬 기준 필수
    query = request.GET.get('q')
    if query:
        tags = tags.filter(name__icontains=query)

    # ----------- 페이지네이션 추가 -----------
    paginator = Paginator(tags, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # ----------- -------------------- -----------

    context = {'tags': page_obj, 'query': query}
    return render(request, 'core/korean_person_tag_list.html', context)

def korean_video_theme_list(request):
    themes = KoreanVideoTheme.objects.all().order_by('name') # 정렬 기준 필수
    query = request.GET.get('q')
    if query:
        themes = themes.filter(name__icontains=query)

    # ----------- 페이지네이션 추가 -----------
    paginator = Paginator(themes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # ----------- -------------------- -----------

    context = {'themes': page_obj, 'query': query}
    return render(request, 'core/korean_video_theme_list.html', context)

def korean_video_tag_list(request):
    tags = KoreanVideoTag.objects.all().order_by('name') # 정렬 기준 필수
    query = request.GET.get('q')
    if query:
        tags = tags.filter(name__icontains=query)

    # ----------- 페이지네이션 추가 -----------
    paginator = Paginator(tags, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # ----------- -------------------- -----------

    context = {'tags': page_obj, 'query': query}
    return render(request, 'core/korean_video_tag_list.html', context)

# 태그 수정 모달을 위한 공통 함수 (GET 요청)
def _edit_tag_modal(request, model_class, form_class, pk):
    tag = get_object_or_404(model_class, pk=pk)
    form = form_class(instance=tag)
    return render(request, 'core/tag_edit_modal_content.html', {'form': form, 'tag_id': pk})

# 태그 업데이트 처리 (POST 요청)
# @csrf_exempt # CSRF 토큰을 처리하는 JavaScript를 구현하기 전까지 임시로 사용 가능.
               # 하지만 보안을 위해 프로덕션 환경에서는 반드시 제거하고 {% csrf_token %}을 사용해야 합니다.
@require_http_methods(["POST"]) # POST 요청만 허용
def _update_tag_data(request, model_class, form_class, pk):
    tag = get_object_or_404(model_class, pk=pk)
    # 이미지 파일 처리를 위해 request.FILES를 함께 전달
    form = form_class(request.POST, request.FILES, instance=tag)

    if form.is_valid():
        form.save()
        # 성공 시 JSON 응답 반환
        response_data = {
            'success': True,
            'name': tag.name, # 업데이트된 태그명 반환
            'image_url': tag.image.url if tag.image else '', # 업데이트된 이미지 URL 반환
            'tag_id': tag.pk
        }
        if hasattr(tag, 'pumbeon'):
            response_data['pumbeon'] = tag.pumbeon
        return JsonResponse(response_data)
    else:
        # 실패 시 에러 메시지와 함께 JSON 응답 반환
        return JsonResponse({
            'success': False,
            'errors': form.errors.as_json() # 폼 에러를 JSON 형태로 반환
        }, status=400) # Bad Request

# 개별 태그 수정 뷰
def edit_japanese_work_tag(request, pk):
    # AJAX 요청에 대한 인증 확인 (로그인 기능 사용 시)
    # if not request.user.is_authenticated:
    #     return JsonResponse({'success': False, 'error': 'Authentication Required'}, status=403)

    try:
        tag = get_object_or_404(JapaneseWorkTag, pk=pk)
    except JapaneseWorkTag.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Tag not found.'}, status=404)

    if request.method == 'POST':
        form = JapaneseWorkTagForm(request.POST, request.FILES, instance=tag)
        if form.is_valid():
            tag = form.save()
            data = {
                'success': True,
                'tag_id': tag.pk,
                'name': tag.name,
                'pumbeon': tag.pumbeon,
                'type_name': tag.type.name if tag.type else '',
                'image_url': tag.image.url if tag.image else '',
                'description': tag.description, # description 데이터 추가
            }
            return JsonResponse(data)
        else:
            return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)
    
    # GET 요청일 경우 (모달에 폼을 처음 로드할 때)
    form = JapaneseWorkTagForm(instance=tag)
    return render(request, 'core/edit_tag_form.html', {'form': form, 'tag': tag})
def edit_korean_person_tag(request, pk):
    if request.method == 'POST':
        return _update_tag_data(request, KoreanPersonTag, KoreanPersonTagForm, pk)
    else:
        return _edit_tag_modal(request, KoreanPersonTag, KoreanPersonTagForm, pk)

def edit_korean_video_theme(request, pk):
    if request.method == 'POST':
        return _update_tag_data(request, KoreanVideoTheme, KoreanVideoThemeForm, pk)
    else:
        return _edit_tag_modal(request, KoreanVideoTheme, KoreanVideoThemeForm, pk)

def edit_korean_video_tag(request, pk):
    if request.method == 'POST':
        return _update_tag_data(request, KoreanVideoTag, KoreanVideoTagForm, pk)
    else:
        return _edit_tag_modal(request, KoreanVideoTag, KoreanVideoTagForm, pk)

@require_POST
# @csrf_exempt # CSRF 토큰을 JavaScript에서 처리하기 전까지 임시 사용 (프로덕션에서는 제거!)
def delete_japanese_work_tag(request, pk):
    tag = get_object_or_404(JapaneseWorkTag, pk=pk)
    try:
        tag.delete()
        return JsonResponse({'success': True, 'message': '일본 작품 태그가 성공적으로 삭제되었습니다.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'삭제 중 오류 발생: {str(e)}'}, status=400)

@require_POST
# @csrf_exempt # CSRF 토큰을 JavaScript에서 처리하기 전까지 임시 사용 (프로덕션에서는 제거!)
def delete_korean_person_tag(request, pk):
    tag = get_object_or_404(KoreanPersonTag, pk=pk)
    try:
        tag.delete()
        return JsonResponse({'success': True, 'message': '한국 인물 태그가 성공적으로 삭제되었습니다.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'삭제 중 오류 발생: {str(e)}'}, status=400)

@require_POST
# @csrf_exempt # CSRF 토큰을 JavaScript에서 처리하기 전까지 임시 사용 (프로덕션에서는 제거!)
def delete_korean_video_theme(request, pk):
    theme = get_object_or_404(KoreanVideoTheme, pk=pk) # theme 변수명 사용
    try:
        theme.delete()
        return JsonResponse({'success': True, 'message': '한국 영상 주제 태그가 성공적으로 삭제되었습니다.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'삭제 중 오류 발생: {str(e)}'}, status=400)

@require_POST
# @csrf_exempt # CSRF 토큰을 JavaScript에서 처리하기 전까지 임시 사용 (프로덕션에서는 제거!)
def delete_korean_video_tag(request, pk):
    tag = get_object_or_404(KoreanVideoTag, pk=pk)
    try:
        tag.delete()
        return JsonResponse({'success': True, 'message': '한국 영상 태그가 성공적으로 삭제되었습니다.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'삭제 중 오류 발생: {str(e)}'}, status=400)