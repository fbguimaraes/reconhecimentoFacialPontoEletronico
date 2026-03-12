"""
URL configuration for django_backend project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('employees.urls')),
    path('', include('dashboard.urls')),
]

# Servir arquivos de mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customizar admin
admin.site.site_header = "Sistema de Reconhecimento Facial"
admin.site.site_title = "Admin - Reconhecimento Facial"
admin.site.index_title = "Painel de Administração"
