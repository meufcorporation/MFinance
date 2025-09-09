from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'templates', views.NotificationTemplateViewSet)
router.register(r'notifications', views.NotificationViewSet)
router.register(r'preferences', views.NotificationPreferenceViewSet)
router.register(r'logs', views.NotificationLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
