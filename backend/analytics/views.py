from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import datetime, timedelta
from .services import AnalyticsService


class AnalyticsViewSet(viewsets.ViewSet):
    """ViewSet for analytics data"""
    permission_classes = [IsAuthenticated]
    
    def get_analytics_service(self):
        return AnalyticsService(self.request.user)
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get dashboard analytics data"""
        period_days = int(request.query_params.get('period_days', 30))
        service = self.get_analytics_service()
        data = service.get_dashboard_data(period_days)
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get category analysis"""
        period_days = int(request.query_params.get('period_days', 30))
        service = self.get_analytics_service()
        data = service.get_category_analysis(period_days)
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def monthly_comparison(self, request):
        """Get monthly comparison data"""
        months = int(request.query_params.get('months', 12))
        service = self.get_analytics_service()
        data = service.get_monthly_comparison(months)
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def budgets(self, request):
        """Get budget analysis"""
        service = self.get_analytics_service()
        data = service.get_budget_analysis()
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def taxes(self, request):
        """Get tax analysis"""
        service = self.get_analytics_service()
        data = service.get_tax_analysis()
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def merchants(self, request):
        """Get merchant analysis"""
        period_days = int(request.query_params.get('period_days', 30))
        service = self.get_analytics_service()
        data = service.get_merchant_analysis(period_days)
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def trends(self, request):
        """Get financial trends"""
        period_days = int(request.query_params.get('period_days', 30))
        service = self.get_analytics_service()
        data = service.get_dashboard_data(period_days)
        
        # Extract trends data
        trends_data = {
            'daily_trends': data.get('daily_trends', []),
            'period_days': period_days
        }
        
        return Response(trends_data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get comprehensive summary"""
        period_days = int(request.query_params.get('period_days', 30))
        service = self.get_analytics_service()
        
        # Get all analytics data
        dashboard_data = service.get_dashboard_data(period_days)
        category_data = service.get_category_analysis(period_days)
        budget_data = service.get_budget_analysis()
        tax_data = service.get_tax_analysis()
        
        summary = {
            'dashboard': dashboard_data,
            'categories': category_data,
            'budgets': budget_data,
            'taxes': tax_data,
            'period_days': period_days,
            'generated_at': timezone.now().isoformat()
        }
        
        return Response(summary)