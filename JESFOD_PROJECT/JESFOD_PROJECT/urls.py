from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from menber_JESFOD.views_fixed import *

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('menber/', include('menber_JESFOD.urls')),
    path('adminjesfod/', include('admin_JESFOD.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

