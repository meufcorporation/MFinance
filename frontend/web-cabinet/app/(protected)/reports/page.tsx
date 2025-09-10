"use client";

import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

interface Report {
  id: number;
  name: string;
  type: string;
  period: string;
  status: string;
  created_at: string;
  file_url?: string;
  submitted_at?: string;
}

interface ReportTemplate {
  id: number;
  name: string;
  description: string;
  type: string;
  is_available: boolean;
}

export default function ReportsPage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [reports, setReports] = useState<Report[]>([]);
  const [templates, setTemplates] = useState<ReportTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('reports');

  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/login");
    }
  }, [status, router]);

  useEffect(() => {
    if (session) {
      fetchReportsData();
    }
  }, [session]);

  const fetchReportsData = async () => {
    try {
      // Try to fetch from API first
      const [reportsResponse, templatesResponse] = await Promise.all([
        fetch(`${process.env.NEXT_PUBLIC_API_URL}/reports/`),
        fetch(`${process.env.NEXT_PUBLIC_API_URL}/reports/templates/`)
      ]);

      if (reportsResponse.ok && templatesResponse.ok) {
        const [reportsData, templatesData] = await Promise.all([
          reportsResponse.json(),
          templatesResponse.json()
        ]);

        setReports(reportsData.results || reportsData);
        setTemplates(templatesData.results || templatesData);
      } else {
        throw new Error('Failed to fetch reports data');
      }
    } catch (error) {
      console.error("Error fetching reports data:", error);
      // Fallback to mock data
      const mockReports: Report[] = [
        {
          id: 1,
          name: "Звіт за вересень 2025",
          type: "monthly",
          period: "2025-09",
          status: "completed",
          created_at: "2025-09-01T10:00:00Z",
          file_url: "/reports/september-2025.pdf",
          submitted_at: "2025-09-30T15:30:00Z"
        },
        {
          id: 2,
          name: "Звіт за серпень 2025",
          type: "monthly",
          period: "2025-08",
          status: "submitted",
          created_at: "2025-08-01T10:00:00Z",
          file_url: "/reports/august-2025.pdf",
          submitted_at: "2025-08-31T14:20:00Z"
        },
        {
          id: 3,
          name: "Квартальний звіт Q3 2025",
          type: "quarterly",
          period: "2025-Q3",
          status: "processing",
          created_at: "2025-09-15T09:00:00Z"
        },
        {
          id: 4,
          name: "Звіт за липень 2025",
          type: "monthly",
          period: "2025-07",
          status: "failed",
          created_at: "2025-07-01T10:00:00Z"
        }
      ];

      const mockTemplates: ReportTemplate[] = [
        {
          id: 1,
          name: "Місячний звіт ФОП",
          description: "Стандартний звіт про доходи та витрати за місяць",
          type: "monthly",
          is_available: true
        },
        {
          id: 2,
          name: "Квартальний звіт",
          description: "Звіт за квартал з деталізацією по категоріях",
          type: "quarterly",
          is_available: true
        },
        {
          id: 3,
          name: "Річний звіт",
          description: "Повний річний звіт з аналітикою",
          type: "yearly",
          is_available: true
        },
        {
          id: 4,
          name: "Звіт для ДПС",
          description: "Офіційний звіт для податкової служби",
          type: "tax",
          is_available: false
        }
      ];

      setReports(mockReports);
      setTemplates(mockTemplates);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'submitted':
        return 'bg-blue-100 text-blue-800';
      case 'processing':
        return 'bg-yellow-100 text-yellow-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return 'Завершено';
      case 'submitted':
        return 'Подано';
      case 'processing':
        return 'Обробляється';
      case 'failed':
        return 'Помилка';
      default:
        return status;
    }
  };

  const getTypeText = (type: string) => {
    switch (type) {
      case 'monthly':
        return 'Місячний';
      case 'quarterly':
        return 'Квартальний';
      case 'yearly':
        return 'Річний';
      case 'tax':
        return 'Податковий';
      default:
        return type;
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

  const completedReports = reports.filter(r => r.status === 'completed').length;
  const submittedReports = reports.filter(r => r.status === 'submitted').length;
  const processingReports = reports.filter(r => r.status === 'processing').length;
  const failedReports = reports.filter(r => r.status === 'failed').length;

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Звіти</h1>
          <p className="text-gray-600 mt-1">Генерація та управління фінансовими звітами</p>
        </div>
        <div className="flex space-x-2">
          <button className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors flex items-center space-x-2">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            <span>Створити звіт</span>
          </button>
          <button className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors flex items-center space-x-2">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span>Експорт всіх</span>
          </button>
        </div>
      </div>

      {/* Навігація по табах */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('reports')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'reports'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Мої звіти
          </button>
          <button
            onClick={() => setActiveTab('templates')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'templates'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Шаблони
          </button>
          <button
            onClick={() => setActiveTab('analytics')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'analytics'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Аналітика
          </button>
        </nav>
      </div>

      {/* Вкладка Мої звіти */}
      {activeTab === 'reports' && (
        <div className="space-y-6">
          {/* Статистика */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-md border">
              <div className="flex items-center">
                <div className="p-2 bg-green-100 rounded-lg">
                  <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Завершено</p>
                  <p className="text-2xl font-bold text-green-600">{completedReports}</p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md border">
              <div className="flex items-center">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Подано</p>
                  <p className="text-2xl font-bold text-blue-600">{submittedReports}</p>
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
                  <p className="text-sm font-medium text-gray-600">Обробляється</p>
                  <p className="text-2xl font-bold text-yellow-600">{processingReports}</p>
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
                  <p className="text-2xl font-bold text-red-600">{failedReports}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Список звітів */}
          <div className="bg-white rounded-lg shadow-md border">
            <div className="p-6 border-b">
              <h2 className="text-xl font-semibold">Список звітів</h2>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {reports.map((report) => (
                  <div key={report.id} className="border rounded-lg p-4 hover:bg-gray-50">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-lg font-medium text-gray-900">{report.name}</h3>
                      <div className="flex items-center space-x-2">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(report.status)}`}>
                          {getStatusText(report.status)}
                        </span>
                        <span className="text-sm text-gray-500">{getTypeText(report.type)}</span>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
                      <div>
                        <p className="text-sm text-gray-600">Період</p>
                        <p className="text-sm font-medium text-gray-900">{report.period}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Створено</p>
                        <p className="text-sm font-medium text-gray-900">
                          {new Date(report.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Подано</p>
                        <p className="text-sm font-medium text-gray-900">
                          {report.submitted_at ? new Date(report.submitted_at).toLocaleDateString() : '-'}
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      {report.file_url && (
                        <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                          📄 Завантажити PDF
                        </button>
                      )}
                      {report.status === 'completed' && (
                        <button className="text-green-600 hover:text-green-800 text-sm font-medium">
                          📤 Подати до ДПС
                        </button>
                      )}
                      {report.status === 'failed' && (
                        <button className="text-red-600 hover:text-red-800 text-sm font-medium">
                          🔄 Повторити
                        </button>
                      )}
                      <button className="text-gray-600 hover:text-gray-800 text-sm font-medium">
                        ⚙️ Налаштування
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Вкладка Шаблони */}
      {activeTab === 'templates' && (
        <div className="bg-white rounded-lg shadow-md border">
          <div className="p-6 border-b">
            <h2 className="text-xl font-semibold">Доступні шаблони звітів</h2>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {templates.map((template) => (
                <div key={template.id} className="border rounded-lg p-4 hover:bg-gray-50">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="text-lg font-medium text-gray-900">{template.name}</h3>
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                      template.is_available ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {template.is_available ? 'Доступний' : 'Недоступний'}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-4">{template.description}</p>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">{getTypeText(template.type)}</span>
                    <button 
                      disabled={!template.is_available}
                      className={`px-4 py-2 rounded-md text-sm font-medium ${
                        template.is_available
                          ? 'bg-blue-600 text-white hover:bg-blue-700'
                          : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      }`}
                    >
                      Використати
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Вкладка Аналітика */}
      {activeTab === 'analytics' && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-md border">
            <div className="p-6 border-b">
              <h2 className="text-xl font-semibold">Аналітика звітів</h2>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Статистика по типах</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Місячні звіти</span>
                      <span className="text-sm font-medium text-gray-900">
                        {reports.filter(r => r.type === 'monthly').length}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Квартальні звіти</span>
                      <span className="text-sm font-medium text-gray-900">
                        {reports.filter(r => r.type === 'quarterly').length}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Річні звіти</span>
                      <span className="text-sm font-medium text-gray-900">
                        {reports.filter(r => r.type === 'yearly').length}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Останні дії</h3>
                  <div className="space-y-3">
                    {reports.slice(0, 3).map((report) => (
                      <div key={report.id} className="flex items-center space-x-3">
                        <div className={`w-2 h-2 rounded-full ${
                          report.status === 'completed' ? 'bg-green-500' :
                          report.status === 'submitted' ? 'bg-blue-500' :
                          report.status === 'processing' ? 'bg-yellow-500' : 'bg-red-500'
                        }`}></div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900 truncate">{report.name}</p>
                          <p className="text-xs text-gray-500">
                            {new Date(report.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
