"use client";

import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

interface Notification {
  id: number;
  subject: string;
  body: string;
  channel: string;
  priority: string;
  status: string;
  created_at: string;
  sent_at?: string;
  delivered_at?: string;
}

interface NotificationPreference {
  email_enabled: boolean;
  sms_enabled: boolean;
  push_enabled: boolean;
  telegram_enabled: boolean;
  tax_deadline_enabled: boolean;
  payment_reminder_enabled: boolean;
  report_enabled: boolean;
  system_alert_enabled: boolean;
  daily_digest: boolean;
  weekly_digest: boolean;
  monthly_digest: boolean;
}

export default function NotificationsPage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [preferences, setPreferences] = useState<NotificationPreference | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('notifications');

  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/login");
    }
  }, [status, router]);

  useEffect(() => {
    if (session) {
      fetchNotificationsData();
    }
  }, [session]);

  const fetchNotificationsData = async () => {
    try {
      // Мокові дані для нотифікацій
      const mockNotifications: Notification[] = [
        {
          id: 1,
          subject: "Нагадування про дедлайн податку",
          body: "До сплати єдиного податку за вересень 2025 залишилось 5 днів. Сума до сплати: 1,500 UAH",
          channel: "email",
          priority: "high",
          status: "delivered",
          created_at: "2025-09-05T10:00:00Z",
          sent_at: "2025-09-05T10:00:00Z",
          delivered_at: "2025-09-05T10:01:00Z"
        },
        {
          id: 2,
          subject: "Тижневий звіт",
          body: "Ваш тижневий звіт готовий. Доходи: 25,000 UAH, Витрати: 12,000 UAH",
          channel: "push",
          priority: "normal",
          status: "delivered",
          created_at: "2025-09-08T09:00:00Z",
          sent_at: "2025-09-08T09:00:00Z",
          delivered_at: "2025-09-08T09:00:00Z"
        },
        {
          id: 3,
          subject: "Помилка синхронізації з банком",
          body: "Не вдалося синхронізувати дані з ПриватБанк. Спробуйте пізніше.",
          channel: "email",
          priority: "urgent",
          status: "failed",
          created_at: "2025-09-09T14:30:00Z",
          sent_at: "2025-09-09T14:30:00Z"
        },
        {
          id: 4,
          subject: "Нова транзакція",
          body: "На ваш рахунок надійшов платіж на суму 5,000 UAH",
          channel: "push",
          priority: "normal",
          status: "pending",
          created_at: "2025-09-10T15:45:00Z"
        }
      ];

      // Мокові дані для налаштувань
      const mockPreferences: NotificationPreference = {
        email_enabled: true,
        sms_enabled: false,
        push_enabled: true,
        telegram_enabled: false,
        tax_deadline_enabled: true,
        payment_reminder_enabled: true,
        report_enabled: true,
        system_alert_enabled: true,
        daily_digest: false,
        weekly_digest: true,
        monthly_digest: true
      };

      setNotifications(mockNotifications);
      setPreferences(mockPreferences);
    } catch (error) {
      console.error("Error fetching notifications data:", error);
    } finally {
      setLoading(false);
    }
  };

  const getChannelIcon = (channel: string) => {
    switch (channel) {
      case 'email':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        );
      case 'push':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-5 5v-5zM4 19h6v-6H4v6zM4 5h6V1H4v4zM15 7h5l-5-5v5z" />
          </svg>
        );
      case 'sms':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        );
      case 'telegram':
        return (
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
          </svg>
        );
      default:
        return null;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return 'bg-red-100 text-red-800';
      case 'high':
        return 'bg-orange-100 text-orange-800';
      case 'normal':
        return 'bg-blue-100 text-blue-800';
      case 'low':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'delivered':
        return 'bg-green-100 text-green-800';
      case 'sent':
        return 'bg-blue-100 text-blue-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'delivered':
        return 'Доставлено';
      case 'sent':
        return 'Відправлено';
      case 'pending':
        return 'Очікує';
      case 'failed':
        return 'Помилка';
      default:
        return status;
    }
  };

  const getPriorityText = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return 'Терміновий';
      case 'high':
        return 'Високий';
      case 'normal':
        return 'Звичайний';
      case 'low':
        return 'Низький';
      default:
        return priority;
    }
  };

  if (status === "loading" || loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (status === "unauthenticated") {
    return null;
  }

  const unreadCount = notifications.filter(n => n.status === 'pending').length;
  const deliveredCount = notifications.filter(n => n.status === 'delivered').length;
  const failedCount = notifications.filter(n => n.status === 'failed').length;

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Нотифікації</h1>
        <div className="flex space-x-2">
          <button className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">
            Налаштування
          </button>
          <button className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors">
            Тестовий лист
          </button>
        </div>
      </div>

      {/* Навігація по табах */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('notifications')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'notifications'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Нотифікації ({notifications.length})
          </button>
          <button
            onClick={() => setActiveTab('preferences')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'preferences'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Налаштування
          </button>
        </nav>
      </div>

      {/* Вкладка Нотифікації */}
      {activeTab === 'notifications' && (
        <div className="space-y-6">
          {/* Статистика */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-md border">
              <div className="flex items-center">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-5 5v-5zM4 19h6v-6H4v6zM4 5h6V1H4v4zM15 7h5l-5-5v5z" />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Всього</p>
                  <p className="text-2xl font-bold text-blue-600">{notifications.length}</p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md border">
              <div className="flex items-center">
                <div className="p-2 bg-yellow-100 rounded-lg">
                  <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Очікують</p>
                  <p className="text-2xl font-bold text-yellow-600">{unreadCount}</p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md border">
              <div className="flex items-center">
                <div className="p-2 bg-green-100 rounded-lg">
                  <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Доставлено</p>
                  <p className="text-2xl font-bold text-green-600">{deliveredCount}</p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md border">
              <div className="flex items-center">
                <div className="p-2 bg-red-100 rounded-lg">
                  <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Помилки</p>
                  <p className="text-2xl font-bold text-red-600">{failedCount}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Список нотифікацій */}
          <div className="bg-white rounded-lg shadow-md border">
            <div className="p-6 border-b">
              <h2 className="text-xl font-semibold">Список нотифікацій</h2>
            </div>
            <div className="divide-y divide-gray-200">
              {notifications.map((notification) => (
                <div key={notification.id} className="p-6 hover:bg-gray-50">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                          {getChannelIcon(notification.channel)}
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2 mb-1">
                          <h3 className="text-sm font-medium text-gray-900">
                            {notification.subject}
                          </h3>
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getPriorityColor(notification.priority)}`}>
                            {getPriorityText(notification.priority)}
                          </span>
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(notification.status)}`}>
                            {getStatusText(notification.status)}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">
                          {notification.body}
                        </p>
                        <div className="flex items-center space-x-4 text-xs text-gray-500">
                          <span>Створено: {new Date(notification.created_at).toLocaleString()}</span>
                          {notification.sent_at && (
                            <span>Відправлено: {new Date(notification.sent_at).toLocaleString()}</span>
                          )}
                          {notification.delivered_at && (
                            <span>Доставлено: {new Date(notification.delivered_at).toLocaleString()}</span>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {notification.status === 'failed' && (
                        <button className="text-red-600 hover:text-red-800 text-sm font-medium">
                          Повторити
                        </button>
                      )}
                      {notification.status === 'pending' && (
                        <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                          Відправити зараз
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Вкладка Налаштування */}
      {activeTab === 'preferences' && preferences && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-md border">
            <div className="p-6 border-b">
              <h2 className="text-xl font-semibold">Налаштування нотифікацій</h2>
            </div>
            <div className="p-6 space-y-6">
              {/* Канали нотифікацій */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Канали нотифікацій</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={preferences.email_enabled}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">Email</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={preferences.sms_enabled}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">SMS</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={preferences.push_enabled}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">Push-сповіщення</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={preferences.telegram_enabled}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">Telegram</span>
                  </label>
                </div>
              </div>

              {/* Типи нотифікацій */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Типи нотифікацій</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={preferences.tax_deadline_enabled}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">Дедлайни податків</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={preferences.payment_reminder_enabled}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">Нагадування про платежі</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={preferences.report_enabled}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">Звіти</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={preferences.system_alert_enabled}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">Системні сповіщення</span>
                  </label>
                </div>
              </div>

              {/* Дайджести */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Дайджести</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={preferences.daily_digest}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">Щоденний дайджест</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={preferences.weekly_digest}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">Тижневий дайджест</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={preferences.monthly_digest}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">Місячний дайджест</span>
                  </label>
                </div>
              </div>

              <div className="pt-4">
                <button className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">
                  Зберегти налаштування
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
