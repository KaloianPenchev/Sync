from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views.auth import RegisterView, CustomTokenObtainPairView, logout_view
from .views.feed import feed, explore_posts
from .views.posts import (
    post_list, post_detail, post_like,
    post_likes_list, post_comments,
)
from .views.comments import comment_detail
from .views.users import (
    user_detail, user_posts, user_follow,
    user_followers, user_following,
)
from .views.groups import (
    group_list, group_detail, group_membership,
    group_members_list, group_posts,
)

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="auth-login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="auth-refresh"),
    path("auth/logout/", logout_view, name="auth-logout"),

    path("feed/", feed, name="feed"),
    path("explore/", explore_posts, name="explore-posts"),

    path("posts/", post_list, name="post-list"),
    path("posts/<int:pk>/", post_detail, name="post-detail"),
    path("posts/<int:pk>/like/", post_like, name="post-like"),
    path("posts/<int:pk>/likes/", post_likes_list, name="post-likes-list"),
    path("posts/<int:pk>/comments/", post_comments, name="post-comments"),

    path("comments/<int:pk>/", comment_detail, name="comment-detail"),

    path("users/<str:username>/", user_detail, name="user-detail"),
    path("users/<str:username>/posts/", user_posts, name="user-posts"),
    path("users/<str:username>/follow/", user_follow, name="user-follow"),
    path("users/<str:username>/followers/", user_followers, name="user-followers"),
    path("users/<str:username>/following/", user_following, name="user-following"),

    path("groups/", group_list, name="group-list"),
    path("groups/<int:pk>/", group_detail, name="group-detail"),
    path("groups/<int:pk>/membership/", group_membership, name="group-membership"),
    path("groups/<int:pk>/members/", group_members_list, name="group-members-list"),
    path("groups/<int:pk>/posts/", group_posts, name="group-posts"),
]
