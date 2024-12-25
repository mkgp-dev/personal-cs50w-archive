
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('profile/<str:username>', views.profile_index, name="profile_index"),
    path('profile/<str:username>/follow', views.user_follow, name="user_follow"),
    path('following', views.following_index, name="following_index"),

    # APIs
    path('posts/', views.post_list, name="post_list"),
    path('posts/create', views.create_post, name="create_post"),
    path('posts/<str:username>', views.profile_list, name="profile_list"),
    path('posts/following/', views.following_list, name="following_list"),
    path('posts/<int:var_id>/edit', views.edit_post, name="edit_post"),
    path('posts/<int:var_id>/like', views.like_post, name="like_post"),
]
