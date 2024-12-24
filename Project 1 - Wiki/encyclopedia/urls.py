from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('wiki/<str:title>', views.wiki_content, name='wiki_content'),
    path('wiki/<str:title>/edit', views.edit_page, name='wiki_edit'),
    path('create-page', views.create_new_page, name='create_page'),
    path('give-me-something-random', views.random_page, name='randomizer'),
]
