from django.contrib import admin
from django.urls import path , include

from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('members/', views.MemberListView.as_view(), name='member_list'),
    path('members/create/', views.MemberCreateView.as_view(), name='member_create'),
    path('members/<int:pk>/update/', views.MemberUpdateView.as_view(), name='member_update'),
    path('members/<int:pk>/delete/', views.MemberDeleteView.as_view(), name='member_delete'),
    path('news/create/', views.news_create, name='news_create'),
    path('gallery/create/', views.gallery_create, name='gallery_create'),
    path('certifications/pending/', views.pending_certifications, name='pending_certifications'),
    path('certifications/<int:pk>/certify/', views.certify_member, name='certify_member'),
]
