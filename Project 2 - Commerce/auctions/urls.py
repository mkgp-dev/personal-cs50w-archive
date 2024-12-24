from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('create-auction', views.create_auction, name="create_auction"),
    path('item/<int:item_id>', views.item_page, name="item_page"),
    path('watchlist', views.watchlist_page, name="watchlist_page"),
    path('category', views.category_page, name="category_page"),
    path('category/<str:category>/', views.category_list, name="category_list"),
]
