from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BankViewSet, BankAccountViewSet, BankTransactionViewSet,
    BankTokenViewSet, BankWebhookViewSet, BankSyncLogViewSet
)

router = DefaultRouter()
router.register(r'banks', BankViewSet, basename='bank')
router.register(r'accounts', BankAccountViewSet, basename='bankaccount')
router.register(r'transactions', BankTransactionViewSet, basename='banktransaction')
router.register(r'tokens', BankTokenViewSet, basename='banktoken')
router.register(r'webhooks', BankWebhookViewSet, basename='bankwebhook')
router.register(r'sync-logs', BankSyncLogViewSet, basename='banksynclog')

urlpatterns = [
    path('', include(router.urls)),
]
