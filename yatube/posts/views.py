from .models import Post, User, Group
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .forms import PostForm


@login_required
def index(request):
    latest = Post.objects.order_by("-pub_date")[:11]
    return render(request, "index.html", {"posts": latest})


@login_required
def new_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            user = request.user
            text = form.cleaned_data["text"]
            group = form.cleaned_data["group"]
            post = Post.objects.create(text=text, group=group, author=user)

            return redirect(f"/{user.username}/{post.id}")
        return render(request, 'new_post.html', {"form": form})

    form = PostForm()
    return render(request, 'new_post.html', {"form": form})


@login_required
def view_post(request, username, post_id):
    profile = User.objects.get(username=username)
    post = Post.objects.get(pk=post_id)

    return render(request, 'post.html', {"profile": profile, "post": post})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)

    posts = Post.objects.filter(group=group).order_by("-pub_date")[:12]
    return render(request, "group.html", {"group": group, "posts": posts})