from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.home, name='member_home'),  # Landing home
    path('login/', views.custom_login, name='login'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.member_dashboard, name='member_dashboard'),
    path('certification/', views.certification, name='certification'),
    path('profile/', views.MemberDetailView.as_view(), name='profile'),
    path('activities/', views.member_activities, name='member_activities'),
    path('news/', views.news_list, name='news_list'),
    path('news/create/', views.news_create, name='news_create'),
    path('news/<int:pk>/', views.NewsDetailView.as_view(), name='news_detail'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
]
