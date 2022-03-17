from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User
from .utils import create_comments_tree

page_size = settings.REST_FRAMEWORK['PAGE_SIZE']


@cache_page(20, key_prefix='index_page')
def index(request):
    post_list = Post.objects.select_related(
        'author').select_related('group').all()
    paginator = Paginator(post_list, page_size)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    groups = Group.objects.all()
    posts = Post.objects.all()[:5]
    context = {
        'page_obj': page_obj,
        'groups': groups,
        'posts': posts,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(
        Group.objects.prefetch_related('posts'), slug=slug
    )
    post_list = group.posts.all()
    paginator = Paginator(post_list, page_size)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(
        User.objects.prefetch_related('posts'), username=username
    )
    post_list = author.posts.all()
    paginator = Paginator(post_list, page_size)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    author = User.objects.get(username=username)
    if (
        not request.user.is_authenticated
        or request.user == author
    ):
        context = {
            'page_obj': page_obj,
            'author': author,
        }
        return render(request, 'posts/profile.html', context)
    following = Follow.objects.filter(
        user=request.user, author=author).exists()
    context = {
        'page_obj': page_obj,
        'author': author,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related(
            'author').select_related('group'), pk=post_id)
    amount = post.author.posts.count()
    comments = post.comments.all()
    comment_list = create_comments_tree(comments)
    paginator = Paginator(comment_list, page_size)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    form = CommentForm()
    context = {
        'post': post,
        'amount': amount,
        'form': form,
        'page_obj': page_obj,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        f = form.save(commit=False)
        f.author = request.user
        form.save()
        return redirect('posts:profile', f.author)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        request.FILES or None,
        instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'form': form,
        'post': post,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)
    post.delete()
    return redirect('posts:index')


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.content_type = ContentType.objects.get(model='post')
        comment.object_id = post_id
        comment.parent = None
        comment.is_child = False
        comment.save()
    return redirect('posts:post_detail', post_id=post.id)


@login_required
@transaction.atomic
def add_child_comment(request):
    print(request.POST)
    username = request.POST.get('user')
    current_id = request.POST.get('id')
    text = request.POST.get('text')
    author = get_object_or_404(User, username=username)
    content_type = ContentType.objects.get(model='post')
    parent = Comment.objects.get(id=int(current_id))
    object_id = parent.object_id
    is_child = False if not parent else True
    post = get_object_or_404(Post, pk=object_id)
    Comment.objects.create(
        author=author, text=text, content_type=content_type,
        object_id=object_id, parent=parent, is_child=is_child
    )
    comments_ = post.comments.all()
    comment_list = create_comments_tree(comments_)
    paginator = Paginator(comment_list, page_size)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    form = CommentForm()
    context = {
        'post': post,
        'form': form,
        'page_obj': page_obj,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def delete_comment(request, comment_id):
    print(comment_id)
    comment = get_object_or_404(
        Comment.objects.select_related('author'), pk=comment_id)
    post_id = comment.object_id
    if request.user != comment.author:
        return redirect('posts:post_detail', post_id=post_id)
    comment.delete()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, page_size)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow = get_object_or_404(Follow, user=request.user, author=author)
    follow.delete()
    return redirect('posts:profile', username=username)
