"use client";

import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

interface FOPProfile {
  id: number;
  first_name: string;
  last_name: string;
  middle_name: string;
  tax_number: string;
  registration_date: string;
  tax_group: string;
  tax_system: string;
  bank_name: string;
  bank_code: string;
  account_number: string;
  phone: string;
  email: string;
  address: string;
  is_active: boolean;
}

interface TaxPeriod {
  id: number;
  period_type: string;
  year: number;
  month?: number;
  quarter?: number;
  declaration_deadline: string;
  payment_deadline: string;
  declaration_submitted: boolean;
  payment_made: boolean;
  tax_amount: string;
  paid_amount: string;
}

export default function FOPPage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [profile, setProfile] = useState<FOPProfile | null>(null);
  const [taxPeriods, setTaxPeriods] = useState<TaxPeriod[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('profile');

  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/login");
    }
  }, [status, router]);

  useEffect(() => {
    if (session) {
      fetchFOPData();
    }
  }, [session]);

  const fetchFOPData = async () => {
    try {
      // Мокові дані
      const mockProfile: FOPProfile = {
        id: 1,
        first_name: "Іван",
        last_name: "Петренко",
        middle_name: "Олександрович",
        tax_number: "1234567890",
        registration_date: "2020-01-15",
        tax_group: "2",
        tax_system: "single",
        bank_name: "ПриватБанк",
        bank_code: "305299",
        account_number: "UA123456789012345678901234567",
        phone: "+380501234567",
        email: "ivan.petrenko@example.com",
        address: "м. Київ, вул. Хрещатик, 1",
        is_active: true
      };

      const mockTaxPeriods: TaxPeriod[] = [
        {
          id: 1,
          period_type: "monthly",
          year: 2025,
          month: 9,
          declaration_deadline: "2025-10-20",
          payment_deadline: "2025-10-31",
          declaration_submitted: false,
          payment_made: false,
          tax_amount: "1500.00",
          paid_amount: "0.00"
        },
        {
          id: 2,
          period_type: "monthly",
          year: 2025,
          month: 8,
          declaration_deadline: "2025-09-20",
          payment_deadline: "2025-09-30",
          declaration_submitted: true,
          payment_made: true,
          tax_amount: "1500.00",
          paid_amount: "1500.00"
        },
        {
          id: 3,
          period_type: "quarterly",
          year: 2025,
          quarter: 3,
          declaration_deadline: "2025-10-20",
          payment_deadline: "2025-10-31",
          declaration_submitted: false,
          payment_made: false,
          tax_amount: "4500.00",
          paid_amount: "0.00"
        }
      ];

      setProfile(mockProfile);
      setTaxPeriods(mockTaxPeriods);
    } catch (error) {
      console.error("Error fetching FOP data:", error);
    } finally {
      setLoading(false);
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

  const getTaxGroupText = (group: string) => {
    const groups = {
      '1': '1 група - до 300 тис. грн',
      '2': '2 група - до 1.5 млн грн',
      '3': '3 група - до 7 млн грн'
    };
    return groups[group as keyof typeof groups] || group;
  };

  const getTaxSystemText = (system: string) => {
    const systems = {
      'single': 'Єдиний податок',
      'general': 'Загальна система',
      'simplified': 'Спрощена система'
    };
    return systems[system as keyof typeof systems] || system;
  };

  const getPeriodText = (period: TaxPeriod) => {
    if (period.period_type === 'monthly') {
      return `${period.year}-${period.month!.toString().padStart(2, '0')}`;
    } else if (period.period_type === 'quarterly') {
      return `${period.year} Q${period.quarter}`;
    } else {
      return period.year.toString();
    }
  };

  const upcomingDeadlines = taxPeriods.filter(p => 
    new Date(p.payment_deadline) > new Date() && !p.payment_made
  ).sort((a, b) => new Date(a.payment_deadline).getTime() - new Date(b.payment_deadline).getTime());

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">ФОП Профіль</h1>
        <div className="flex space-x-2">
          <button className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">
            Редагувати
          </button>
          <button className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors">
            Створити звіт
          </button>
        </div>
      </div>

      {/* Навігація по табах */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('profile')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'profile'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Профіль
          </button>
          <button
            onClick={() => setActiveTab('periods')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'periods'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Податкові періоди
          </button>
          <button
            onClick={() => setActiveTab('deadlines')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'deadlines'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Дедлайни
          </button>
        </nav>
      </div>

      {/* Вкладка Профіль */}
      {activeTab === 'profile' && profile && (
        <div className="space-y-6">
          {/* Основна інформація */}
          <div className="bg-white rounded-lg shadow-md border">
            <div className="p-6 border-b">
              <h2 className="text-xl font-semibold">Основна інформація</h2>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700">ПІБ</label>
                  <p className="mt-1 text-sm text-gray-900">
                    {profile.last_name} {profile.first_name} {profile.middle_name}
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">ІПН</label>
                  <p className="mt-1 text-sm text-gray-900">{profile.tax_number}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Дата реєстрації</label>
                  <p className="mt-1 text-sm text-gray-900">
                    {new Date(profile.registration_date).toLocaleDateString()}
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Податкова група</label>
                  <p className="mt-1 text-sm text-gray-900">{getTaxGroupText(profile.tax_group)}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Система оподаткування</label>
                  <p className="mt-1 text-sm text-gray-900">{getTaxSystemText(profile.tax_system)}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Статус</label>
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                    profile.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {profile.is_active ? 'Активний' : 'Неактивний'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Банківські реквізити */}
          <div className="bg-white rounded-lg shadow-md border">
            <div className="p-6 border-b">
              <h2 className="text-xl font-semibold">Банківські реквізити</h2>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Банк</label>
                  <p className="mt-1 text-sm text-gray-900">{profile.bank_name}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">МФО</label>
                  <p className="mt-1 text-sm text-gray-900">{profile.bank_code}</p>
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700">Номер рахунку</label>
                  <p className="mt-1 text-sm text-gray-900 font-mono">{profile.account_number}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Контактна інформація */}
          <div className="bg-white rounded-lg shadow-md border">
            <div className="p-6 border-b">
              <h2 className="text-xl font-semibold">Контактна інформація</h2>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Телефон</label>
                  <p className="mt-1 text-sm text-gray-900">{profile.phone}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Email</label>
                  <p className="mt-1 text-sm text-gray-900">{profile.email}</p>
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700">Адреса</label>
                  <p className="mt-1 text-sm text-gray-900">{profile.address}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Вкладка Податкові періоди */}
      {activeTab === 'periods' && (
        <div className="bg-white rounded-lg shadow-md border">
          <div className="p-6 border-b">
            <h2 className="text-xl font-semibold">Податкові періоди</h2>
          </div>
          <div className="p-6">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Період</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Дедлайн декларації</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Дедлайн сплати</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Сума податку</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Статус</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {taxPeriods.map((period) => (
                    <tr key={period.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {getPeriodText(period)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {new Date(period.declaration_deadline).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {new Date(period.payment_deadline).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {parseFloat(period.tax_amount).toLocaleString()} UAH
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <div className="flex space-x-2">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            period.declaration_submitted ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                          }`}>
                            {period.declaration_submitted ? 'Подано' : 'Не подано'}
                          </span>
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            period.payment_made ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                          }`}>
                            {period.payment_made ? 'Сплачено' : 'Не сплачено'}
                          </span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Вкладка Дедлайни */}
      {activeTab === 'deadlines' && (
        <div className="space-y-6">
          {/* Наближуючі дедлайни */}
          <div className="bg-white rounded-lg shadow-md border">
            <div className="p-6 border-b">
              <h2 className="text-xl font-semibold">Наближуючі дедлайни</h2>
            </div>
            <div className="p-6">
              {upcomingDeadlines.length > 0 ? (
                <div className="space-y-4">
                  {upcomingDeadlines.map((period) => {
                    const daysUntilDeadline = Math.ceil(
                      (new Date(period.payment_deadline).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24)
                    );
                    return (
                      <div key={period.id} className="flex items-center justify-between p-4 border rounded-lg">
                        <div>
                          <p className="font-medium">{getPeriodText(period)}</p>
                          <p className="text-sm text-gray-600">
                            Дедлайн: {new Date(period.payment_deadline).toLocaleDateString()}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-lg font-semibold text-gray-900">
                            {parseFloat(period.tax_amount).toLocaleString()} UAH
                          </p>
                          <p className={`text-sm ${
                            daysUntilDeadline <= 7 ? 'text-red-600' : 
                            daysUntilDeadline <= 14 ? 'text-yellow-600' : 'text-gray-600'
                          }`}>
                            {daysUntilDeadline} днів залишилось
                          </p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-8">Немає наближуючих дедлайнів</p>
              )}
            </div>
          </div>

          {/* Статистика */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-md border">
              <div className="flex items-center">
                <div className="p-2 bg-yellow-100 rounded-lg">
                  <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Наближуючі дедлайни</p>
                  <p className="text-2xl font-bold text-yellow-600">{upcomingDeadlines.length}</p>
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
                  <p className="text-sm font-medium text-gray-600">Сплачено</p>
                  <p className="text-2xl font-bold text-green-600">
                    {taxPeriods.filter(p => p.payment_made).length}
                  </p>
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
                  <p className="text-sm font-medium text-gray-600">Прострочено</p>
                  <p className="text-2xl font-bold text-red-600">
                    {taxPeriods.filter(p => new Date(p.payment_deadline) < new Date() && !p.payment_made).length}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
