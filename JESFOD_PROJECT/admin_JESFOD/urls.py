from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.admin_dashboard, name='admin_dashboard'),

    # Members & Bureau Setup
    path('bureau/setup/', views.bureau_setup, name='bureau_setup'),
    path('members/', views.MemberListView.as_view(), name='member_list'),
    path('members/create/', views.MemberCreateView.as_view(), name='member_create'),
    path('members/<int:pk>/update/', views.MemberUpdateView.as_view(), name='member_update'),
    path('members/<int:pk>/delete/', views.MemberDeleteView.as_view(), name='member_delete'),

    # Certifications
    path('certifications/pending/', views.pending_certifications, name='pending_certifications'),
    path('certifications/<int:pk>/certify/', views.certify_member, name='certify_member'),

    # Content - Gallery CRUD
    path('gallery/', views.gallery_list, name='gallery_list'),
    path('gallery/create/', views.gallery_create, name='gallery_create'),
    path('gallery/<int:pk>/update/', views.gallery_update, name='gallery_update'),
    path('gallery/<int:pk>/delete/', views.gallery_delete, name='gallery_delete'),

    # Content - Event CRUD
    path('events/', views.event_list, name='event_list'),
    path('event/create/', views.event_create, name='event_create'),
    path('event/<int:pk>/update/', views.event_update, name='event_update'),
    path('event/<int:pk>/delete/', views.event_delete, name='event_delete'),

    # Content - News
    path('news/create/', views.news_create, name='news_create'),

    # Finance
    path('finance/', views.finance_list, name='finance_list'),
    path('finance/create/', views.finance_create, name='finance_create'),
    path('finance/<int:pk>/update/', views.finance_update, name='finance_update'),
    path('finance/<int:pk>/delete/', views.finance_delete, name='finance_delete'),
    path('finance/<int:pk>/paid/', views.finance_mark_paid, name='finance_mark_paid'),

    # Séances CRUD
    path('seances/', views.seance_list, name='seance_list'),
    path('seances/create/', views.seance_create, name='seance_create'),
    path('seances/<int:pk>/update/', views.seance_update, name='seance_update'),
    path('seances/<int:pk>/delete/', views.seance_delete, name='seance_delete'),

    # Absences
    path('absences/', views.absence_list, name='absence_list'),
    path('absences/create/', views.absence_create, name='absence_create'),

    # Exports PDF & Reçus
    path('finance/export/pdf/', views.export_finance_pdf, name='export_finance_pdf'),
    path('finance/<int:pk>/receipt/', views.export_receipt_pdf, name='export_receipt_pdf'),
    path('members/export/pdf/', views.export_members_pdf, name='export_members_pdf'),
    path('absences/export/pdf/', views.export_absences_pdf, name='export_absences_pdf'),

    # Rappels Emails
    path('seances/<int:pk>/remind/', views.send_seance_reminder, name='send_seance_reminder'),
    path('finance/<int:pk>/remind/', views.send_finance_reminder, name='send_finance_reminder'),

]
