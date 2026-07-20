from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.admin_dashboard, name='admin_dashboard'),

    # Members
    path('members/', views.MemberListView.as_view(), name='member_list'),
    path('members/create/', views.MemberCreateView.as_view(), name='member_create'),
    path('members/<int:pk>/update/', views.MemberUpdateView.as_view(), name='member_update'),
    path('members/<int:pk>/delete/', views.MemberDeleteView.as_view(), name='member_delete'),

    # Certifications
    path('certifications/pending/', views.pending_certifications, name='pending_certifications'),
    path('certifications/<int:pk>/certify/', views.certify_member, name='certify_member'),

    # Content
    path('news/create/', views.news_create, name='news_create'),
    path('gallery/create/', views.gallery_create, name='gallery_create'),
    path('event/create/', views.event_create, name='event_create'),

    # Finance
    path('finance/', views.finance_list, name='finance_list'),
    path('finance/create/', views.finance_create, name='finance_create'),
    path('finance/<int:pk>/update/', views.finance_update, name='finance_update'),
    path('finance/<int:pk>/delete/', views.finance_delete, name='finance_delete'),
    path('finance/<int:pk>/paid/', views.finance_mark_paid, name='finance_mark_paid'),
]
