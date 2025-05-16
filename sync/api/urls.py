from django.urls import path
from . import views

urlpatterns = [
    path("posts/", views.post_list, name="post-list"),
    path("posts/<int:pk>/", views.post_detail, name="post-detail"),
]
