from django.urls import path
from . import views

urlpatterns = [
    # Keycloak аутентифікація
    path('keycloak/login/', views.KeycloakLoginView.as_view(), name='keycloak_login'),
    
    # Профіль користувача
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    
    # Вихід
    path('logout/', views.LogoutView.as_view(), name='logout'),
]
