from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q, F, Count, Prefetch
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
import urllib

from .models import JapanesePhoto, KoreanPhoto, JapanesePhotoImage, KoreanPhotoImage
from .forms import JapanesePhotoForm, KoreanPhotoForm

def japanese_photo_list(request):
    query = request.GET.get('q', '')
    tag_query = request.GET.get('tag', '')
    actor_id = request.GET.get('actor_id', '')
    sort_by = request.GET.get('sort', 'year')
    order = request.GET.get('order', 'desc')

    first_image_prefetch = Prefetch(
        'images',
        queryset=JapanesePhotoImage.objects.order_by('id'),
        to_attr='first_image_list'
    )
    
    photo_sets = JapanesePhoto.objects.prefetch_related(
        'actors', 'tags', first_image_prefetch
    ).annotate(
        image_count=Count('images')
    )

    if query:
        photo_sets = photo_sets.filter(
            Q(description__icontains=query) | Q(actors__name__icontains=query) | Q(tags__name__icontains=query)
        ).distinct()
    if tag_query:
        photo_sets = photo_sets.filter(tags__name__icontains=tag_query).distinct()
    if actor_id:
        photo_sets = photo_sets.filter(actors__pk=actor_id).distinct()

    if sort_by == 'random':
        photo_sets = photo_sets.order_by('?')
    else:
        # 'updated_at' 정렬 조건 추가
        sort_field = sort_by if sort_by in ['year', 'created_at', 'updated_at'] else 'year'
        order_expression = F(sort_field).desc(nulls_last=True) if order == 'desc' else F(sort_field).asc(nulls_last=True)
        photo_sets = photo_sets.order_by(order_expression)

    paginator = Paginator(photo_sets, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    for item in page_obj:
        item.first_image = item.first_image_list[0] if item.first_image_list else None

    # 정렬 옵션에 '수정일' 추가
    sort_options = [
        {'key': 'year', 'value': '연도'}, 
        {'key': 'created_at', 'value': '생성일'},
        {'key': 'updated_at', 'value': '수정일'},
    ]
    base_params = {k: v for k, v in request.GET.items() if k != 'page'}

    context = {
        'photos': page_obj,
        'query': query,
        'tag_query': tag_query,
        'current_sort': sort_by,
        'current_order': order,
        'sort_options': sort_options,
        'base_params_encoded': urllib.parse.urlencode(base_params),
    }
    return render(request, 'photos/japanese_photo_list.html', context)

def korean_photo_list(request):
    query = request.GET.get('q', '')
    tag_query = request.GET.get('tag', '')
    person_id = request.GET.get('person_id', '')
    sort_by = request.GET.get('sort', 'year')
    order = request.GET.get('order', 'desc')

    first_image_prefetch = Prefetch(
        'images',
        queryset=KoreanPhotoImage.objects.order_by('id'),
        to_attr='first_image_list'
    )

    photo_sets = KoreanPhoto.objects.prefetch_related(
        'persons', 'tags', first_image_prefetch
    ).annotate(
        image_count=Count('images')
    )

    if query:
        photo_sets = photo_sets.filter(
            Q(description__icontains=query) | Q(persons__name__icontains=query) | Q(tags__name__icontains=query)
        ).distinct()
    if tag_query:
        photo_sets = photo_sets.filter(tags__name__icontains=tag_query).distinct()
    if person_id:
        photo_sets = photo_sets.filter(persons__pk=person_id).distinct()

    if sort_by == 'random':
        photo_sets = photo_sets.order_by('?')
    else:
        # 'updated_at' 정렬 조건 추가
        sort_field = sort_by if sort_by in ['year', 'created_at', 'updated_at'] else 'year'
        order_expression = F(sort_field).desc(nulls_last=True) if order == 'desc' else F(sort_field).asc(nulls_last=True)
        photo_sets = photo_sets.order_by(order_expression)

    paginator = Paginator(photo_sets, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    for item in page_obj:
        item.first_image = item.first_image_list[0] if item.first_image_list else None

    # 정렬 옵션에 '수정일' 추가
    sort_options = [
        {'key': 'year', 'value': '연도'}, 
        {'key': 'created_at', 'value': '생성일'},
        {'key': 'updated_at', 'value': '수정일'},
    ]
    base_params = {k: v for k, v in request.GET.items() if k != 'page'}

    context = {
        'photos': page_obj,
        'query': query,
        'tag_query': tag_query,
        'current_sort': sort_by,
        'current_order': order,
        'sort_options': sort_options,
        'base_params_encoded': urllib.parse.urlencode(base_params),
    }
    return render(request, 'photos/korean_photo_list.html', context)

def photo_detail_json(request, model_name, pk):
    if model_name == 'japanese':
        model = JapanesePhoto
    elif model_name == 'korean':
        model = KoreanPhoto
    else:
        return JsonResponse({'error': 'Invalid model name'}, status=400)
    
    try:
        photo_set = model.objects.get(pk=pk)
        images = list(photo_set.images.all().values('image'))
        image_urls = [img['image'] for img in images]
        return JsonResponse({'images': image_urls})
    except model.DoesNotExist:
        return JsonResponse({'error': 'Photo set not found'}, status=404)

def edit_japanese_photo(request, pk):
    photo_set = get_object_or_404(JapanesePhoto, pk=pk)
    if request.method == 'POST':
        form = JapanesePhotoForm(request.POST, instance=photo_set)
        if form.is_valid():
            images_to_delete = request.POST.getlist('delete_images')
            if images_to_delete:
                JapanesePhotoImage.objects.filter(pk__in=images_to_delete, photo_set=photo_set).delete()
            
            instance = form.save()
            # getlist를 사용하여 여러 이미지 파일을 가져옵니다.
            new_images_files = request.FILES.getlist('new_images')
            form.save_related_data(instance, new_images_files)
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)
    else:
        form = JapanesePhotoForm(instance=photo_set)
        return render(request, 'photos/_photo_edit_form.html', {'form': form, 'photo_set': photo_set})

@require_POST
def delete_japanese_photo(request, pk):
    photo_set = get_object_or_404(JapanesePhoto, pk=pk)
    photo_set.delete()
    return JsonResponse({'success': True})

def edit_korean_photo(request, pk):
    photo_set = get_object_or_404(KoreanPhoto, pk=pk)
    if request.method == 'POST':
        form = KoreanPhotoForm(request.POST, instance=photo_set)
        if form.is_valid():
            images_to_delete = request.POST.getlist('delete_images')
            if images_to_delete:
                KoreanPhotoImage.objects.filter(pk__in=images_to_delete, photo_set=photo_set).delete()

            instance = form.save()
            # getlist를 사용하여 여러 이미지 파일을 가져옵니다.
            new_images_files = request.FILES.getlist('new_images')
            form.save_related_data(instance, new_images_files)
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)
    else:
        form = KoreanPhotoForm(instance=photo_set)
        return render(request, 'photos/_photo_edit_form.html', {'form': form, 'photo_set': photo_set})

@require_POST
def delete_korean_photo(request, pk):
    photo_set = get_object_or_404(KoreanPhoto, pk=pk)
    photo_set.delete()
    return JsonResponse({'success': True})