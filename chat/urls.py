from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('chat/<int:chat_id>/', views.chat, name='chat'),
    path('search_users/', views.search_users, name='search_users'),
    path('start_chat/<int:user2_id>/', views.start_chat, name='start_chat'),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
]