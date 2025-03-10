from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("listing/<int:pk>", views.show_listing, name="show_listing"),
    path("watchlist", views.watch_list, name="watchlist"),
    path("category/<str:category>", views.category, name="category"),
    path("categories", views.show_categories, name="show_categories")
]
