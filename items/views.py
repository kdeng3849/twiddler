import time
import json
import uuid

from django.core import serializers
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from users.models import Profile
from .models import Item, ItemProperty
# from .serializers import ItemSerializer
from .utils import to_dict

def home(request):

    context = {
        'items': []
    }
    query = list(Item.objects.filter(timestamp__lte=time.time()).order_by('-timestamp')[:10])
    for item in query:
        context['items'].append(to_dict(item))

    return render(request, 'items/home.html', context)

@csrf_exempt
def add_item(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error'})

    data = json.loads(request.body, encoding='utf-8')

    try:
        username = request.user.username
        content = data['content']
        # child_type = data['childType']
    except KeyError:
        context = {
            'status': 'error',
            'error': "POST body must include properties 'content', 'parent', and 'media' in the form of JSON",
        }
        return JsonResponse(context)

    item = Item()
    item.id = uuid.uuid4().node
    item.username = username
    item.property = ItemProperty()
    item.content = content
    item.save()

    context = {
        'status': 'OK',
        'id': item.id,
        # 'timestamp': item.timestamp,
    }
    return JsonResponse(context)

@csrf_exempt
def get_item(request, item_id):
    try:
        item = Item.objects.get(id=item_id)
        # query = list(Item.objects.filter(id=item_id).values('id', 'username', 'property', 'retweeted', 'content', 'timestamp'))
    except:
        context = {
            'status': 'error',
            'error': 'Item not found',
        }
        return JsonResponse(context, status=404)

    if request.method == 'DELETE':
        # if not request.user.is_authenticated:
        #     return JsonResponse({'status': 'error'})

        item.delete()
        return HttpResponse(status=200)

    item = to_dict(item)
    context = {
        'status': 'OK',
        'item': item,
    }

    return JsonResponse(context)

@csrf_exempt
def search(request):
    data = json.loads(request.body, encoding='utf-8') if request.body else {}
    timestamp = data.get('timestamp') or time.time()
    limit = data.get('limit') or 25
    q = data.get('q')
    username = data.get('username')
    following = data.get('following')

    print(data)
    print(request.user.username)

    if limit > 100:
        response = {
            'status': 'error',
            'error': 'limit must not be greater than 100'
        }
        return JsonResponse(response)

    response = {
        'status': 'OK',
        'items': [],
    }

    query = Item.objects.filter(timestamp__lte=timestamp).order_by('-timestamp')

    if q:
        keywords_query = Item.objects.none()
        keywords = q.split()
        for keyword in keywords:
            keywords_query |= Item.objects.filter(content__icontains=keyword)
        query &= keywords_query

    if username:
        username_query = Item.objects.filter(username=username)
        query &= username_query

    if following and request.user.is_authenticated:
        # print(request.user.username)
        profile = Profile.objects.get(user__username=request.user.username)
        following_query = Item.objects.filter(username__in=profile.get_following())
        query &= following_query

    # query = timestamp_query & username_query & following_query
    # query = timestamp_query
    query = list(query[:limit])
    for item in query:
        response['items'].append(to_dict(item))

    return JsonResponse(response)

@csrf_exempt
@require_http_methods(["POST"])
def like(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error'})

    data = json.loads(request.body, encoding='utf-8')
    print(data)
    item_id = data['id']

    try:
        item = Item.objects.get(id=item_id)
        item.property.likes += 1
        item.save()
    except:
        return JsonResponse({'status': 'error'})

    response = {
        'status': 'OK',
        'likes': item.property.likes,
    }
    return JsonResponse(response)
