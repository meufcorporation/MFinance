from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'templates', views.ReportTemplateViewSet)
router.register(r'reports', views.ReportViewSet)
router.register(r'data', views.ReportDataViewSet)
router.register(r'signatures', views.DigitalSignatureViewSet)
router.register(r'submissions', views.ReportSubmissionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
