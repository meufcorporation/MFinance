from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'providers', views.PaymentProviderViewSet)
router.register(r'methods', views.PaymentMethodViewSet)
router.register(r'payments', views.PaymentViewSet)
router.register(r'schedules', views.PaymentScheduleViewSet)
router.register(r'templates', views.PaymentTemplateViewSet)
router.register(r'webhooks', views.PaymentWebhookViewSet)
router.register(r'logs', views.PaymentLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
