from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from reports.models import ReportTemplate

User = get_user_model()


class Command(BaseCommand):
    help = 'Створити початкові шаблони звітів'

    def handle(self, *args, **options):
        """Створити шаблони звітів"""
        
        # Отримати або створити адміністратора
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@mfinance.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        templates = [
            {
                'name': 'Звіт з єдиного податку (ЄП) - 1 група',
                'description': 'Шаблон для звіту з єдиного податку для ФОП 1 групи',
                'report_type': 'single_tax',
                'format': 'xml',
                'template_content': '''<?xml version="1.0" encoding="UTF-8"?>
<Report>
    <Header>
        <ReportType>Єдиний податок</ReportType>
        <FOPGroup>1</FOPGroup>
        <Period>{{ tax_period }}</Period>
        <FOPName>{{ fop_name }}</FOPName>
        <FOPCode>{{ fop_code }}</FOPCode>
    </Header>
    <Data>
        <Income>{{ income }}</Income>
        <TaxRate>{{ tax_rate }}</TaxRate>
        <TaxAmount>{{ tax_amount }}</TaxAmount>
        <MinTax>{{ min_tax }}</MinTax>
        <FinalTax>{{ final_tax }}</FinalTax>
    </Data>
</Report>''',
                'is_active': True,
                'is_public': True,
                'version': '1.0'
            },
            {
                'name': 'Звіт з єдиного податку (ЄП) - 2 група',
                'description': 'Шаблон для звіту з єдиного податку для ФОП 2 групи',
                'report_type': 'single_tax',
                'format': 'xml',
                'template_content': '''<?xml version="1.0" encoding="UTF-8"?>
<Report>
    <Header>
        <ReportType>Єдиний податок</ReportType>
        <FOPGroup>2</FOPGroup>
        <Period>{{ tax_period }}</Period>
        <FOPName>{{ fop_name }}</FOPName>
        <FOPCode>{{ fop_code }}</FOPCode>
    </Header>
    <Data>
        <Income>{{ income }}</Income>
        <TaxRate>{{ tax_rate }}</TaxRate>
        <TaxAmount>{{ tax_amount }}</TaxAmount>
        <MinTax>{{ min_tax }}</MinTax>
        <FinalTax>{{ final_tax }}</FinalTax>
    </Data>
</Report>''',
                'is_active': True,
                'is_public': True,
                'version': '1.0'
            },
            {
                'name': 'Звіт з єдиного податку (ЄП) - 3 група',
                'description': 'Шаблон для звіту з єдиного податку для ФОП 3 групи',
                'report_type': 'single_tax',
                'format': 'xml',
                'template_content': '''<?xml version="1.0" encoding="UTF-8"?>
<Report>
    <Header>
        <ReportType>Єдиний податок</ReportType>
        <FOPGroup>3</FOPGroup>
        <Period>{{ tax_period }}</Period>
        <FOPName>{{ fop_name }}</FOPName>
        <FOPCode>{{ fop_code }}</FOPCode>
    </Header>
    <Data>
        <Income>{{ income }}</Income>
        <TaxRate>{{ tax_rate }}</TaxRate>
        <TaxAmount>{{ tax_amount }}</TaxAmount>
        <MinTax>{{ min_tax }}</MinTax>
        <FinalTax>{{ final_tax }}</FinalTax>
    </Data>
</Report>''',
                'is_active': True,
                'is_public': True,
                'version': '1.0'
            },
            {
                'name': 'Звіт з єдиного соціального внеску (ЄСВ)',
                'description': 'Шаблон для звіту з єдиного соціального внеску',
                'report_type': 'social_contribution',
                'format': 'xml',
                'template_content': '''<?xml version="1.0" encoding="UTF-8"?>
<Report>
    <Header>
        <ReportType>Єдиний соціальний внесок</ReportType>
        <Period>{{ tax_period }}</Period>
        <FOPName>{{ fop_name }}</FOPName>
        <FOPCode>{{ fop_code }}</FOPCode>
    </Header>
    <Data>
        <Income>{{ income }}</Income>
        <ESVRate>{{ esv_rate }}</ESVRate>
        <ESVAmount>{{ esv_amount }}</ESVAmount>
        <MinESV>{{ min_esv }}</MinESV>
        <FinalESV>{{ final_esv }}</FinalESV>
    </Data>
</Report>''',
                'is_active': True,
                'is_public': True,
                'version': '1.0'
            },
            {
                'name': 'Звіт з ПДВ',
                'description': 'Шаблон для звіту з податку на додану вартість',
                'report_type': 'vat',
                'format': 'xml',
                'template_content': '''<?xml version="1.0" encoding="UTF-8"?>
<Report>
    <Header>
        <ReportType>Податок на додану вартість</ReportType>
        <Period>{{ tax_period }}</Period>
        <FOPName>{{ fop_name }}</FOPName>
        <FOPCode>{{ fop_code }}</FOPCode>
    </Header>
    <Data>
        <VATIncome>{{ vat_income }}</VATIncome>
        <VATRate>{{ vat_rate }}</VATRate>
        <VATAmount>{{ vat_amount }}</VATAmount>
        <VATDeduction>{{ vat_deduction }}</VATDeduction>
        <FinalVAT>{{ final_vat }}</FinalVAT>
    </Data>
</Report>''',
                'is_active': True,
                'is_public': True,
                'version': '1.0'
            },
            {
                'name': 'PDF Звіт з єдиного податку',
                'description': 'PDF версія звіту з єдиного податку',
                'report_type': 'single_tax',
                'format': 'pdf',
                'template_content': '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Звіт з єдиного податку</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { text-align: center; margin-bottom: 30px; }
        .data { margin: 20px 0; }
        .row { display: flex; justify-content: space-between; margin: 10px 0; }
        .label { font-weight: bold; }
        .value { text-align: right; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Звіт з єдиного податку</h1>
        <p>Період: {{ tax_period }}</p>
        <p>ФОП: {{ fop_name }} ({{ fop_code }})</p>
    </div>
    <div class="data">
        <div class="row">
            <span class="label">Дохід:</span>
            <span class="value">{{ income }} грн</span>
        </div>
        <div class="row">
            <span class="label">Податкова ставка:</span>
            <span class="value">{{ tax_rate }}%</span>
        </div>
        <div class="row">
            <span class="label">Сума податку:</span>
            <span class="value">{{ tax_amount }} грн</span>
        </div>
        <div class="row">
            <span class="label">Мінімальний податок:</span>
            <span class="value">{{ min_tax }} грн</span>
        </div>
        <div class="row">
            <span class="label">До сплати:</span>
            <span class="value"><strong>{{ final_tax }} грн</strong></span>
        </div>
    </div>
</body>
</html>''',
                'is_active': True,
                'is_public': True,
                'version': '1.0'
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for template_data in templates:
            template, created = ReportTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults={
                    **template_data,
                    'created_by': admin_user
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Створено шаблон: {template.name}')
                )
            else:
                # Оновити існуючий шаблон
                for key, value in template_data.items():
                    if key != 'name':
                        setattr(template, key, value)
                template.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'🔄 Оновлено шаблон: {template.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Налаштування шаблонів звітів завершено!\n'
                f'Створено: {created_count}\n'
                f'Оновлено: {updated_count}'
            )
        )
