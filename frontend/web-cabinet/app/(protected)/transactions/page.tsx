"use client";
import { useMemo, useState } from "react";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { ColumnDef, useReactTable, getCoreRowModel, getFilteredRowModel, getPaginationRowModel, flexRender } from "@tanstack/react-table";
import Papa from "papaparse";
import * as XLSX from "xlsx";

type Transaction = {
  id: string;
  date: string;
  description: string;
  amount: number;
  category?: string;
};

export default function TransactionsPage() {
  const { status } = useSession();
  const router = useRouter();
  if (status === "unauthenticated") router.push("/login");

  const [globalFilter, setGlobalFilter] = useState("");
  const data = useMemo<Transaction[]>(
    () => [
      { id: "1", date: "2025-09-01", description: "Зарплата за вересень", amount: 25000, category: "Зарплата" },
      { id: "2", date: "2025-09-02", description: "Продукти в супермаркеті", amount: -1200, category: "Продукти" },
      { id: "3", date: "2025-09-03", description: "Бензин", amount: -800, category: "Транспорт" },
      { id: "4", date: "2025-09-04", description: "Кава", amount: -150, category: "Розваги" },
      { id: "5", date: "2025-09-05", description: "Депозит", amount: 10000, category: "Інвестиції" },
      { id: "6", date: "2025-09-06", description: "Оренда квартири", amount: -8000, category: "Житло" },
      { id: "7", date: "2025-09-07", description: "Інтернет", amount: -300, category: "Комунальні" },
      { id: "8", date: "2025-09-08", description: "Мобільний зв'язок", amount: -200, category: "Комунальні" },
      { id: "9", date: "2025-09-09", description: "Фриланс проект", amount: 5000, category: "Фриланс" },
      { id: "10", date: "2025-09-10", description: "Книги", amount: -500, category: "Освіта" }
    ],
    []
  );

  const columns = useMemo<ColumnDef<Transaction>[]>(
    () => [
      { 
        header: "Дата", 
        accessorKey: "date",
        cell: ({ getValue }) => new Date(getValue() as string).toLocaleDateString()
      },
      { header: "Опис", accessorKey: "description" },
      { 
        header: "Сума", 
        accessorKey: "amount",
        cell: ({ getValue }) => {
          const amount = getValue() as number;
          return (
            <span className={`font-semibold ${amount >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {amount >= 0 ? '+' : ''}{amount.toLocaleString()} UAH
            </span>
          );
        }
      },
      { header: "Категорія", accessorKey: "category" },
    ],
    []
  );

  const table = useReactTable({
    data,
    columns,
    state: { globalFilter },
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
  });

  const exportCSV = () => {
    const csv = Papa.unparse(data);
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "transactions.csv";
    a.click();
    URL.revokeObjectURL(url);
  };

  const exportExcel = () => {
    const ws = XLSX.utils.json_to_sheet(data);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Transactions");
    XLSX.writeFile(wb, "transactions.xlsx");
  };

  const totalIncome = data.filter(t => t.amount > 0).reduce((sum, t) => sum + t.amount, 0);
  const totalExpense = data.filter(t => t.amount < 0).reduce((sum, t) => sum + Math.abs(t.amount), 0);
  const balance = totalIncome - totalExpense;

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Транзакції</h1>
        <div className="flex space-x-2">
          <button 
            onClick={exportCSV} 
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
          >
            Експорт CSV
          </button>
          <button 
            onClick={exportExcel} 
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            Експорт Excel
          </button>
        </div>
      </div>

      {/* Статистика */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md border">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Доходи</p>
              <p className="text-2xl font-bold text-green-600">+{totalIncome.toLocaleString()} UAH</p>
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
              <p className="text-sm font-medium text-gray-600">Витрати</p>
              <p className="text-2xl font-bold text-red-600">-{totalExpense.toLocaleString()} UAH</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md border">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Баланс</p>
              <p className="text-2xl font-bold text-blue-600">{balance.toLocaleString()} UAH</p>
            </div>
          </div>
        </div>
      </div>

      {/* Фільтри */}
      <div className="bg-white p-6 rounded-lg shadow-md border">
        <h2 className="text-xl font-semibold mb-4">Фільтри</h2>
        <div className="flex gap-4 items-center">
          <input
            value={globalFilter ?? ""}
            onChange={(e) => setGlobalFilter(e.target.value)}
            placeholder="Пошук по опису або категорії..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Таблиця */}
      <div className="bg-white rounded-lg shadow-md border">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold">Список транзакцій ({data.length})</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              {table.getHeaderGroups().map((hg) => (
                <tr key={hg.id}>
                  {hg.headers.map((header) => (
                    <th key={header.id} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {header.isPlaceholder
                        ? null
                        : flexRender(header.column.columnDef.header, header.getContext())}
                    </th>
                  ))}
                </tr>
              ))}
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {table.getRowModel().rows.map((row) => (
                <tr key={row.id} className="hover:bg-gray-50">
                  {row.getVisibleCells().map((cell) => (
                    <td key={cell.id} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}


