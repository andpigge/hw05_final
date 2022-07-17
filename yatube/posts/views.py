from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm


AMOUNT_POSTS_ON_ONE_PAGE = 10


def get_pagination(request, posts, amount):
    paginator = Paginator(posts, amount)

    page_number = request.GET.get('page')

    return paginator.get_page(page_number)


def index(request):
    author = request.user

    posts = Post.objects.select_related('group').all()

    page_obj = get_pagination(request, posts, AMOUNT_POSTS_ON_ONE_PAGE)

    context = {
        'author': author,
        'page_obj': page_obj
    }

    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)

    posts = group.posts.all()

    page_obj = get_pagination(request, posts, AMOUNT_POSTS_ON_ONE_PAGE)

    context = {
        'group': group,
        'page_obj': page_obj
    }

    return render(request, 'posts/group_list.html', context)


def profile(request, username):

    author = get_object_or_404(User, username=username)

    posts = author.posts.all()

    page_obj = get_pagination(request, posts, AMOUNT_POSTS_ON_ONE_PAGE)

    following = User.objects.filter(following__author=author).exists()

    is_author = author == request.user

    context = {
        'page_obj': page_obj,
        'post_count': page_obj.paginator.count,
        'author': author,
        'following': following,
        'is_author': is_author
    }

    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):

    post = get_object_or_404(Post, pk=post_id)

    comments = post.comments.all()

    post_count = post.author.posts.count()

    author = request.user

    form = CommentForm(request.POST or None)

    context = {
        'post': post,
        'post_count': post_count,
        'author': author,
        'form': form,
        'comments': comments
    }

    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):

    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )

    if not form.is_valid():

        context = {
            'form': form,
            'is_edit': False
        }

        return render(request, 'posts/create_post.html', context)

    author = request.user

    fields = form.save(commit=False)

    fields.author = author

    form.save()

    return redirect('posts:profile', author.username)


@login_required
def post_edit(request, post_id):
    author = request.user

    post = get_object_or_404(Post, pk=post_id)

    if not post.author == author:
        return redirect('posts:post_detail', post.id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )

    if not form.is_valid():

        context = {
            'post': post,
            'form': form,
            'is_edit': True
        }

        return render(request, 'posts/create_post.html', context)

    fields = form.save(commit=False)

    fields.post_edit = True

    form.save()

    return redirect('posts:post_detail', post.id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    form = CommentForm(request.POST or None)

    if form.is_valid():
        fields = form.save(commit=False)

        fields.author = request.user
        fields.post = post

        form.save()

    return redirect('posts:post_detail', post_id=post_id)


@login_required
def post_delete(request, post_id):
    author = request.user

    post = get_object_or_404(Post, pk=post_id)

    if post.author == author:
        post.delete()

    return redirect('posts:index')


@login_required
def comment_delete(request, comment_id):
    author = request.user

    comment = get_object_or_404(Comment, pk=comment_id)

    if comment.author == author:
        comment.delete()

    return redirect('posts:post_detail', comment.post.id)


@login_required
def follow_index(request):
    """ Избранные посты авторов. """

    # В постах, у автора, узнаем на что он подписан
    posts = Post.objects.filter(author__following__user=request.user)

    page_obj = get_pagination(request, posts, AMOUNT_POSTS_ON_ONE_PAGE)

    authors = User.objects.filter(following__user=request.user)

    context = {
        'page_obj': page_obj,
        'authors': authors
    }

    return render(request, 'posts/follow.html', context)


@login_required
def follow_author(request, username):
    """ Перейти на посты автора. """
    posts = Post.objects.filter(author__following__author__username=username)

    page_obj = get_pagination(request, posts, AMOUNT_POSTS_ON_ONE_PAGE)

    authors = User.objects.filter(following__user=request.user)

    context = {
        'page_obj': page_obj,
        'authors': authors,
        'username': username
    }

    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """ Подписаться. """

    # Автор поста
    author = get_object_or_404(User, username=username)

    # Текущий пользователь
    user = request.user

    # Автор, не может подписаться сам на себя
    if not author == user:
        obj, created = Follow.objects.get_or_create(user=user, author=author)

    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    """ Отписаться. """

    # Автор поста
    follow = Follow.objects.filter(
        author__username=username,
        user__username=request.user
    )

    follow.delete()

    return redirect('posts:profile', username)
