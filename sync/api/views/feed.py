from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from ..models import Post, Follow
from ..serializers import PostSerializer

def _get_following_ids(user):
    following_ids = list(Follow.objects.filter(follower=user).values_list('followed_id', flat=True))
    following_ids.append(user.id)
    return following_ids

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def explore_posts(request):
    following_ids = _get_following_ids(request.user)
    posts = Post.objects.exclude(user_id__in=following_ids).order_by('-created_at')
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(posts, request)
    serializer = PostSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def feed(request):
    following_ids = _get_following_ids(request.user)
    posts = Post.objects.filter(user_id__in=following_ids).order_by('-created_at')
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(posts, request)
    serializer = PostSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)
