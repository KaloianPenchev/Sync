from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import Post, User
from .serializers import PostSerializer

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
