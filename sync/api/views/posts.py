from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from ..models import Post, Like, Comment
from ..serializers import PostSerializer, LikeSerializer, CommentSerializer

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def post_list(request):
    if request.method == 'GET':
        paginator = PageNumberPagination()
        paginator.page_size = 10
        posts = Post.objects.all().order_by('-created_at')
        result_page = paginator.paginate_queryset(posts, request)
        serializer = PostSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    elif request.method == 'POST':
        serializer = PostSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'GET':
        serializer = PostSerializer(post)
        return Response(serializer.data)
    elif request.method == 'PUT':
        if post.user != request.user:
            return Response({"error": "You don't have permission to edit this post."}, status=status.HTTP_403_FORBIDDEN)
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        if post.user != request.user:
            return Response({"error": "You don't have permission to delete this post."}, status=status.HTTP_403_FORBIDDEN)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def post_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    user = request.user
    if request.method == 'POST':
        if Like.objects.filter(user=user, post=post).exists():
            return Response({"error": "You have already liked this post"}, status=status.HTTP_400_BAD_REQUEST)
        Like.objects.create(user=user, post=post)
        post.likes_count += 1
        post.save()
        return Response({"success": "Post liked successfully"}, status=status.HTTP_201_CREATED)
    elif request.method == 'DELETE':
        like = Like.objects.filter(user=user, post=post).first()
        if not like:
            return Response({"error": "You have not liked this post"}, status=status.HTTP_400_BAD_REQUEST)
        like.delete()
        post.likes_count = max(0, post.likes_count - 1)
        post.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def post_likes_list(request, pk):
    post = get_object_or_404(Post, pk=pk)
    likes = Like.objects.filter(post=post)
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(likes, request)
    serializer = LikeSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def post_comments(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'GET':
        comments = Comment.objects.filter(post=post).order_by('-created_at')
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(comments, request)
        serializer = CommentSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    elif request.method == 'POST':
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            serializer.save(user=user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
