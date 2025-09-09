from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'accounts', views.AccountViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'transactions', views.TransactionViewSet)
router.register(r'budgets', views.BudgetViewSet)
router.register(r'rules', views.RuleViewSet)
router.register(r'import-jobs', views.ImportJobViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
