from .models import Post
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def index(request):
    latest = Post.objects.order_by("-pub_date")[:11]
    return render(request, "index.html", {"posts": latest})