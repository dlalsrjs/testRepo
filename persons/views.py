# persons/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Case, When, Value, IntegerField, F, Count # 검색을 위해 Q 객체 임포트
from django.views.decorators.http import require_POST, require_GET, require_http_methods # HTTP 메서드 데코레이터
from django.urls import reverse
# from django.views.decorators.csrf import csrf_exempt # 개발 중 테스트를 위해 임시 사용 (프로덕션에서는 제거)
from .models import JapaneseActor, KoreanPerson
from .forms import JapaneseActorForm, KoreanPersonForm # 새로 정의한 폼 임포트
from django.core.paginator import Paginator
import urllib

# 1. 일본 배우 목록 뷰
def japanese_actor_list(request):
    query = request.GET.get('q', '')
    looks_query = request.GET.get('looks', '')
    sort_by = request.GET.get('sort', 'name')
    order = request.GET.get('order', 'asc')

    actors = JapaneseActor.objects.all().annotate(
        work_count=Count('japanesework', distinct=True)
    )

    if query:
        actors = actors.filter(
            Q(name__icontains=query) | Q(other_names__icontains=query) | Q(description__icontains=query)
        )
    if looks_query:
        actors = actors.filter(looks=looks_query)

    if sort_by == 'random':
        actors = actors.order_by('?')
    elif sort_by == 'looks':
        looks_order = Case(
            When(looks='GOD', then=Value(0)), When(looks='SSS', then=Value(1)),
            When(looks='SS', then=Value(2)), When(looks='S', then=Value(3)),
            When(looks='A', then=Value(4)), When(looks='B', then=Value(5)),
            When(looks='C', then=Value(6)), When(looks='D', then=Value(7)),
            When(looks='F', then=Value(8)), default=Value(9),
            output_field=IntegerField(),
        )
        order_expression = looks_order.desc() if order == 'desc' else looks_order.asc()
        actors = actors.order_by(order_expression, 'name')
    elif sort_by in ['name', 'birth_year', 'debut_year', 'hardness', 'work_count']:
        order_expression = F(sort_by).desc(nulls_last=True) if order == 'desc' else F(sort_by).asc(nulls_last=True)
        actors = actors.order_by(order_expression, 'name')
    else:
        actors = actors.order_by('name')

    paginator = Paginator(actors, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    sort_options = [
        {'key': 'name', 'value': '이름'}, {'key': 'birth_year', 'value': '출생연도'},
        {'key': 'debut_year', 'value': '데뷔연도'}, {'key': 'work_count', 'value': '작품 개수'},
        {'key': 'looks', 'value': '외모'}, {'key': 'hardness', 'value': '하드함'},
    ]
    
    # ✨✨✨ 핵심 수정사항 1: 'looks_choices'를 뷰에서 직접 정의합니다. ✨✨✨
    looks_choices = [
        ("GOD", "GOD"), ("SSS", "SSS"), ("SS", "SS"), ("S", "S"),
        ("A", "A"), ("B", "B"), ("C", "C"), ("D", "D"), ("F", "F"),
    ]
    
    base_params = {k: v for k, v in request.GET.items() if k != 'page'}
    context = {
        'actors': page_obj, 'query': query, 'looks_query': looks_query,
        'looks_choices': looks_choices, # 직접 정의한 리스트를 전달
        'current_sort': sort_by, 'current_order': order,
        'sort_options': sort_options, 'base_params_encoded': urllib.parse.urlencode(base_params),
    }
    return render(request, 'persons/japanese_actor_list.html', context)

# 2. 한국 인물 목록 뷰
def korean_person_list(request):
    query = request.GET.get('q', '')
    tag_query = request.GET.get('tag', '')
    looks_query = request.GET.get('looks', '')
    sort_by = request.GET.get('sort', 'name')
    order = request.GET.get('order', 'asc')

    persons = KoreanPerson.objects.all().annotate(
        video_count=Count('koreanvideo', distinct=True)
    )

    if query:
        persons = persons.filter(
            Q(name__icontains=query) | Q(description__icontains=query) |
            Q(looks__icontains=query) | Q(other_names__icontains=query)
        )
    if tag_query:
        persons = persons.filter(tags__name__icontains=tag_query)
    if looks_query:
        persons = persons.filter(looks=looks_query)

    if sort_by == 'looks':
        looks_order_case = Case(
            When(looks='GOD', then=Value(0)), When(looks='SSS', then=Value(1)),
            When(looks='SS', then=Value(2)), When(looks='S', then=Value(3)),
            When(looks='A', then=Value(4)), When(looks='B', then=Value(5)),
            When(looks='C', then=Value(6)), When(looks='D', then=Value(7)),
            When(looks='F', then=Value(8)), default=Value(9),
            output_field=IntegerField()
        )
        order_expression = looks_order_case.desc() if order == 'desc' else looks_order_case.asc()
        persons = persons.order_by(order_expression, 'name')
    elif sort_by in ['name', 'birth_year', 'video_count']:
        order_expression = F(sort_by).desc(nulls_last=True) if order == 'desc' else F(sort_by).asc(nulls_last=True)
        persons = persons.order_by(order_expression, 'name')
    else:
        persons = persons.order_by('name')

    paginator = Paginator(persons, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    sort_options = [
        {'key': 'name', 'value': '이름'}, {'key': 'birth_year', 'value': '출생연도'},
        {'key': 'looks', 'value': '외모'}, {'key': 'video_count', 'value': '영상 개수'},
    ]
    
    # ✨✨✨ 핵심 수정사항 2: 'looks_choices'를 뷰에서 직접 정의합니다. ✨✨✨
    looks_choices = [
        ("GOD", "GOD"), ("SSS", "SSS"), ("SS", "SS"), ("S", "S"),
        ("A", "A"), ("B", "B"), ("C", "C"), ("D", "D"), ("F", "F"),
    ]
    
    base_params = {k: v for k, v in request.GET.items() if k != 'page'}
    context = {
        'persons': page_obj, 'query': query, 'tag_query': tag_query, 'looks_query': looks_query,
        'looks_choices': looks_choices, # 직접 정의한 리스트를 전달
        'current_sort': sort_by, 'current_order': order,
        'sort_options': sort_options, 'base_params_encoded': urllib.parse.urlencode(base_params),
    }
    return render(request, 'persons/korean_person_list.html', context)

# 배우 수정 모달을 위한 함수 (GET 요청)
def edit_japanese_actor(request, pk):
    actor = get_object_or_404(JapaneseActor, pk=pk)
    if request.method == 'POST':
        form = JapaneseActorForm(request.POST, request.FILES, instance=actor)
        if form.is_valid():
            # ArrayField 'other_names' 수동 처리 수정
            cleaned_other_names = form.cleaned_data['other_names']
            if isinstance(cleaned_other_names, str): # 문자열인 경우에만 split
                # 쉼표로 구분된 문자열을 리스트로 변환
                actor.other_names = [name.strip() for name in cleaned_other_names.split(',') if name.strip()]
            elif isinstance(cleaned_other_names, list): # 이미 리스트인 경우 그대로 사용
                actor.other_names = [name.strip() for name in cleaned_other_names if name.strip()]
            else: # 그 외의 경우 (예: None)
                actor.other_names = None

            # 나머지 필드는 form.save()가 처리
            # 하지만 other_names를 수동으로 할당했으므로, save(commit=False) 후 수동 저장
            form.save(commit=False) # other_names가 이미 instance에 할당되었으므로 commit=False
            actor.save() # actor 객체 직접 저장

            return JsonResponse({
                'success': True,
                'name': actor.name,
                'other_names': actor.other_names if actor.other_names else [],
                'birth_year': actor.birth_year,
                'debut_year': actor.debut_year,
                'looks': actor.looks,
                'hardness': actor.hardness,
                'description': actor.description,
                'image_url': actor.image.url if actor.image else ''
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors.as_json()
            }, status=400)
    else: # GET 요청
        # ArrayField 'other_names'를 폼에 전달할 때 쉼표로 구분된 문자열로 변환하여 초기값 설정
        # 이것은 사용자가 폼 필드에 텍스트로 보게 되는 부분입니다.
        initial_other_names = ",".join(actor.other_names) if actor.other_names else ""
        form = JapaneseActorForm(instance=actor, initial={'other_names': initial_other_names})
        return render(request, 'persons/actor_edit_modal_content.html', {'form': form, 'actor_id': pk})
    
def edit_korean_person(request, pk):
    person = get_object_or_404(KoreanPerson, pk=pk)
    if request.method == 'POST':
        form = KoreanPersonForm(request.POST, request.FILES, instance=person)
        if form.is_valid():
            person = form.save(commit=False) # ManyToManyField 저장을 위해 commit=False
            person.save()
            form.save_m2m() # ManyToManyField 저장

            # 업데이트된 ManyToMany 필드 데이터 가져오기 (이름 목록으로)
            updated_tags = [tag.name for tag in person.tags.all()]

            return JsonResponse({
                'success': True,
                'name': person.name,
                'other_names': person.other_names if person.other_names else [],
                'birth_year': person.birth_year,
                'tags': updated_tags, # 태그 이름 리스트로 반환
                'looks': person.looks,
                'description': person.description,
                'image_url': person.image.url if person.image else '',
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors.as_json()
            }, status=400)
    else: # GET 요청
        form = KoreanPersonForm(instance=person)
        return render(request, 'persons/edit_person_form.html', {'form': form, 'person': person})
    
@require_POST
# @csrf_exempt # CSRF 토큰을 JavaScript에서 처리하기 전까지 임시 사용 (프로덕션에서는 제거!)
def delete_japanese_actor(request, pk):
    actor = get_object_or_404(JapaneseActor, pk=pk)
    try:
        actor.delete()
        return JsonResponse({'success': True, 'message': '일본 배우가 성공적으로 삭제되었습니다.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'삭제 중 오류 발생: {str(e)}'}, status=400)

@require_POST
# @csrf_exempt # CSRF 토큰을 JavaScript에서 처리하기 전까지 임시 사용 (프로덕션에서는 제거!)
def delete_korean_person(request, pk):
    person = get_object_or_404(KoreanPerson, pk=pk)
    try:
        person.delete()
        return JsonResponse({'success': True, 'message': '한국 인물이 성공적으로 삭제되었습니다.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'삭제 중 오류 발생: {str(e)}'}, status=400)
    
def view_works_by_actor(request, pk):
    actor = get_object_or_404(JapaneseActor, pk=pk)
    # reverse를 사용하여 기본 URL을 얻은 후 쿼리 파라미터를 수동으로 추가
    base_url = reverse('videos:japanese_work_list')
    # 쿼리 파라미터는 actor_name_query 대신 q 파라미터를 사용해도 됩니다.
    # 하지만 명시적으로 actor_name_query를 받는 것이 더 명확할 수 있습니다.
    # (videos/views.py에서 actor_name_query로 받도록 이미 수정했기 때문)
    return redirect(f"{base_url}?actor_name={actor.name}")

def view_videos_by_person(request, pk):
    person = get_object_or_404(KoreanPerson, pk=pk)
    # reverse를 사용하여 기본 URL을 얻은 후 쿼리 파라미터를 수동으로 추가
    base_url = reverse('videos:korean_video_list')
    # 마찬가지로 person_name_query를 받는 것이 명확합니다.
    return redirect(f"{base_url}?person_name={person.name}")