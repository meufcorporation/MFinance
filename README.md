# MFinance - Financial Management System

Комплексна система управління фінансами для ФОП та малого бізнесу в Україні.

## 🚀 Швидкий старт

### Вимоги
- Docker & Docker Compose
- Git
- 8GB RAM (рекомендовано)

### Запуск в режимі розробки

```bash
# Клонування репозиторію
git clone <repository-url>
cd MFinance

# Запуск всіх сервісів
make up
# або
docker-compose up -d

# Перевірка статусу
make status
# або
docker-compose ps
```

### Доступні сервіси

| Сервіс | URL | Опис |
|--------|-----|------|
| **Frontend** | http://localhost:3000 | Web Cabinet (Next.js) |
| **Backend API** | http://localhost:8000 | Django REST API |
| **Admin Panel** | http://localhost:8000/admin | Django Admin |
| **Grafana** | http://localhost:3001 | Моніторинг (admin/admin) |
| **MinIO** | http://localhost:9000 | Файлове сховище (minioadmin/minioadmin) |
| **Prometheus** | http://localhost:9090 | Метрики |
| **RabbitMQ** | http://localhost:15672 | Message Broker (admin/admin) |
| **Keycloak** | http://localhost:8080 | Identity Provider (admin/admin) |

## 🏗️ Архітектура

### Backend (Django)
- **Python 3.11** + Django 5 + DRF
- **PostgreSQL** - основна база даних
- **Redis** - кеш та брокер повідомлень
- **Celery** - фонові завдання
- **OpenTelemetry** - моніторинг

### Frontend (Next.js)
- **Next.js 14** з App Router
- **Tailwind CSS** - стилізація
- **NextAuth.js** - аутентифікація
- **React Table** - таблиці даних

### Інфраструктура
- **Docker Compose** - оркестрація
- **Prometheus + Grafana** - моніторинг
- **MinIO** - файлове сховище
- **Keycloak** - управління користувачами

## 📁 Структура проекту

```
MFinance/
├── backend/                 # Django Backend
│   ├── finance/            # Фінансовий модуль
│   ├── fop/                # ФОП модуль
│   ├── notifications/      # Система нотифікацій
│   ├── bank_integration/   # Інтеграція з банками
│   ├── tax_calculations/   # Розрахунки податків
│   ├── analytics/          # Аналітика
│   └── mfinance/           # Основні налаштування
├── frontend/               # Next.js Frontend
│   └── web-cabinet/        # Web Cabinet
├── mobile/                 # Flutter Mobile App
├── infrastructure/         # Конфігурація інфраструктури
├── docker-compose.yml      # Development
├── docker-compose.prod.yml # Production
├── docker-compose.test.yml # Testing
└── Makefile               # Команди управління
```

## 🛠️ Команди управління

### Основні команди
```bash
make up          # Запуск в режимі розробки
make up-prod     # Запуск в production режимі
make down        # Зупинка всіх сервісів
make restart     # Перезапуск сервісів
make logs        # Перегляд логів
make status      # Статус сервісів
```

### Розробка
```bash
make build       # Збірка Docker образів
make migrate     # Запуск міграцій
make shell-backend   # Shell Django
make shell-frontend  # Shell Next.js
```

### Тестування
```bash
make test        # Запуск всіх тестів
make test-backend    # Тести backend
make test-frontend   # Тести frontend
make lint        # Перевірка коду
make format      # Форматування коду
```

### Управління даними
```bash
make createsuperuser  # Створення адміна
make loaddata         # Завантаження тестових даних
make backup          # Резервна копія БД
make restore FILE=backup.sql  # Відновлення БД
```

## 🔧 Налаштування

### Environment Variables
Скопіюйте `env.example` в `.env` та налаштуйте змінні:

```bash
cp env.example .env
```

### База даних
```bash
# Створення міграцій
make migrate

# Завантаження тестових даних
make loaddata
```

### Аутентифікація
За замовчуванням використовується тестовий користувач:
- **Username**: `testuser`
- **Password**: `testpass123`

## 📊 Модулі системи

### 1. Finance System
- Управління рахунками
- Імпорт транзакцій (CSV)
- Категоризація витрат
- Бюджети та аналітика

### 2. FOP System
- Профілі ФОП
- Податкові періоди
- Розрахунки податків
- Зобов'язання

