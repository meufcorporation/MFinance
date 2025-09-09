"use client";

import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

interface Account {
  id: number;
  name: string;
  bank_name: string;
  balance: string;
  currency: string;
  account_type: string;
}

interface Transaction {
  id: number;
  description: string;
  amount: string;
  transaction_type: string;
  date: string;
  category_name?: string;
}

export default function Dashboard() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/login");
    }
  }, [status, router]);

  useEffect(() => {
    if (session) {
      fetchDashboardData();
    }
  }, [session]);

  const fetchDashboardData = async () => {
    try {
      // Тут буде реальний API запит
      // const response = await fetch('/api/accounts');
      // const data = await response.json();
      
      // Поки що використовуємо мокові дані
      setAccounts([
        { id: 1, name: "Основной рахунок", bank_name: "ПриватБанк", balance: "15000.00", currency: "UAH", account_type: "checking" },
        { id: 2, name: "Депозит", bank_name: "Монобанк", balance: "50000.00", currency: "UAH", account_type: "savings" },
        { id: 3, name: "Кредитна карта", bank_name: "Ощадбанк", balance: "-5000.00", currency: "UAH", account_type: "credit" }
      ]);
      
      setTransactions([
        { id: 1, description: "Зарплата за вересень", amount: "25000.00", transaction_type: "income", date: "2025-09-01", category_name: "Зарплата" },
        { id: 2, description: "Продукти в супермаркеті", amount: "1200.00", transaction_type: "expense", date: "2025-09-02", category_name: "Продукти" },
        { id: 3, description: "Бензин", amount: "800.00", transaction_type: "expense", date: "2025-09-03", category_name: "Транспорт" }
      ]);
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
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

  const totalBalance = accounts.reduce((sum, account) => sum + parseFloat(account.balance), 0);
  const monthlyIncome = transactions
    .filter(t => t.transaction_type === "income")
    .reduce((sum, t) => sum + parseFloat(t.amount), 0);
  const monthlyExpense = transactions
    .filter(t => t.transaction_type === "expense")
    .reduce((sum, t) => sum + parseFloat(t.amount), 0);

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <div className="text-sm text-gray-600">
          Привіт, {session?.user?.name}!
        </div>
      </div>

      {/* Статистичні картки */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md border">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Загальний баланс</p>
              <p className="text-2xl font-bold text-gray-900">{totalBalance.toLocaleString()} UAH</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md border">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Доходи за місяць</p>
              <p className="text-2xl font-bold text-green-600">+{monthlyIncome.toLocaleString()} UAH</p>
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
              <p className="text-sm font-medium text-gray-600">Витрати за місяць</p>
              <p className="text-2xl font-bold text-red-600">-{monthlyExpense.toLocaleString()} UAH</p>
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
              <p className="text-sm font-medium text-gray-600">Дедлайни податків</p>
              <p className="text-2xl font-bold text-yellow-600">3</p>
            </div>
          </div>
        </div>
      </div>

      {/* Рахунки */}
      <div className="bg-white rounded-lg shadow-md border">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold">Рахунки</h2>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {accounts.map((account) => (
              <div key={account.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-blue-600 font-semibold">
                      {account.bank_name.charAt(0)}
                    </span>
                  </div>
                  <div>
                    <p className="font-medium">{account.name}</p>
                    <p className="text-sm text-gray-600">{account.bank_name}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className={`text-lg font-semibold ${parseFloat(account.balance) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {parseFloat(account.balance).toLocaleString()} {account.currency}
                  </p>
                  <p className="text-sm text-gray-600 capitalize">{account.account_type}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Останні транзакції */}
      <div className="bg-white rounded-lg shadow-md border">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold">Останні транзакції</h2>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {transactions.map((transaction) => (
              <div key={transaction.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    transaction.transaction_type === 'income' ? 'bg-green-100' : 'bg-red-100'
                  }`}>
                    <span className={`font-semibold ${
                      transaction.transaction_type === 'income' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {transaction.transaction_type === 'income' ? '+' : '-'}
                    </span>
                  </div>
                  <div>
                    <p className="font-medium">{transaction.description}</p>
                    <p className="text-sm text-gray-600">{transaction.category_name}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className={`text-lg font-semibold ${
                    transaction.transaction_type === 'income' ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {transaction.transaction_type === 'income' ? '+' : '-'}{parseFloat(transaction.amount).toLocaleString()} UAH
                  </p>
                  <p className="text-sm text-gray-600">{new Date(transaction.date).toLocaleDateString()}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}


