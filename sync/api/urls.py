from django.urls import path
from . import views

urlpatterns = [
    path("posts/", views.post_list, name="post-list"),
    path("posts/<int:pk>/", views.post_detail, name="post-detail"),
    path("posts/<int:pk>/like/", views.post_like, name="post-like"),
    path("posts/<int:pk>/likes/", views.post_likes_list, name="post-likes-list"),
]
