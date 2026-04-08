from django.urls import path
from django.contrib.auth.views import LogoutView
from .views_fixed import *

urlpatterns = [
    path('', home, name='member_home'),  # Landing home
    path('login/', custom_login, name='login'),
    path('register/', register, name='register'),
    path('dashboard/', member_dashboard, name='member_dashboard'),
    path('certification/', certification, name='certification'),
    path('profile/', MemberDetailView.as_view(), name='profile'),
    path('activities/', member_activities, name='member_activities'),
    path('news/', news_list, name='news_list'),
    path('news/create/', news_create, name='news_create'),
    path('news/<int:pk>/', NewsDetailView.as_view(), name='news_detail'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
]
