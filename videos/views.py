# videos/views.py

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q, Count, Subquery, OuterRef, Min, Case, When, Value, IntegerField, F
from django.core.paginator import Paginator
from django.db.models.functions import Coalesce, ExtractYear
import urllib

from .models import JapaneseWork, KoreanVideo
from .forms import JapaneseWorkForm, KoreanVideoForm
from persons.models import JapaneseActor, KoreanPerson

# 중복 함수를 모두 제거하고, 모든 오류를 수정한 최종 버전입니다.
def japanese_work_list(request):
    query = request.GET.get('q', '')
    tag_query = request.GET.get('tag', '')
    actor_name_query = request.GET.get('actor_name')
    sort_by = request.GET.get('sort', 'release_year')
    order = request.GET.get('order', 'desc')

    works_qs = JapaneseWork.objects.prefetch_related('actors', 'tags').all()

    # --- 검색 쿼리 처리 ---
    if query:
        works_qs = works_qs.filter(
            Q(product_number__icontains=query) | Q(rating__icontains=query) | Q(urls__icontains=query)
        ).distinct()
    if tag_query:
        works_qs = works_qs.filter(tags__name__icontains=tag_query).distinct()
    if actor_name_query:
        works_qs = works_qs.filter(actors__name__icontains=actor_name_query).distinct()

    # --- 정렬을 위한 Annotation 로직 ---
    # *** 오류 수정: 'actors__looks' -> 'looks' ***
    # 이 부분이 FieldError의 원인이었습니다.
    looks_order_case = Case(
        When(looks='GOD', then=Value(0)), When(looks='SSS', then=Value(1)),
        When(looks='SS', then=Value(2)), When(looks='S', then=Value(3)),
        When(looks='A', then=Value(4)), When(looks='B', then=Value(5)),
        When(looks='C', then=Value(6)), When(looks='D', then=Value(7)),
        When(looks='F', then=Value(8)),
        default=Value(9), output_field=IntegerField()
    )

    best_looks_subquery = JapaneseActor.objects.filter(
        japanesework=OuterRef('pk')
    ).annotate(order=looks_order_case).order_by('order').values('order')[:1]

    min_birth_year_subquery = JapaneseActor.objects.filter(
        japanesework=OuterRef('pk')
    ).values('japanesework__pk').annotate(min_birth=Min('birth_year')).values('min_birth')

    works_qs = works_qs.annotate(
        tag_count=Count('tags', distinct=True),
        max_looks_order=Coalesce(Subquery(best_looks_subquery), Value(9)),
        min_birth_year=Subquery(min_birth_year_subquery, output_field=IntegerField())
    )
    
    works_qs = works_qs.annotate(
        age_at_release=Case(
            When(release_year__isnull=False, min_birth_year__isnull=False,
                 then=F('release_year') - F('min_birth_year') + 1),
            default=Value(-1),
            output_field=IntegerField()
        )
    )

    # --- 정렬 로직 ---
    if sort_by == 'random':
        works_qs = works_qs.order_by('?')
    else:
        sort_field_map = {
            'product_number': 'product_number', 'tag_count': 'tag_count',
            'release_year': 'release_year', 'age_at_release': 'age_at_release',
            'looks': 'max_looks_order', 'work_hardness': 'work_hardness'
        }
        sort_field = sort_field_map.get(sort_by, 'release_year')
        
        base_order = []
        if sort_by == 'age_at_release':
            works_qs = works_qs.annotate(is_age_valid=Case(When(age_at_release__gt=0, then=1), default=0))
            base_order.append(F('is_age_valid').desc())

        order_flow = F(sort_field).desc(nulls_last=True) if order == 'desc' else F(sort_field).asc(nulls_last=True)
        works_qs = works_qs.order_by(*base_order, order_flow, '-pk')

    paginator = Paginator(works_qs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    sort_options = [
        {'key': 'product_number', 'value': '품번'}, {'key': 'tag_count', 'value': '태그 개수'},
        {'key': 'release_year', 'value': '출시 연도'}, {'key': 'age_at_release', 'value': '당시 나이'},
        {'key': 'looks', 'value': '외모'}, {'key': 'work_hardness', 'value': '작품 하드함'},
    ]

    base_params = {k: v for k, v in request.GET.items() if k != 'page'}

    context = {
        'works': page_obj,
        'query': query,
        'tag_query': tag_query,
        'actor_name_query': actor_name_query,
        'current_sort': sort_by,
        'current_order': order,
        'sort_options': sort_options,
        'base_params_encoded': urllib.parse.urlencode(base_params),
    }
    return render(request, 'videos/japanese_work_list.html', context)


def korean_video_list(request):
    # GET 파라미터 가져오기
    query = request.GET.get('q', '')
    theme_query = request.GET.get('theme', '')
    tag_query = request.GET.get('tag', '')
    edited_query = request.GET.get('edited')
    person_name_query = request.GET.get('person_name')
    sort_by = request.GET.get('sort', 'date') # 기본 정렬: 날짜
    order = request.GET.get('order', 'desc') # 기본 순서: 내림차순

    videos_qs = KoreanVideo.objects.prefetch_related('persons', 'themes', 'tags').all()

    # --- 검색 필터링 ---
    filters = Q()
    if query:
        filters |= (Q(urls__icontains=query) | Q(description__icontains=query))
    if theme_query:
        filters &= Q(themes__name__icontains=theme_query)
    if tag_query:
        filters &= Q(tags__name__icontains=tag_query)
    if person_name_query:
        filters &= Q(persons__name__icontains=person_name_query)
    if edited_query:
        if edited_query.lower() == 'true':
            filters &= Q(edited=True)
        elif edited_query.lower() == 'false':
            filters &= Q(edited=False)
    if filters:
        videos_qs = videos_qs.filter(filters).distinct()

    # --- 정렬을 위한 Annotation 로직 ---
    looks_order_case = Case(
        When(looks='GOD', then=Value(0)), When(looks='SSS', then=Value(1)),
        When(looks='SS', then=Value(2)), When(looks='S', then=Value(3)),
        When(looks='A', then=Value(4)), When(looks='B', then=Value(5)),
        When(looks='C', then=Value(6)), When(looks='D', then=Value(7)),
        When(looks='F', then=Value(8)),
        default=Value(9), output_field=IntegerField()
    )

    best_looks_subquery = KoreanPerson.objects.filter(
        koreanvideo=OuterRef('pk')
    ).annotate(order=looks_order_case).order_by('order').values('order')[:1]

    min_birth_year_subquery = KoreanPerson.objects.filter(
        koreanvideo=OuterRef('pk')
    ).values('koreanvideo__pk').annotate(min_birth=Min('birth_year')).values('min_birth')

    videos_qs = videos_qs.annotate(
        max_looks_order=Coalesce(Subquery(best_looks_subquery), Value(9)),
        min_birth_year=Subquery(min_birth_year_subquery, output_field=IntegerField())
    )
    
    videos_qs = videos_qs.annotate(
        age_at_release=Case(
            When(date__isnull=False, min_birth_year__isnull=False,
                 then=ExtractYear('date') - F('min_birth_year') + 1),
            default=Value(-1),
            output_field=IntegerField()
        )
    )

    # --- 정렬 로직 ---
    if sort_by == 'random':
        videos_qs = videos_qs.order_by('?')
    else:
        sort_field_map = {
            'date': 'date',
            'age': 'age_at_release',
            'looks': 'max_looks_order',
        }
        sort_field = sort_field_map.get(sort_by, 'date')
        
        base_order = []
        if sort_by == 'age':
            videos_qs = videos_qs.annotate(is_age_valid=Case(When(age_at_release__gt=0, then=1), default=0))
            base_order.append(F('is_age_valid').desc())

        order_flow = F(sort_field).desc(nulls_last=True) if order == 'desc' else F(sort_field).asc(nulls_last=True)
        videos_qs = videos_qs.order_by(*base_order, order_flow, '-pk')

    paginator = Paginator(videos_qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    sort_options = [
        {'key': 'date', 'value': '날짜'},
        {'key': 'age', 'value': '나이'},
        {'key': 'looks', 'value': '외모'},
    ]
    
    base_params = {k: v for k, v in request.GET.items() if k != 'page'}

    context = {
        'videos': page_obj,
        'query': query,
        'theme_query': theme_query,
        'tag_query': tag_query,
        'edited_query': edited_query,
        'person_name_query': person_name_query,
        'current_sort': sort_by,
        'current_order': order,
        'sort_options': sort_options,
        'base_params_encoded': urllib.parse.urlencode(base_params),
    }
    return render(request, 'videos/korean_video_list.html', context)


def edit_japanese_work(request, pk):
    work = get_object_or_404(JapaneseWork, pk=pk)
    if request.method == 'POST':
        form = JapaneseWorkForm(request.POST, request.FILES, instance=work)
        if form.is_valid():
            work = form.save()
            updated_actors = [actor.name for actor in work.actors.all()]
            updated_tags = [tag.name for tag in work.tags.all()]

            return JsonResponse({
                'success': True,
                'product_number': work.product_number,
                'urls': work.urls if work.urls else [],
                'actors': updated_actors,
                'tags': updated_tags,
                'release_year': work.release_year,
                'rating': work.rating,
                'work_hardness': work.work_hardness,
                'image_url': work.image.url if work.image else '',
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)
    else:
        initial_urls = ",".join(work.urls) if work.urls else ""
        form = JapaneseWorkForm(instance=work, initial={'urls': initial_urls})
        return render(request, 'videos/work_edit_modal_content.html', {'form': form, 'work_id': pk})


def edit_korean_video(request, pk):
    video = get_object_or_404(KoreanVideo, pk=pk)
    if request.method == 'POST':
        form = KoreanVideoForm(request.POST, request.FILES, instance=video)
        if form.is_valid():
            video = form.save()
            updated_persons = [person.name for person in video.persons.all()]
            updated_themes = [theme.name for theme in video.themes.all()]
            updated_tags = [tag.name for tag in video.tags.all()]

            return JsonResponse({
                'success': True,
                'urls': video.urls,
                'persons': updated_persons,
                'themes': updated_themes,
                'tags': updated_tags,
                'date': video.date.strftime('%Y년 %m월 %d일') if video.date else None,
                'description': video.description,
                'image_url': video.image.url if video.image else '',
                'edited': video.edited,
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)
    else:
        initial_urls = ",".join(video.urls) if video.urls else ""
        form = KoreanVideoForm(instance=video, initial={'urls': initial_urls})
        return render(request, 'videos/video_edit_modal_content.html', {'form': form, 'video_id': pk})


def delete_japanese_work(request, pk):
    work = get_object_or_404(JapaneseWork, pk=pk)
    if request.method == 'POST':
        try:
            work.delete()
            return JsonResponse({'success': True, 'message': '일본 작품이 성공적으로 삭제되었습니다.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'삭제 중 오류 발생: {str(e)}'}, status=400)
    return JsonResponse({'success': False, 'message': '잘못된 요청입니다.'}, status=405)


def delete_korean_video(request, pk):
    video = get_object_or_404(KoreanVideo, pk=pk)
    if request.method == 'POST':
        try:
            video.delete()
            return JsonResponse({'success': True, 'message': '한국 영상이 성공적으로 삭제되었습니다.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'삭제 중 오류 발생: {str(e)}'}, status=400)
    return JsonResponse({'success': False, 'message': '잘못된 요청입니다.'}, status=405)