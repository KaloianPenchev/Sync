from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from ..models import User, Post, Follow
from ..serializers import UserSerializer, PostSerializer, FollowSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_detail(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    serializer = UserSerializer(user)
    followers_count = user.followers.count()
    following_count = user.following.count()
    data = serializer.data
    data['followers_count'] = followers_count
    data['following_count'] = following_count
    is_following = Follow.objects.filter(follower=request.user, followed=user).exists()
    data['is_following'] = is_following
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_posts(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    posts = Post.objects.filter(user=user).order_by('-created_at')
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(posts, request)
    serializer = PostSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def user_follow(request, username):
    try:
        followed_user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    follower_user = request.user
    if follower_user.id == followed_user.id:
        return Response({"error": "You cannot follow yourself"}, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'POST':
        if Follow.objects.filter(follower=follower_user, followed=followed_user).exists():
            return Response({"error": "You are already following this user"}, status=status.HTTP_400_BAD_REQUEST)
        follow = Follow.objects.create(follower=follower_user, followed=followed_user)
        serializer = FollowSerializer(follow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    elif request.method == 'DELETE':
        follow = Follow.objects.filter(follower=follower_user, followed=followed_user).first()
        if not follow:
            return Response({"error": "You are not following this user"}, status=status.HTTP_400_BAD_REQUEST)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_followers(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    follows = Follow.objects.filter(followed=user)
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(follows, request)
    serializer = FollowSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_following(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    follows = Follow.objects.filter(follower=user)
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(follows, request)
    serializer = FollowSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)
