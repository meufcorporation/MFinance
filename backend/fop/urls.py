from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'profiles', views.FOPProfileViewSet)
router.register(r'tax-periods', views.TaxPeriodViewSet)
router.register(r'settings', views.FOPSettingsViewSet)
router.register(r'tax-obligations', views.TaxObligationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
