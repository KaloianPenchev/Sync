from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from ..models import Group, GroupMembership, Post
from ..serializers import GroupSerializer, GroupMembershipSerializer, PostSerializer

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
            return Response({"error": "You don't have permission to edit this group."}, status=status.HTTP_403_FORBIDDEN)
        serializer = GroupSerializer(group, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        if group.owner != request.user:
            return Response({"error": "You don't have permission to delete this group."}, status=status.HTTP_403_FORBIDDEN)
        group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def group_membership(request, pk):
    group = get_object_or_404(Group, pk=pk)
    user = request.user
    if request.method == 'POST':
        if GroupMembership.objects.filter(user=user, group=group).exists():
            return Response({"error": "You are already a member of this group."}, status=status.HTTP_400_BAD_REQUEST)
        membership = GroupMembership.objects.create(user=user, group=group)
        serializer = GroupMembershipSerializer(membership)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    elif request.method == 'DELETE':
        if group.owner == user:
            return Response({"error": "Group owner cannot leave the group directly. Transfer ownership or delete the group."}, status=status.HTTP_400_BAD_REQUEST)
        membership = GroupMembership.objects.filter(user=user, group=group).first()
        if not membership:
            return Response({"error": "You are not a member of this group."}, status=status.HTTP_400_BAD_REQUEST)
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

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def group_posts(request, pk):
    group = get_object_or_404(Group, pk=pk)
    user = request.user
    if request.method == 'GET':
        posts = Post.objects.filter(group=group).order_by('-created_at')
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(posts, request)
        serializer = PostSerializer(result_page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
    elif request.method == 'POST':
        if not GroupMembership.objects.filter(user=user, group=group).exists():
            return Response({"error": "You must be a member of the group to post."}, status=status.HTTP_403_FORBIDDEN)
        serializer = PostSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                serializer.save(user=user, group=group)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
