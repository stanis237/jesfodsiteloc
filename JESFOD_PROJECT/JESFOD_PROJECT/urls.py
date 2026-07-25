from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from menber_JESFOD.views_fixed import *

urlpatterns = [
    path('', home, name='home'),
    path('evenements/', public_events, name='public_events'),
    path('evenements/<int:pk>/', public_event_detail, name='public_event_detail'),
    path('galerie/', public_gallery, name='public_gallery'),
    path('galerie/<int:pk>/download/', download_photo, name='download_photo'),
    path('admin/', admin.site.urls),
    path('contact/', contact_submit, name='contact_submit'),
    path('membre/<int:pk>/', public_member_detail, name='public_member_detail'),
    path('manifest.json', pwa_manifest, name='pwa_manifest'),
    path('sw.js', pwa_serviceworker, name='pwa_serviceworker'),
    path('menber/', include('menber_JESFOD.urls')),
    path('adminjesfod/', include('admin_JESFOD.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

