from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from .models import Post, Comment, Like, Follow


def home(request):
    if request.method == "POST":
        content = request.POST.get("content")
        post_id = request.POST.get("post_id")
        comment_text = request.POST.get("comment_text")
        like_post_id = request.POST.get("like_post_id")
        follow_user_id = request.POST.get("follow_user_id")

        # Create Post
        if content and not post_id and not like_post_id and not follow_user_id:
            if request.user.is_authenticated:
                Post.objects.create(
                    user=request.user,
                    content=content
                )
            return redirect("home")

        # Create Comment
        if comment_text and post_id:
            if request.user.is_authenticated:
                post = Post.objects.get(id=post_id)

                Comment.objects.create(
                    post=post,
                    user=request.user,
                    text=comment_text
                )

            return redirect("home")

        # Like / Unlike
        if like_post_id:
            if request.user.is_authenticated:
                post = Post.objects.get(id=like_post_id)

                like = Like.objects.filter(
                    post=post,
                    user=request.user
                ).first()

                if like:
                    like.delete()
                else:
                    Like.objects.create(
                        post=post,
                        user=request.user
                    )

            return redirect("home")

        # Follow / Unfollow
        if follow_user_id:
            if request.user.is_authenticated:
                target_user = User.objects.get(id=follow_user_id)

                if target_user != request.user:
                    follow = Follow.objects.filter(
                        follower=request.user,
                        following=target_user
                    ).first()

                    if follow:
                        follow.delete()
                    else:
                        Follow.objects.create(
                            follower=request.user,
                            following=target_user
                        )

            return redirect("home")

    posts = Post.objects.all().order_by("-created_at")
    users = User.objects.exclude(id=request.user.id)

    return render(request, "social/home.html", {
        "posts": posts,
        "users": users
    })


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if username and password:
            if User.objects.filter(username=username).exists():
                return render(request, "social/register.html", {
                    "error": "Username already exists!"
                })

            user = User.objects.create_user(
                username=username,
                password=password
            )

            login(request, user)
            return redirect("home")

    return render(request, "social/register.html")


def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("home")

        return render(request, "social/login.html", {
            "error": "Invalid username or password!"
        })

    return render(request, "social/login.html")


def user_logout(request):
    logout(request)
    return redirect("home")


# Profile Page
def profile(request):
    if not request.user.is_authenticated:
        return redirect("login")

    user = request.user

    posts = Post.objects.filter(
        user=user
    ).order_by("-created_at")

    followers_count = Follow.objects.filter(
        following=user
    ).count()

    following_count = Follow.objects.filter(
        follower=user
    ).count()

    return render(request, "social/profile.html", {
        "user": user,
        "posts": posts,
        "followers_count": followers_count,
        "following_count": following_count,
    })