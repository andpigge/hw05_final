from django.contrib import admin

from .models import Post, Group, Comment, Follow


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'created',
        'author',
        'group',
        'edited',
        'image'
    )
    list_editable = ('group', 'image')
    search_fields = ('text',)
    list_filter = ('created',)
    empty_value_display = '-пусто-'
    readonly_fields = ('edited',)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'title',
        'description',
        'slug'
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'author',
        'post',
        'created',
        'edited'
    )
    search_fields = ('text',)
    list_filter = ('created',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'author'
    )
