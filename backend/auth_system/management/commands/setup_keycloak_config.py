from django.core.management.base import BaseCommand
from auth_system.models import KeycloakConfig, Role


class Command(BaseCommand):
    help = 'Налаштувати конфігурацію Keycloak та базові ролі'

    def handle(self, *args, **options):
        # Створити конфігурацію Keycloak
        config, created = KeycloakConfig.objects.get_or_create(
            name='development',
            defaults={
                'server_url': 'http://localhost:8080',
                'realm_name': 'mfinance',
                'client_id': 'mfinance-web',
                'client_secret': 'mfinance-secret-key-2024',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('✅ Конфігурація Keycloak створена')
            )
        else:
            self.stdout.write(
                self.style.WARNING('⚠️ Конфігурація Keycloak вже існує')
            )
        
        # Створити базові ролі
        roles_data = [
            {
                'name': 'user',
                'description': 'Звичайний користувач системи',
                'permissions': ['view_own_data', 'create_transactions', 'view_reports']
            },
            {
                'name': 'admin',
                'description': 'Адміністратор системи',
                'permissions': ['*']  # Всі дозволи
            },
            {
                'name': 'accountant',
                'description': 'Бухгалтер',
                'permissions': ['view_all_data', 'create_reports', 'manage_budgets']
            },
            {
                'name': 'fop',
                'description': 'Фізична особа-підприємець',
                'permissions': ['manage_fop_profile', 'view_tax_obligations', 'create_payments']
            }
        ]
        
        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults={
                    'description': role_data['description'],
                    'permissions': role_data['permissions'],
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Роль "{role.name}" створена')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Роль "{role.name}" вже існує')
                )
        
        self.stdout.write(
            self.style.SUCCESS('\n🎉 Налаштування Keycloak завершено!')
        )
