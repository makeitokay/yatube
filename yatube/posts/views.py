from .models import Post, User
from django.shortcuts import render, redirect
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