from django.urls import path
from . import views


app_name = 'posts'

follow_post = (
    path(
        'follow/',
        views.follow_index,
        name='follow_index'
    ),
    path(
        'follow/<str:username>/',
        views.follow_author,
        name='follow_author'
    ),
    path(
        'profile/<str:username>/follow/',
        views.profile_follow,
        name='profile_follow'
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.profile_unfollow,
        name='profile_unfollow'
    )
)

urlpatterns = [
    path(
        '',
        views.index,
        name='index'
    ),
    path(
        'group/<slug:slug>/',
        views.group_posts,
        name='group_posts'
    ),
    path(
        'profile/<str:username>/',
        views.profile,
        name='profile'
    ),
    path(
        'posts/<int:post_id>/',
        views.post_detail,
        name='post_detail'
    ),
    path(
        'posts/<int:post_id>/edit/',
        views.post_edit,
        name='post_edit'
    ),
    path(
        'create/',
        views.post_create,
        name='post_create'
    ),
    path(
        'posts/<int:post_id>/comment/',
        views.add_comment,
        name='add_comment'
    ),
    path(
        'posts/<int:post_id>/delete/',
        views.post_delete,
        name='post_delete'
    ),
    path(
        'posts/<int:comment_id>/comment/delete/',
        views.comment_delete,
        name='comment_delete'
    ),
    *follow_post
]
