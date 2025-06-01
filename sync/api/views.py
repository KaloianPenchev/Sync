from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Post, User, Like, Comment, Follow, Group, GroupMembership
from .serializers import (
    PostSerializer, LikeSerializer, CommentSerializer, 
    FollowSerializer, UserSerializer, RegisterSerializer,
    CustomTokenObtainPairSerializer, GroupSerializer, GroupMembershipSerializer
)


class CustomTokenObtainPairView(TokenObtainPairView):

    serializer_class = CustomTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response(status=status.HTTP_205_RESET_CONTENT)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
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
            return Response(
                {"error": "You don't have permission to edit this post."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        serializer = PostSerializer(post, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if post.user != request.user:
            return Response(
                {"error": "You don't have permission to delete this post."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def post_like(request, pk):

    post = get_object_or_404(Post, pk=pk)
    
    user = request.user
    
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

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def comment_detail(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    
    if request.method == 'GET':
        serializer = CommentSerializer(comment)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        if comment.user != request.user:
            return Response(
                {"error": "You don't have permission to edit this comment."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if comment.user != request.user and comment.post.user != request.user:
            return Response(
                {"error": "You don't have permission to delete this comment."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
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
    
    is_following = Follow.objects.filter(follower=request.user, followed=user).exists()
    data['is_following'] = is_following
    
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
def user_follow(request, username):
    try:
        followed_user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    follower_user = request.user
    
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
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
def explore_posts(request):
    user = request.user
    
    following_ids = Follow.objects.filter(follower=user).values_list('followed_id', flat=True)
    
    following_ids = list(following_ids)
    following_ids.append(user.id)
    
    posts = Post.objects.exclude(user_id__in=following_ids).order_by('-created_at')
    
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(posts, request)
    
    serializer = PostSerializer(result_page, many=True)
    
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def feed(request):
    user = request.user
    
    following_ids = Follow.objects.filter(follower=user).values_list('followed_id', flat=True)
    
    following_ids = list(following_ids)
    following_ids.append(user.id)
    
    posts = Post.objects.filter(user_id__in=following_ids).order_by('-created_at')
    

    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(posts, request)
    

    serializer = PostSerializer(result_page, many=True)
    
    
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def group_list(request):
    if request.method == 'GET':
        groups = Group.objects.all().order_by('-created_at')
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(groups, request)
        serializer = GroupSerializer(result_page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
    
    elif request.method == 'POST':
        serializer = GroupSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            group = serializer.save(owner=request.user)
            GroupMembership.objects.create(user=request.user, group=group, role='admin')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def group_detail(request, pk):
    group = get_object_or_404(Group, pk=pk)
    
    if request.method == 'GET':
        serializer = GroupSerializer(group, context={'request': request})
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        if group.owner != request.user:
            return Response(
                {"error": "You don't have permission to edit this group."},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = GroupSerializer(group, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if group.owner != request.user:
            return Response(
                {"error": "You don't have permission to delete this group."},
                status=status.HTTP_403_FORBIDDEN
            )
        group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def group_membership(request, pk):
    group = get_object_or_404(Group, pk=pk)
    user = request.user

    if request.method == 'POST': # Join group
        if GroupMembership.objects.filter(user=user, group=group).exists():
            return Response(
                {"error": "You are already a member of this group."},
                status=status.HTTP_400_BAD_REQUEST
            )
        membership = GroupMembership.objects.create(user=user, group=group)
        serializer = GroupMembershipSerializer(membership)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    elif request.method == 'DELETE': # Leave group
        if group.owner == user:
            return Response(
                {"error": "Group owner cannot leave the group directly. Transfer ownership or delete the group."},
                status=status.HTTP_400_BAD_REQUEST
            )
        membership = GroupMembership.objects.filter(user=user, group=group).first()
        if not membership:
            return Response(
                {"error": "You are not a member of this group."},
                status=status.HTTP_400_BAD_REQUEST
            )
        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def group_members_list(request, pk):
    group = get_object_or_404(Group, pk=pk)
    memberships = GroupMembership.objects.filter(group=group).order_by('date_joined')
    
    paginator = PageNumberPagination()
    paginator.page_size = 20 
    result_page = paginator.paginate_queryset(memberships, request)
    serializer = GroupMembershipSerializer(result_page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)

