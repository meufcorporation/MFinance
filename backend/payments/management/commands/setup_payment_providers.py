from django.core.management.base import BaseCommand
from payments.models import PaymentProvider


class Command(BaseCommand):
    help = 'Створити початкових платіжних провайдерів'

    def handle(self, *args, **options):
        """Створити провайдерів платежів"""
        
        providers = [
            {
                'name': 'mono',
                'display_name': 'Mono Bank',
                'is_active': True,
                'api_url': 'https://api.monobank.ua',
                'webhook_url': 'https://mfinance.com/api/payments/webhook/mono',
                'credentials': {
                    'api_token': 'YOUR_MONO_API_TOKEN',
                    'merchant_id': 'YOUR_MERCHANT_ID'
                },
                'settings': {
                    'currency': 'UAH',
                    'timeout': 30,
                    'retry_attempts': 3
                }
            },
            {
                'name': 'privat',
                'display_name': 'PrivatBank',
                'is_active': True,
                'api_url': 'https://api.privatbank.ua',
                'webhook_url': 'https://mfinance.com/api/payments/webhook/privat',
                'credentials': {
                    'access_token': 'YOUR_PRIVAT_ACCESS_TOKEN',
                    'merchant_id': 'YOUR_MERCHANT_ID'
                },
                'settings': {
                    'currency': 'UAH',
                    'timeout': 30,
                    'retry_attempts': 3
                }
            },
            {
                'name': 'open_banking',
                'display_name': 'Open Banking',
                'is_active': True,
                'api_url': 'https://api.openbanking.ua',
                'webhook_url': 'https://mfinance.com/api/payments/webhook/open-banking',
                'credentials': {
                    'access_token': 'YOUR_OPEN_BANKING_TOKEN',
                    'client_id': 'YOUR_CLIENT_ID'
                },
                'settings': {
                    'currency': 'UAH',
                    'timeout': 30,
                    'retry_attempts': 3
                }
            },
            {
                'name': 'manual',
                'display_name': 'Ручна сплата',
                'is_active': True,
                'api_url': None,
                'webhook_url': None,
                'credentials': {},
                'settings': {
                    'requires_confirmation': True,
                    'notification_enabled': True
                }
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for provider_data in providers:
            provider, created = PaymentProvider.objects.get_or_create(
                name=provider_data['name'],
                defaults=provider_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Створено провайдера: {provider.display_name}')
                )
            else:
                # Оновити існуючого провайдера
                for key, value in provider_data.items():
                    if key != 'name':
                        setattr(provider, key, value)
                provider.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'🔄 Оновлено провайдера: {provider.display_name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Налаштування провайдерів завершено!\n'
                f'Створено: {created_count}\n'
                f'Оновлено: {updated_count}'
            )
        )
