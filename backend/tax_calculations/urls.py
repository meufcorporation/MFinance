from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TaxRateViewSet, TaxCalculationViewSet, TaxPaymentViewSet,
    TaxRuleViewSet, TaxExemptionViewSet
)

router = DefaultRouter()
router.register(r'rates', TaxRateViewSet, basename='taxrate')
router.register(r'calculations', TaxCalculationViewSet, basename='taxcalculation')
router.register(r'payments', TaxPaymentViewSet, basename='taxpayment')
router.register(r'rules', TaxRuleViewSet, basename='taxrule')
router.register(r'exemptions', TaxExemptionViewSet, basename='taxexemption')

urlpatterns = [
    path('', include(router.urls)),
]
