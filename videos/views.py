# videos/views.py

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q, Count, Subquery, OuterRef, Min, Case, When, Value, IntegerField, F
from django.core.paginator import Paginator
from django.db.models.functions import Coalesce, ExtractYear
import urllib

from .models import JapaneseWork, KoreanVideo, LocalVideo
from .forms import JapaneseWorkForm, KoreanVideoForm, LocalVideoForm
from persons.models import JapaneseActor, KoreanPerson

# 1. 일본 작품 목록 뷰
def japanese_work_list(request):
    query = request.GET.get('q', '')
    tag_query = request.GET.get('tag', '')
    actor_name_query = request.GET.get('actor_name', '')
    sort_by = request.GET.get('sort', 'release_year')
    order = request.GET.get('order', 'desc')

    works_qs = JapaneseWork.objects.prefetch_related('actors', 'tags').all()

    # --- 검색 필터링 ---
    if query:
        works_qs = works_qs.filter(
            Q(product_number__icontains=query) | Q(rating__icontains=query) | Q(urls__icontains=query)
        ).distinct()
    if tag_query:
        works_qs = works_qs.filter(tags__name__icontains=tag_query).distinct()
    if actor_name_query:
        works_qs = works_qs.filter(actors__name__icontains=actor_name_query).distinct()
        
    # --- '당시 나이' 계산을 위한 Annotation ---
    # ✨✨✨ 1. 오류가 발생했던 Subquery를 올바르게 수정합니다. ✨✨✨
    min_birth_year_subquery = JapaneseActor.objects.filter(
        japanesework=OuterRef('pk')
    ).values('japanesework__pk').annotate(
        min_birth=Min('birth_year')
    ).values('min_birth')

    works_qs = works_qs.annotate(
        min_birth_year=Subquery(min_birth_year_subquery, output_field=IntegerField())
    )
    
    works_qs = works_qs.annotate(
        age_at_release=Case(
            When(release_year__isnull=False, min_birth_year__isnull=False, 
                 then=F('release_year') - F('min_birth_year') + 1),
            default=Value(None),
            output_field=IntegerField()
        )
    )

    # --- 정렬 로직 ---
    if sort_by == 'random':
        works_qs = works_qs.order_by('?')
    else:
        sort_field = sort_by if sort_by in ['product_number', 'release_year', 'work_hardness', 'age_at_release'] else 'release_year'
        order_expression = F(sort_field).desc(nulls_last=True) if order == 'desc' else F(sort_field).asc(nulls_last=True)
        works_qs = works_qs.order_by(order_expression, '-pk')

    paginator = Paginator(works_qs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    sort_options = [
        {'key': 'product_number', 'value': '품번'}, {'key': 'release_year', 'value': '출시 연도'},
        {'key': 'work_hardness', 'value': '하드함'}, {'key': 'age_at_release', 'value': '당시 나이'},
    ]

    base_params = {k: v for k, v in request.GET.items() if k != 'page'}
    context = {
        'works': page_obj, 'query': query, 'tag_query': tag_query,
        'actor_name_query': actor_name_query, 'current_sort': sort_by, 'current_order': order,
        'sort_options': sort_options, 'base_params_encoded': urllib.parse.urlencode(base_params),
    }
    return render(request, 'videos/japanese_work_list.html', context)

# 2. 한국 영상 목록 뷰
def korean_video_list(request):
    query = request.GET.get('q', '')
    theme_query = request.GET.get('theme', '')
    tag_query = request.GET.get('tag', '')
    edited_query = request.GET.get('edited')
    person_name_query = request.GET.get('person_name', '')
    sort_by = request.GET.get('sort', 'date')
    order = request.GET.get('order', 'desc')

    videos_qs = KoreanVideo.objects.prefetch_related('persons', 'themes', 'tags').all()
    
    filters = Q()
    if query: filters |= (Q(urls__icontains=query) | Q(description__icontains=query))
    if theme_query: filters &= Q(themes__name__icontains=theme_query)
    if tag_query: filters &= Q(tags__name__icontains=tag_query)
    if edited_query in ['true', 'false']: filters &= Q(edited=(edited_query == 'true'))
    if person_name_query: filters &= Q(persons__name__icontains=person_name_query)
    if filters: videos_qs = videos_qs.filter(filters).distinct()

    # --- '당시 나이' 계산을 위한 Annotation ---
    # ✨✨✨ 2. 오류가 발생했던 Subquery를 올바르게 수정합니다. ✨✨✨
    min_birth_year_subquery = KoreanPerson.objects.filter(
        koreanvideo=OuterRef('pk')
    ).values('koreanvideo__pk').annotate(
        min_birth=Min('birth_year')
    ).values('min_birth')

    videos_qs = videos_qs.annotate(
        min_birth_year=Subquery(min_birth_year_subquery, output_field=IntegerField())
    )

    videos_qs = videos_qs.annotate(
        age_at_release=Case(
            When(date__isnull=False, min_birth_year__isnull=False,
                 then=ExtractYear('date') - F('min_birth_year') + 1),
            default=Value(None),
            output_field=IntegerField()
        )
    )

    # --- 정렬 로직 ---
    if sort_by == 'random':
        videos_qs = videos_qs.order_by('?')
    else:
        sort_field = sort_by if sort_by in ['date', 'age_at_release'] else 'date'
        order_expression = F(sort_field).desc(nulls_last=True) if order == 'desc' else F(sort_field).asc(nulls_last=True)
        videos_qs = videos_qs.order_by(order_expression, '-pk')

    paginator = Paginator(videos_qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    sort_options = [{'key': 'date', 'value': '날짜'}, {'key': 'age_at_release', 'value': '당시 나이'}]
    
    base_params = {k: v for k, v in request.GET.items() if k != 'page'}
    context = {
        'videos': page_obj, 'query': query, 'theme_query': theme_query, 'tag_query': tag_query,
        'edited_query': edited_query, 'person_name_query': person_name_query,
        'current_sort': sort_by, 'current_order': order,
        'sort_options': sort_options, 'base_params_encoded': urllib.parse.urlencode(base_params),
    }
    return render(request, 'videos/korean_video_list.html', context)

def local_video_list(request):
    query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', 'uuid')
    order = request.GET.get('order', 'desc')

    videos = LocalVideo.objects.all()

    if query:
        videos = videos.filter(
            Q(uuid__icontains=query) |
            Q(description__icontains=query) |
            Q(persons__name__icontains=query)
        ).distinct()

    if sort_by == 'random':
        videos = videos.order_by('?')
    else:
        order_expression = F(sort_by).desc(nulls_last=True) if order == 'desc' else F(sort_by).asc(nulls_last=True)
        videos = videos.order_by(order_expression)

    paginator = Paginator(videos, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    sort_options = [
        {'key': 'uuid', 'value': 'UUID'},
    ]
    
    base_params = {k: v for k, v in request.GET.items() if k != 'page'}

    context = {
        'videos': page_obj,
        'query': query,
        'current_sort': sort_by,
        'current_order': order,
        'sort_options': sort_options,
        'base_params_encoded': urllib.parse.urlencode(base_params),
    }
    return render(request, 'videos/local_video_list.html', context)

def edit_japanese_work(request, pk):
    work = get_object_or_404(JapaneseWork, pk=pk)
    if request.method == 'POST':
        form = JapaneseWorkForm(request.POST, request.FILES, instance=work)
        if form.is_valid():
            form.save()
            # JS에서 페이지를 새로고침하므로 간단한 성공 메시지만 반환
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)
    else: # GET 요청
        # 폼의 __init__이 대부분 처리하므로 instance만 넘겨도 되지만,
        # clean_urls과의 일관성을 위해 urls를 initial로 전달하는 것을 유지
        form = JapaneseWorkForm(instance=work)
        return render(request, 'videos/work_edit_modal_content.html', {'form': form, 'work_id': pk})


def edit_korean_video(request, pk):
    video = get_object_or_404(KoreanVideo, pk=pk)
    if request.method == 'POST':
        form = KoreanVideoForm(request.POST, request.FILES, instance=video)
        if form.is_valid():
            form.save()
            # JS에서 페이지를 새로고침하므로 간단한 성공 메시지만 반환
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)
    else: # GET 요청
        # 폼의 __init__이 관계 필드를 처리하므로 instance만 전달
        form = KoreanVideoForm(instance=video)
        return render(request, 'videos/video_edit_modal_content.html', {'form': form, 'video_id': pk})

def edit_local_video(request, pk):
    video = get_object_or_404(LocalVideo, pk=pk)
    if request.method == 'POST':
        form = LocalVideoForm(request.POST, request.FILES, instance=video)
        if form.is_valid():
            video = form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)
    else:
        form = LocalVideoForm(instance=video)
        return render(request, 'videos/_local_video_form.html', {'form': form, 'video': video})

def delete_japanese_work(request, pk):
    work = get_object_or_404(JapaneseWork, pk=pk)
    if request.method == 'POST':
        work.delete()
        return JsonResponse({'success': True, 'message': '작품이 삭제되었습니다.'})
    return JsonResponse({'success': False}, status=405)

def delete_korean_video(request, pk):
    video = get_object_or_404(KoreanVideo, pk=pk)
    if request.method == 'POST':
        video.delete()
        return JsonResponse({'success': True, 'message': '영상이 삭제되었습니다.'})
    return JsonResponse({'success': False}, status=405)

def delete_local_video(request, pk):
    video = get_object_or_404(LocalVideo, pk=pk)
    if request.method == 'POST':
        try:
            video.delete()
            return JsonResponse({'success': True, 'message': '로컬 영상이 성공적으로 삭제되었습니다.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'삭제 중 오류 발생: {str(e)}'}, status=400)
    return JsonResponse({'success': False, 'message': '잘못된 요청입니다.'}, status=405)