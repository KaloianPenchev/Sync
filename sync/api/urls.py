from django.urls import path
from . import views

urlpatterns = [
    path("posts/", views.post_list, name="post-list"),
    path("posts/<int:pk>/", views.post_detail, name="post-detail"),
    path("posts/<int:pk>/like/", views.post_like, name="post-like"),
    path("posts/<int:pk>/likes/", views.post_likes_list, name="post-likes-list"),
    path("posts/<int:pk>/comments/", views.post_comments, name="post-comments"),
    path("posts/explore/", views.explore_posts, name="explore-posts"),
    path("comments/<int:pk>/", views.comment_detail, name="comment-detail"),
    path("users/<str:username>/", views.user_detail, name="user-detail"),
    path("users/<str:username>/posts/", views.user_posts, name="user-posts"),
    path("users/<str:username>/follow/", views.user_follow, name="user-follow"),
    path("users/<str:username>/followers/", views.user_followers, name="user-followers"),
    path("users/<str:username>/following/", views.user_following, name="user-following"),
]
