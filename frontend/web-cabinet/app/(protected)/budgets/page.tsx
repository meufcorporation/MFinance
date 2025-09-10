"use client";

import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

interface Budget {
  id: number;
  name: string;
  category: string;
  amount: number;
  spent: number;
  period: string;
  start_date: string;
  end_date: string;
  is_active: boolean;
}

interface BudgetCategory {
  id: number;
  name: string;
  total_budget: number;
  total_spent: number;
  percentage: number;
}

interface BudgetStats {
  total_budget: number;
  total_spent: number;
  remaining: number;
  spent_percentage: number;
  active_budgets: number;
  over_budget: number;
}

export default function BudgetsPage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [categories, setCategories] = useState<BudgetCategory[]>([]);
  const [stats, setStats] = useState<BudgetStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/login");
    }
  }, [status, router]);

  useEffect(() => {
    if (session) {
      fetchBudgetsData();
    }
  }, [session]);

  const fetchBudgetsData = async () => {
    try {
      // Try to fetch from API first
      const [budgetsResponse, categoriesResponse, statsResponse] = await Promise.all([
        fetch(`${process.env.NEXT_PUBLIC_API_URL}/finance/budgets/`),
        fetch(`${process.env.NEXT_PUBLIC_API_URL}/finance/categories/`),
        fetch(`${process.env.NEXT_PUBLIC_API_URL}/finance/budget-stats/`)
      ]);

      if (budgetsResponse.ok && categoriesResponse.ok && statsResponse.ok) {
        const [budgetsData, categoriesData, statsData] = await Promise.all([
          budgetsResponse.json(),
          categoriesResponse.json(),
          statsResponse.json()
        ]);

        setBudgets(budgetsData.results || budgetsData);
        setCategories(categoriesData.results || categoriesData);
        setStats(statsData);
      } else {
        throw new Error('Failed to fetch budget data');
      }
    } catch (error) {
      console.error("Error fetching budget data:", error);
      // Fallback to mock data
      const mockBudgets: Budget[] = [
        {
          id: 1,
          name: "Продукти",
          category: "Продукти",
          amount: 5000,
          spent: 3200,
          period: "monthly",
          start_date: "2025-09-01",
          end_date: "2025-09-30",
          is_active: true
        },
        {
          id: 2,
          name: "Транспорт",
          category: "Транспорт",
          amount: 2000,
          spent: 1500,
          period: "monthly",
          start_date: "2025-09-01",
          end_date: "2025-09-30",
          is_active: true
        },
        {
          id: 3,
          name: "Розваги",
          category: "Розваги",
          amount: 1000,
          spent: 800,
          period: "monthly",
          start_date: "2025-09-01",
          end_date: "2025-09-30",
          is_active: true
        },
        {
          id: 4,
          name: "Комунальні",
          category: "Комунальні",
          amount: 3000,
          spent: 2500,
          period: "monthly",
          start_date: "2025-09-01",
          end_date: "2025-09-30",
          is_active: true
        },
        {
          id: 5,
          name: "Освіта",
          category: "Освіта",
          amount: 2000,
          spent: 500,
          period: "monthly",
          start_date: "2025-09-01",
          end_date: "2025-09-30",
          is_active: true
        }
      ];

      const mockCategories: BudgetCategory[] = [
        { id: 1, name: "Продукти", total_budget: 5000, total_spent: 3200, percentage: 64 },
        { id: 2, name: "Транспорт", total_budget: 2000, total_spent: 1500, percentage: 75 },
        { id: 3, name: "Розваги", total_budget: 1000, total_spent: 800, percentage: 80 },
        { id: 4, name: "Комунальні", total_budget: 3000, total_spent: 2500, percentage: 83 },
        { id: 5, name: "Освіта", total_budget: 2000, total_spent: 500, percentage: 25 }
      ];

      const mockStats: BudgetStats = {
        total_budget: 13000,
        total_spent: 8500,
        remaining: 4500,
        spent_percentage: 65.4,
        active_budgets: 5,
        over_budget: 1
      };

      setBudgets(mockBudgets);
      setCategories(mockCategories);
      setStats(mockStats);
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

  const getStatusColor = (percentage: number) => {
    if (percentage >= 90) return 'text-red-600 bg-red-100';
    if (percentage >= 75) return 'text-yellow-600 bg-yellow-100';
    return 'text-green-600 bg-green-100';
  };

  const getStatusText = (percentage: number) => {
    if (percentage >= 90) return 'Перевищено';
    if (percentage >= 75) return 'Майже вичерпано';
    return 'В межах бюджету';
  };

  const getPeriodText = (period: string) => {
    switch (period) {
      case 'monthly': return 'Щомісячно';
      case 'weekly': return 'Щотижня';
      case 'yearly': return 'Щорічно';
      default: return period;
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Бюджети</h1>
          <p className="text-gray-600 mt-1">Управління та аналіз ваших бюджетів</p>
        </div>
        <div className="flex space-x-2">
          <button 
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors flex items-center space-x-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            <span>Створити бюджет</span>
          </button>
          <button className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors flex items-center space-x-2">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <span>Аналітика</span>
          </button>
        </div>
      </div>

      {/* Навігація по табах */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('overview')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'overview'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Огляд
          </button>
          <button
            onClick={() => setActiveTab('budgets')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'budgets'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Бюджети
          </button>
          <button
            onClick={() => setActiveTab('categories')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'categories'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            По категоріях
          </button>
        </nav>
      </div>

      {/* Вкладка Огляд */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Загальна статистика */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-md border">
              <div className="flex items-center">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Загальний бюджет</p>
                  <p className="text-2xl font-bold text-blue-600">{stats?.total_budget.toLocaleString()} UAH</p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md border">
              <div className="flex items-center">
                <div className="p-2 bg-red-100 rounded-lg">
                  <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Витрачено</p>
                  <p className="text-2xl font-bold text-red-600">{stats?.total_spent.toLocaleString()} UAH</p>
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
                  <p className="text-sm font-medium text-gray-600">Залишок</p>
                  <p className="text-2xl font-bold text-green-600">{stats?.remaining.toLocaleString()} UAH</p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md border">
              <div className="flex items-center">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Використано</p>
                  <p className="text-2xl font-bold text-purple-600">{stats?.spent_percentage.toFixed(1)}%</p>
                </div>
              </div>
            </div>
          </div>

          {/* Прогрес бар */}
          <div className="bg-white p-6 rounded-lg shadow-md border">
            <h2 className="text-xl font-semibold mb-4">Загальний прогрес бюджету</h2>
            <div className="space-y-4">
              <div className="flex justify-between text-sm text-gray-600">
                <span>Витрачено: {stats?.total_spent.toLocaleString()} UAH</span>
                <span>Бюджет: {stats?.total_budget.toLocaleString()} UAH</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className={`h-3 rounded-full transition-all duration-300 ${
                    (stats?.spent_percentage || 0) >= 90 ? 'bg-red-500' :
                    (stats?.spent_percentage || 0) >= 75 ? 'bg-yellow-500' : 'bg-green-500'
                  }`}
                  style={{ width: `${Math.min(stats?.spent_percentage || 0, 100)}%` }}
                ></div>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">0%</span>
                <span className="text-gray-600">50%</span>
                <span className="text-gray-600">100%</span>
              </div>
            </div>
          </div>

          {/* Топ категорії */}
          <div className="bg-white rounded-lg shadow-md border">
            <div className="p-6 border-b">
              <h2 className="text-xl font-semibold">Топ категорії за витратами</h2>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {categories
                  .sort((a, b) => b.total_spent - a.total_spent)
                  .slice(0, 5)
                  .map((category) => (
                    <div key={category.id} className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex justify-between text-sm font-medium text-gray-900">
                          <span>{category.name}</span>
                          <span>{category.total_spent.toLocaleString()} UAH</span>
                        </div>
                        <div className="mt-1 flex justify-between text-sm text-gray-500">
                          <span>Бюджет: {category.total_budget.toLocaleString()} UAH</span>
                          <span>{category.percentage}%</span>
                        </div>
                        <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${
                              category.percentage >= 90 ? 'bg-red-500' :
                              category.percentage >= 75 ? 'bg-yellow-500' : 'bg-green-500'
                            }`}
                            style={{ width: `${Math.min(category.percentage, 100)}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Вкладка Бюджети */}
      {activeTab === 'budgets' && (
        <div className="bg-white rounded-lg shadow-md border">
          <div className="p-6 border-b">
            <h2 className="text-xl font-semibold">Список бюджетів</h2>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {budgets.map((budget) => {
                const percentage = (budget.spent / budget.amount) * 100;
                const remaining = budget.amount - budget.spent;
                
                return (
                  <div key={budget.id} className="border rounded-lg p-4 hover:bg-gray-50">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-lg font-medium text-gray-900">{budget.name}</h3>
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(percentage)}`}>
                        {getStatusText(percentage)}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
                      <div>
                        <p className="text-sm text-gray-600">Бюджет</p>
                        <p className="text-lg font-semibold text-blue-600">{budget.amount.toLocaleString()} UAH</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Витрачено</p>
                        <p className="text-lg font-semibold text-red-600">{budget.spent.toLocaleString()} UAH</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Залишок</p>
                        <p className={`text-lg font-semibold ${remaining >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {remaining.toLocaleString()} UAH
                        </p>
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm text-gray-600">
                        <span>{percentage.toFixed(1)}% використано</span>
                        <span>{budget.spent.toLocaleString()} / {budget.amount.toLocaleString()} UAH</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full transition-all duration-300 ${
                            percentage >= 90 ? 'bg-red-500' :
                            percentage >= 75 ? 'bg-yellow-500' : 'bg-green-500'
                          }`}
                          style={{ width: `${Math.min(percentage, 100)}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Вкладка По категоріях */}
      {activeTab === 'categories' && (
        <div className="bg-white rounded-lg shadow-md border">
          <div className="p-6 border-b">
            <h2 className="text-xl font-semibold">Бюджети по категоріях</h2>
          </div>
          <div className="p-6">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Категорія</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Бюджет</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Витрачено</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Залишок</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Прогрес</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Статус</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {categories.map((category) => {
                    const remaining = category.total_budget - category.total_spent;
                    return (
                      <tr key={category.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {category.name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {category.total_budget.toLocaleString()} UAH
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {category.total_spent.toLocaleString()} UAH
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <span className={remaining >= 0 ? 'text-green-600' : 'text-red-600'}>
                            {remaining.toLocaleString()} UAH
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          <div className="flex items-center">
                            <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                              <div
                                className={`h-2 rounded-full ${
                                  category.percentage >= 90 ? 'bg-red-500' :
                                  category.percentage >= 75 ? 'bg-yellow-500' : 'bg-green-500'
                                }`}
                                style={{ width: `${Math.min(category.percentage, 100)}%` }}
                              ></div>
                            </div>
                            <span className="text-xs text-gray-500">{category.percentage}%</span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(category.percentage)}`}>
                            {getStatusText(category.percentage)}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Модальне вікно створення бюджету */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Створити новий бюджет</h3>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <form className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Назва бюджету</label>
                  <input
                    type="text"
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Наприклад: Продукти"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">Категорія</label>
                  <select className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500">
                    <option>Продукти</option>
                    <option>Транспорт</option>
                    <option>Розваги</option>
                    <option>Комунальні</option>
                    <option>Освіта</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">Сума бюджету</label>
                  <input
                    type="number"
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="5000"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">Період</label>
                  <select className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500">
                    <option value="monthly">Щомісячно</option>
                    <option value="weekly">Щотижня</option>
                    <option value="yearly">Щорічно</option>
                  </select>
                </div>
                
                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
                  >
                    Скасувати
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    Створити
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
