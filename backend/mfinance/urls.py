"""
URL configuration for mfinance project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/finance/', include('finance.urls')),
    path('api/fop/', include('fop.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/bank/', include('bank_integration.urls')),
    path('api/tax/', include('tax_calculations.urls')),
    path('api/analytics/', include('analytics.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)