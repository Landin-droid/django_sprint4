from django.urls import path
from .views import (
    UserUpdateView, UserDetailView, PostListView,
    PostCreateView, PostUpdateView, PostDeleteView,
    PostDetailView, CategoryPostsView, CommentCreateView,
    CommentUpdateView, CommentDeleteView
    )
from . import views


app_name = "blog"

urlpatterns = [
    path("", PostListView.as_view(), name="index"),
    path("posts/create/", PostCreateView.as_view(), name="create_post"),
    path("posts/<int:pk>/", PostDetailView.as_view(), name="post_detail"),
    path("posts/<int:pk>/edit/", PostUpdateView.as_view(), name="edit_post"),
    path("posts/<int:pk>/delete/", PostDeleteView.as_view(), name="delete_post"),
    path("category/<slug:category_slug>/", CategoryPostsView.as_view(),
         name="category_posts"),
    path('profile/edit/', UserUpdateView.as_view(), name='edit_profile'),
    path('profile/<str:username>/', UserDetailView.as_view(), name='profile'),
    path("posts/<int:post_pk>/comment/", CommentCreateView.as_view(), name="add_comment"),
    path("posts/<int:post_pk>/edit_comment/<int:comment_pk>/", CommentUpdateView.as_view(), name="edit_comment"),
    path("posts/<int:post_pk>/delete_comment/<int:comment_pk>/", CommentDeleteView.as_view(), name="delete_comment"),
]
