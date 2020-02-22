from django.core.paginator import Paginator

from .models import Post, User, Group
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .forms import PostForm


def index(request):
    post_list = Post.objects.order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page, 'paginator': paginator})


@login_required
def new_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            user = request.user
            text = form.cleaned_data["text"]
            group = form.cleaned_data["group"]
            post = Post.objects.create(text=text, group=group, author=user)

            return redirect("post", username=user.username, post_id=post.id)
        return render(request, 'new_post.html', {"form": form})

    form = PostForm()
    return render(request, 'new_post.html', {"form": form})


def view_post(request, username, post_id):
    profile = User.objects.get(username=username)
    post = Post.objects.get(pk=post_id)
    posts_count = Post.objects.filter(author__id=profile.id).count()

    return render(request, 'post.html', {"profile": profile, "post": post, "posts_count": posts_count})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)

    posts = Post.objects.filter(group=group).order_by("-pub_date").all()
    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group, "posts": posts, "page": page, "paginator": paginator})


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=profile).order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    posts_count = Post.objects.filter(author=profile).count()

    return render(request, "profile.html", {'profile': profile, 'page': page, 'paginator': paginator, "posts_count": posts_count})


def post_edit(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)

    if request.user.username != username:
        return redirect("post", username=username, post_id=post.id)

    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post.text = form.cleaned_data["text"]
            post.group = form.cleaned_data["group"]
            post.save()

            return redirect("post", username=username, post_id=post.id)
        return render(request, 'edit_post.html', {"form": form})

    form = PostForm(instance=post)
    return render(request, 'edit_post.html', {"form": form, "post": post})
