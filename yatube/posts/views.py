from django.core.paginator import Paginator
from django.db.models import Count

from .models import Post, User, Group, Comment, Follow
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .forms import PostForm, CommentForm


def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)


def index(request):
    post_list = (
        Post.objects.select_related("author")
        .select_related("group")
        .order_by("-pub_date")
        .annotate(comment_count=Count("comments"))
        .all()
    )
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "index.html", {"page": page, "paginator": paginator})


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            user = request.user
            text = form.cleaned_data["text"]
            group = form.cleaned_data["group"]
            image = form.cleaned_data["image"]
            post = Post.objects.create(text=text, group=group, image=image, author=user)

            return redirect("post", username=user.username, post_id=post.id)

    return render(request, "new_post.html", {"form": form})


def view_post(request, username, post_id, comment_post=None):
    profile = get_object_or_404(
        User.objects.annotate(posts_count=Count("post_author")), username=username
    )
    post = get_object_or_404(
        Post.objects.select_related("author")
        .select_related("group")
        .annotate(comment_count=Count("comments")),
        pk=post_id,
    )

    comments = Comment.objects.filter(post=post)
    form = CommentForm(comment_post)

    return render(
        request,
        "post.html",
        {"profile": profile, "post": post, "comments": comments, "form": form,},
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)

    posts = (
        Post.objects.filter(group=group)
        .select_related("author")
        .select_related("group")
        .order_by("-pub_date")
        .annotate(comment_count=Count("comments"))
        .all()
    )
    paginator = Paginator(posts, 10)

    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request,
        "group.html",
        {"group": group, "posts": posts, "page": page, "paginator": paginator},
    )


def profile(request, username):
    profile = get_object_or_404(
        User.objects.annotate(posts_count=Count("posts")), username=username
    )
    post_list = (
        Post.objects.filter(author=profile)
        .select_related("author")
        .select_related("group")
        .order_by("-pub_date")
        .all()
        .annotate(comment_count=Count("comments"))
    )
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(author=profile, user=request.user).exists()

    return render(
        request,
        "profile.html",
        {
            "profile": profile,
            "page": page,
            "paginator": paginator,
            "following": following,
        },
    )


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(
        Post.objects.annotate(comment_count=Count("comments")),
        pk=post_id,
        author__username=username,
    )
    user = get_object_or_404(User, username=username)

    if request.user != user:
        return redirect("post", username=username, post_id=post.id)

    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("post", username=username, post_id=post.id)

    return render(request, "edit_post.html", {"form": form, "post": post})


@login_required
def post_delete(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author=request.user)

    if request.user.username != username:
        return redirect("post", username=username, post_id=post_id)

    post.delete()
    return redirect("profile", username=username)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)

    form = CommentForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            author = request.user
            text = form.cleaned_data["text"]
            Comment.objects.create(text=text, author=author, post=post)

    return redirect("post", username=username, post_id=post.id)


@login_required
def follow_index(request):
    follow = Follow.objects.values_list("author", flat=True).filter(user=request.user)
    posts = (
        Post.objects.filter(author__in=follow)
        .select_related("author")
        .select_related("group")
        .order_by("-pub_date")
        .annotate(comment_count=Count("comments"))
    )
    paginator = Paginator(posts, 10)

    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request, "follow.html", {"posts": posts, "page": page, "paginator": paginator}
    )


@login_required
def profile_follow(request, username):
    user = get_object_or_404(User, username=username)
    if (
        request.user.username == username
        or Follow.objects.filter(user=request.user, author=user).exists()
    ):
        return redirect("profile", username=username)
    Follow.objects.create(user=request.user, author=user)
    return redirect("profile", username=username)


@login_required
def profile_unfollow(request, username):
    user = get_object_or_404(User, username=username)
    follow = get_object_or_404(Follow, user=request.user, author=user)
    follow.delete()
    return redirect("profile", username=username)