### 3. Notifications
- Email/SMS/Push повідомлення
- Налаштування каналів
- Шаблони повідомлень

### 4. Bank Integration
- Монобанк API
- ПриватБанк API
- Автоматичний імпорт транзакцій

### 5. Tax Calculations
- Автоматичний розрахунок податків
- Єдиний податок, ЄСВ, ПДВ
- Податкові пільги

### 6. Analytics
- Детальна аналітика фінансів
- Звіти та дашборди
- Тренди та прогнози

## 🚀 Production Deployment

### 1. Підготовка
```bash
# Налаштування environment
cp env.example .env
# Відредагуйте .env для production

# Збірка production образів
docker-compose -f docker-compose.prod.yml build
```

### 2. Запуск
```bash
# Запуск production
docker-compose -f docker-compose.prod.yml up -d

# Перевірка статусу
docker-compose -f docker-compose.prod.yml ps
```

### 3. Nginx (опціонально)
```bash
# Налаштування Nginx reverse proxy
cp infrastructure/nginx/nginx.conf.example infrastructure/nginx/nginx.conf
# Відредагуйте конфігурацію
```

## 🧪 Тестування

### Запуск тестів
```bash
# Всі тести
make test

# Тільки backend
make test-backend

# Тільки frontend
make test-frontend
```

### Покриття коду
```bash
# Генерація звіту покриття
docker-compose -f docker-compose.test.yml up --build
```

## 📈 Моніторинг

### Grafana Dashboards
- **System Metrics** - загальні метрики системи
- **Application Metrics** - метрики додатку
- **Database Metrics** - метрики бази даних
- **Business Metrics** - бізнес метрики

### Prometheus Targets
- Backend API: `http://backend:8000/metrics`
- Frontend: `http://frontend:3000/metrics`
- PostgreSQL: `http://postgres:5432/metrics`
- Redis: `http://redis:6379/metrics`

## 🔒 Безпека

### Production Checklist
- [ ] Змініть всі паролі за замовчуванням
- [ ] Налаштуйте SSL сертифікати
- [ ] Увімкніть MFA
- [ ] Налаштуйте брандмауер
- [ ] Регулярні резервні копії
- [ ] Моніторинг безпеки

### Environment Variables
```bash
# Обов'язково змініть в production
SECRET_KEY=your-secret-key
POSTGRES_PASSWORD=secure-password
REDIS_PASSWORD=secure-password
NEXTAUTH_SECRET=your-nextauth-secret
```

## 🤝 Розробка

### Git Workflow
```bash
# Створення feature branch
git checkout -b feature/new-feature

# Коміт змін
git add .
git commit -m "feat: add new feature"

# Push в репозиторій
git push origin feature/new-feature
```

### Code Style
```bash
# Форматування коду
make format

# Перевірка стилю
make lint
```

## 📚 Документація API

### Swagger UI
- **Development**: http://localhost:8000/api/schema/swagger-ui/
- **ReDoc**: http://localhost:8000/api/schema/redoc/

### Основні endpoints
- `GET /api/accounts/` - рахунки
- `GET /api/transactions/` - транзакції
- `GET /api/categories/` - категорії
- `GET /api/budgets/` - бюджети
- `GET /api/fop/profiles/` - ФОП профілі
- `GET /api/notifications/` - нотифікації

## 🐛 Troubleshooting

### Часті проблеми

#### 1. Порт вже використовується
```bash
# Перевірте, які процеси використовують порт
netstat -tulpn | grep :3000
# Зупиніть процес або змініть порт в docker-compose.yml
```

#### 2. Проблеми з базою даних
```bash
# Перезапуск PostgreSQL
docker-compose restart postgres

# Перевірка логів
docker-compose logs postgres
```

#### 3. Проблеми з frontend
```bash
# Очищення кешу
docker-compose exec frontend npm run build

# Перезапуск
docker-compose restart frontend
```

### Логи
```bash
# Всі сервіси
make logs

# Конкретний сервіс
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 📞 Підтримка

- **Issues**: GitHub Issues
- **Documentation**: Wiki
- **Discussions**: GitHub Discussions

## 📄 Ліцензія

MIT License - дивіться [LICENSE](LICENSE) файл для деталей.

---

**MFinance** - автоматизація обліку фінансів для ФОП та малого бізнесу в Україні 🇺🇦