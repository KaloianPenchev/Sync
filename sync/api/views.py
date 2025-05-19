from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import Post, User, Like, Comment, Follow
from .serializers import PostSerializer, LikeSerializer, CommentSerializer, FollowSerializer, UserSerializer

@api_view(['GET', 'POST'])
def post_list(request):
    
    if request.method == 'GET':
        
        paginator = PageNumberPagination()
        paginator.page_size = 10
        
        posts = Post.objects.all().order_by('-created_at')
        
        result_page = paginator.paginate_queryset(posts, request)
        
        serializer = PostSerializer(result_page, many=True)
        
        return paginator.get_paginated_response(serializer.data)
    
    elif request.method == 'POST':
        serializer = PostSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                user = User.objects.first()
                if not user:
                    return Response(
                        {"error": "No users exist in the database. Create a user first."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                serializer.save(user=user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def post_detail(request, pk):
    
    post = get_object_or_404(Post, pk=pk)
    
    if request.method == 'GET':
        serializer = PostSerializer(post)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = PostSerializer(post, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST', 'DELETE'])
def post_like(request, pk):

    post = get_object_or_404(Post, pk=pk)
    
    user = User.objects.first()
    if not user:
        return Response(
            {"error": "No users exist in the database. Create a user first."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if request.method == 'POST':
        if Like.objects.filter(user=user, post=post).exists():
            return Response(
                {"error": "You have already liked this post"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        Like.objects.create(user=user, post=post)
        
        post.likes_count += 1
        post.save()
        
        return Response({"success": "Post liked successfully"}, status=status.HTTP_201_CREATED)
    
    elif request.method == 'DELETE':
        like = Like.objects.filter(user=user, post=post).first()
        
        if not like:
            return Response(
                {"error": "You have not liked this post"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        like.delete()
        
        post.likes_count = max(0, post.likes_count - 1) 
        post.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def post_likes_list(request, pk):

    post = get_object_or_404(Post, pk=pk)
    
    likes = Like.objects.filter(post=post)
    
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(likes, request)
    
    serializer = LikeSerializer(result_page, many=True)
    
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET', 'POST'])
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
            user = User.objects.first()
            if not user:
                return Response(
                    {"error": "No users exist in the database. Create a user first."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer.save(user=user, post=post)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def comment_detail(request, pk):

    comment = get_object_or_404(Comment, pk=pk)
    
    if request.method == 'GET':
        serializer = CommentSerializer(comment)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def user_detail(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = UserSerializer(user)
    
    followers_count = Follow.objects.filter(followed=user).count()
    following_count = Follow.objects.filter(follower=user).count()
    
    data = serializer.data
    data['followers_count'] = followers_count
    data['following_count'] = following_count
    
    return Response(data)

@api_view(['GET'])
def user_posts(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    posts = Post.objects.filter(user=user).order_by('-created_at')
    
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(posts, request)
    
    serializer = PostSerializer(result_page, many=True)
    
    return paginator.get_paginated_response(serializer.data)

@api_view(['POST', 'DELETE'])
def user_follow(request, username):

    try:
        followed_user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    follower_user = User.objects.first()
    if not follower_user:
        return Response(
            {"error": "No users exist in the database. Create a user first."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if follower_user.id == followed_user.id:
        return Response(
            {"error": "You cannot follow yourself"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if request.method == 'POST':
        if Follow.objects.filter(follower=follower_user, followed=followed_user).exists():
            return Response(
                {"error": "You are already following this user"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        follow = Follow.objects.create(follower=follower_user, followed=followed_user)
        
        serializer = FollowSerializer(follow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    elif request.method == 'DELETE':
        follow = Follow.objects.filter(follower=follower_user, followed=followed_user).first()
        
        if not follow:
            return Response(
                {"error": "You are not following this user"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        follow.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def user_followers(request, username):

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    follows = Follow.objects.filter(followed=user)
    
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(follows, request)
    
    serializer = FollowSerializer(result_page, many=True)
    
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
def user_following(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    follows = Follow.objects.filter(follower=user)
    
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(follows, request)
    
    serializer = FollowSerializer(result_page, many=True)
    
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
def explore_posts(request):

    user = User.objects.first()
    if not user:
        return Response(
            {"error": "No users exist in the database."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    following_ids = Follow.objects.filter(follower=user).values_list('followed_id', flat=True)
    
    following_ids = list(following_ids)
    following_ids.append(user.id)
    
    posts = Post.objects.exclude(user_id__in=following_ids).order_by('-created_at')
    
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(posts, request)
    
    serializer = PostSerializer(result_page, many=True)
    
    return paginator.get_paginated_response(serializer.data)
