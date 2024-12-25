import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import User, Post, Follow


def index(request):
    return render(request, "network/index.html", {
        "default_user": request.user.username,
    })


def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


# Improve Pagination system
def pagination(request, query):
    page = request.GET.get('page', 1)
    pagination = Paginator(query, 10)
    pagination_data = pagination.get_page(page)

    data = [
        {
            "id": post.id,
            "username": post.user.username,
            "content": post.content,
            "date": post.created.strftime('%B %d, %Y %I:%M%p'),
            "likes": post.likes.count(),
            "liked": request.user in post.likes.all()
        }
        for post in pagination_data
    ]

    return {
        "posts": data,
        "next": pagination_data.has_next(),
        "previous": pagination_data.has_previous(),
        "page": pagination_data.number,
        "total": pagination.num_pages,
        "user_auth_bool": request.user.is_authenticated,
    }


# Profile page
def profile_index(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return render(request, "network/profile.html", {
            "not_found": True
        })

    # Followers/Following
    followers = user.followers.count()
    following = user.following.count()

    bool_follow = False
    if request.user.is_authenticated and request.user != user:
        bool_follow = Follow.objects.filter(user=user, follower=request.user).exists()

    return render(request, "network/profile.html", {
        "default_user": request.user.username,
        "username": username,
        "followers": followers,
        "following": following,
        "bool_follow": bool_follow,
    })


# User follow
@login_required(login_url=login_view)
def user_follow(request, username):
    try:
        user = User.objects.get(username=username)
    except Exception as e:
        return render(request, index)

    follow_init = Follow.objects.filter(user=user, follower=request.user)

    if request.method == "POST":
        # Anti-stupidity
        if user == request.user:
            return redirect('profile_index', username=username)

        if follow_init.exists():
            follow_init.delete()
            return redirect('profile_index', username=username)
        else:
            Follow.objects.create(user=user, follower=request.user)
            return redirect('profile_index', username=username)


# Following page
@login_required(login_url=login_view)
def following_index(request):
    return render(request, "network/following.html", {
        "default_user": request.user.username,
    })


# API: Create post
@csrf_exempt
@login_required(login_url=login_view)
def create_post(request):
    # Throw error if not POST
    if request.method != "POST":
        return JsonResponse({"error": "Invalid action."}, status=405)

    # Mechanism
    try:
        data = json.loads(request.body)
        content = data.get("content", "").strip()

        if not content:
            return JsonResponse({"error": "Content cannot be empty."}, status=400)

        post = Post.objects.create(user=request.user, content=content)

        return JsonResponse({"message": "Post created succesfully."}, status=200)
    except Exception as e:
        return JsonResponse({"error": f"An error has occurred. {str(e)}"}, status=400)


# Pagination draft
# https://docs.djangoproject.com/en/4.0/topics/pagination/
# https://docs.djangoproject.com/en/4.0/ref/paginator/#django.core.paginator.Paginator
# def post_list(request):
#     # Pagination
#     page = request.GET.get('page', 1)
#     posts = Post.objects.all().order_by('-created')
#     pagination = Paginator(posts, 10)
#     pagination_data = pagination.get_page(page)

#     # Reference from Project 3: Mail
#     # return JsonResponse([email.serialize() for email in emails], safe=False)
#     data = [
#         {
#             "id": post.id,
#             "username": post.user.username,
#             "content": post.content,
#             "date": post.created.strftime('%Y-%m-%d %I:%M%p'),
#             "likes": post.likes
#         }
#         for post in pagination_data
#     ]

#     return JsonResponse({
#         "posts": data,
#         "next": pagination_data.has_next(),
#         "previous": pagination_data.has_previous(),
#         "page": pagination_data.number,
#         "total": pagination.num_pages,
#     }, safe=False)


# API: Fetch post list
def post_list(request):
    query = Post.objects.all().order_by('-created')
    data = pagination(request, query)

    return JsonResponse(data, safe=False)


# API: Fetch profile post list
# @login_required(login_url=login_view)
def profile_list(request, username):
    try:
        user = User.objects.get(username=username)
    except Exception as e:
        return JsonResponse({"error": f"An error has occured. {str(e)}"}, status=400)

    query = Post.objects.filter(user=user).order_by('-created')
    data = pagination(request, query)

    return JsonResponse(data, safe=False)


# API: Fetch following post list
@login_required(login_url=login_view)
def following_list(request):
    following = Follow.objects.filter(follower=request.user).values_list('user', flat=True)
    query = Post.objects.filter(user__in=following).order_by('-created')

    data = pagination(request, query)
    return JsonResponse(data, safe=False)


# API: Edit post
@csrf_exempt
@login_required(login_url=login_view)
def edit_post(request, var_id):
    if request.method == "PUT":
        try:
            post = Post.objects.get(id=var_id, user=request.user)
            data = json.loads(request.body)

            content = data.get('content', '').strip()
            if not content:
                return JsonResponse({"error": "Content cannot be empty."}, status=400)

            # Anti-stupidity
            if request.user.username != post.user.username:
                return JsonResponse({"error": "Forbidden action."}, status=400)

            post.content = content
            post.save()

            return JsonResponse({"message": "Content updated successfully.", "content": post.content}, status=200)
        except Exception as e:
            return JsonResponse({"error": f"An error has occured. {str(e)}"}, status=400)

    return JsonResponse({"error": "Invalid method."}, status=405)


# API: Like/Unlike post
@csrf_exempt
@login_required(login_url=login_view)
def like_post(request, var_id):
    if request.method == "PUT":
        try:
            post = Post.objects.get(id=var_id)
            user = request.user
            data = json.loads(request.body)

            like = data.get('like', None)
            if like is None:
                return JsonResponse({"error": "Like variable is missing."}, status=400)

            if like and user not in post.likes.all():
                post.likes.add(user)
            elif not like and user in post.likes.all():
                post.likes.remove(user)

            return JsonResponse({"message": "Successfully liked the post.", "likes": post.likes.count(), "bool": like}, status=200)
        except Exception as e:
            return JsonResponse({"error": f"An error has occured. {str(e)}"}, status=400)

    return JsonResponse({"error": "Invalid method."}, status=405)