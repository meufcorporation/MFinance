"use client";

import { useState, useEffect } from "react";
import { useSession } from "next-auth/react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { AlertCircle, CreditCard, Plus, Calendar, DollarSign, CheckCircle, XCircle, Clock, RefreshCw } from "lucide-react";

interface Payment {
  id: number;
  amount: number;
  currency: string;
  status: string;
  payment_type: string;
  description: string;
  created_at: string;
  processed_at?: string;
  provider: {
    display_name: string;
  };
  payment_method: {
    method_type: string;
    card_holder?: string;
    iban?: string;
  };
}

interface PaymentMethod {
  id: number;
  method_type: string;
  card_holder?: string;
  iban?: string;
  is_default: boolean;
  is_active: boolean;
  auto_pay_enabled: boolean;
  provider: {
    display_name: string;
  };
}

interface PaymentTemplate {
  id: number;
  name: string;
  description: string;
  amount?: number;
  payment_type: string;
  is_public: boolean;
}

export default function PaymentsPage() {
  const { data: session } = useSession();
  const [payments, setPayments] = useState<Payment[]>([]);
  const [paymentMethods, setPaymentMethods] = useState<PaymentMethod[]>([]);
  const [templates, setTemplates] = useState<PaymentTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreatePayment, setShowCreatePayment] = useState(false);
  const [showCreateMethod, setShowCreateMethod] = useState(false);

  // Форма створення платежу
  const [paymentForm, setPaymentForm] = useState({
    amount: "",
    description: "",
    payment_method_id: "",
    template_id: "",
    fop_profile_id: "1"
  });

  // Форма створення способу оплати
  const [methodForm, setMethodForm] = useState({
    method_type: "",
    provider_id: "",
    card_holder: "",
    iban: "",
    is_default: false,
    auto_pay_enabled: false
  });

  useEffect(() => {
    if (session) {
      fetchPayments();
      fetchPaymentMethods();
      fetchTemplates();
    }
  }, [session]);

  const fetchPayments = async () => {
    try {
      const response = await fetch("/api/payments/payments/", {
        headers: {
          "Authorization": `Bearer ${session?.accessToken}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setPayments(data.results || data);
      }
    } catch (error) {
      console.error("Помилка завантаження платежів:", error);
    }
  };

  const fetchPaymentMethods = async () => {
    try {
      const response = await fetch("/api/payments/methods/", {
        headers: {
          "Authorization": `Bearer ${session?.accessToken}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setPaymentMethods(data.results || data);
      }
    } catch (error) {
      console.error("Помилка завантаження способів оплати:", error);
    }
  };

  const fetchTemplates = async () => {
    try {
      const response = await fetch("/api/payments/templates/", {
        headers: {
          "Authorization": `Bearer ${session?.accessToken}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setTemplates(data.results || data);
      }
    } catch (error) {
      console.error("Помилка завантаження шаблонів:", error);
    }
  };

  const handleCreatePayment = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch("/api/payments/payments/create_from_template/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${session?.accessToken}`
        },
        body: JSON.stringify(paymentForm)
      });

      if (response.ok) {
        setShowCreatePayment(false);
        setPaymentForm({ amount: "", description: "", payment_method_id: "", template_id: "", fop_profile_id: "1" });
        fetchPayments();
      }
    } catch (error) {
      console.error("Помилка створення платежу:", error);
    }
  };

  const handleCreateMethod = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch("/api/payments/methods/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${session?.accessToken}`
        },
        body: JSON.stringify(methodForm)
      });

      if (response.ok) {
        setShowCreateMethod(false);
        setMethodForm({ method_type: "", provider_id: "", card_holder: "", iban: "", is_default: false, auto_pay_enabled: false });
        fetchPaymentMethods();
      }
    } catch (error) {
      console.error("Помилка створення способу оплати:", error);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      pending: { color: "bg-yellow-100 text-yellow-800", icon: Clock },
      processing: { color: "bg-blue-100 text-blue-800", icon: RefreshCw },
      completed: { color: "bg-green-100 text-green-800", icon: CheckCircle },
      failed: { color: "bg-red-100 text-red-800", icon: XCircle },
      cancelled: { color: "bg-gray-100 text-gray-800", icon: XCircle },
      refunded: { color: "bg-purple-100 text-purple-800", icon: RefreshCw }
    };

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.pending;
    const Icon = config.icon;

    return (
      <Badge className={config.color}>
        <Icon className="w-3 h-3 mr-1" />
        {status}
      </Badge>
    );
  };

  const getMethodTypeDisplay = (methodType: string) => {
    const types = {
      card: "Банківська карта",
      iban: "IBAN переказ",
      cash: "Готівка",
      crypto: "Криптовалюта"
    };
    return types[methodType as keyof typeof types] || methodType;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Платежі</h1>
          <p className="text-gray-600">Управління платежами та способами оплати</p>
        </div>
        <div className="flex gap-2">
          <Dialog open={showCreatePayment} onOpenChange={setShowCreatePayment}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Створити платіж
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-md">
              <DialogHeader>
                <DialogTitle>Створити платіж</DialogTitle>
                <DialogDescription>
                  Створіть новий платіж для сплати податків або інших зобов'язань
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleCreatePayment} className="space-y-4">
                <div>
                  <Label htmlFor="amount">Сума (UAH)</Label>
                  <Input
                    id="amount"
                    type="number"
                    step="0.01"
                    value={paymentForm.amount}
                    onChange={(e) => setPaymentForm({ ...paymentForm, amount: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="description">Опис</Label>
                  <Textarea
                    id="description"
                    value={paymentForm.description}
                    onChange={(e) => setPaymentForm({ ...paymentForm, description: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="payment_method">Спосіб оплати</Label>
                  <Select
                    value={paymentForm.payment_method_id}
                    onValueChange={(value) => setPaymentForm({ ...paymentForm, payment_method_id: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Оберіть спосіб оплати" />
                    </SelectTrigger>
                    <SelectContent>
                      {paymentMethods.map((method) => (
                        <SelectItem key={method.id} value={method.id.toString()}>
                          {getMethodTypeDisplay(method.method_type)} - {method.card_holder || method.iban}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <Button type="submit" className="w-full">
                  Створити платіж
                </Button>
              </form>
            </DialogContent>
          </Dialog>

          <Dialog open={showCreateMethod} onOpenChange={setShowCreateMethod}>
            <DialogTrigger asChild>
              <Button variant="outline">
                <CreditCard className="w-4 h-4 mr-2" />
                Додати спосіб оплати
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-md">
              <DialogHeader>
                <DialogTitle>Додати спосіб оплати</DialogTitle>
                <DialogDescription>
                  Додайте новий спосіб оплати для швидких платежів
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleCreateMethod} className="space-y-4">
                <div>
                  <Label htmlFor="method_type">Тип способу оплати</Label>
                  <Select
                    value={methodForm.method_type}
                    onValueChange={(value) => setMethodForm({ ...methodForm, method_type: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Оберіть тип" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="card">Банківська карта</SelectItem>
                      <SelectItem value="iban">IBAN переказ</SelectItem>
                      <SelectItem value="cash">Готівка</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                {methodForm.method_type === "card" && (
                  <div>
                    <Label htmlFor="card_holder">Власник картки</Label>
                    <Input
                      id="card_holder"
                      value={methodForm.card_holder}
                      onChange={(e) => setMethodForm({ ...methodForm, card_holder: e.target.value })}
                      placeholder="Ім'я Прізвище"
                    />
                  </div>
                )}
                {methodForm.method_type === "iban" && (
                  <div>
                    <Label htmlFor="iban">IBAN</Label>
                    <Input
                      id="iban"
                      value={methodForm.iban}
                      onChange={(e) => setMethodForm({ ...methodForm, iban: e.target.value })}
                      placeholder="UA123456789012345678901234567"
                    />
                  </div>
                )}
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="is_default"
                    checked={methodForm.is_default}
                    onChange={(e) => setMethodForm({ ...methodForm, is_default: e.target.checked })}
                  />
                  <Label htmlFor="is_default">Основний спосіб оплати</Label>
                </div>
                <Button type="submit" className="w-full">
                  Додати спосіб оплати
                </Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <Tabs defaultValue="payments" className="space-y-6">
        <TabsList>
          <TabsTrigger value="payments">Платежі</TabsTrigger>
          <TabsTrigger value="methods">Способи оплати</TabsTrigger>
          <TabsTrigger value="templates">Шаблони</TabsTrigger>
        </TabsList>

        <TabsContent value="payments">
          <Card>
            <CardHeader>
              <CardTitle>Історія платежів</CardTitle>
              <CardDescription>
                Всі ваші платежі та їх статуси
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>ID</TableHead>
                    <TableHead>Сума</TableHead>
                    <TableHead>Опис</TableHead>
                    <TableHead>Статус</TableHead>
                    <TableHead>Спосіб оплати</TableHead>
                    <TableHead>Дата створення</TableHead>
                    <TableHead>Дії</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {payments.map((payment) => (
                    <TableRow key={payment.id}>
                      <TableCell className="font-medium">#{payment.id}</TableCell>
                      <TableCell>
                        <div className="flex items-center">
                          <DollarSign className="w-4 h-4 mr-1" />
                          {payment.amount} {payment.currency}
                        </div>
                      </TableCell>
                      <TableCell>{payment.description}</TableCell>
                      <TableCell>{getStatusBadge(payment.status)}</TableCell>
                      <TableCell>
                        <div className="text-sm">
                          <div>{getMethodTypeDisplay(payment.payment_method.method_type)}</div>
                          <div className="text-gray-500">
                            {payment.payment_method.card_holder || payment.payment_method.iban}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        {new Date(payment.created_at).toLocaleDateString('uk-UA')}
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          {payment.status === 'failed' && (
                            <Button size="sm" variant="outline">
                              Повторити
                            </Button>
                          )}
                          {payment.status === 'pending' && (
                            <Button size="sm" variant="outline">
                              Скасувати
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="methods">
          <Card>
            <CardHeader>
              <CardTitle>Способи оплати</CardTitle>
              <CardDescription>
                Управління способами оплати
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {paymentMethods.map((method) => (
                  <Card key={method.id}>
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-lg">
                          {getMethodTypeDisplay(method.method_type)}
                        </CardTitle>
                        {method.is_default && (
                          <Badge variant="default">Основний</Badge>
                        )}
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        <div className="text-sm text-gray-600">
                          {method.card_holder || method.iban}
                        </div>
                        <div className="text-sm text-gray-500">
                          {method.provider.display_name}
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant={method.is_active ? "default" : "secondary"}>
                            {method.is_active ? "Активний" : "Неактивний"}
                          </Badge>
                          {method.auto_pay_enabled && (
                            <Badge variant="outline">Автооплата</Badge>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="templates">
          <Card>
            <CardHeader>
              <CardTitle>Шаблони платежів</CardTitle>
              <CardDescription>
                Готові шаблони для швидкого створення платежів
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {templates.map((template) => (
                  <Card key={template.id}>
                    <CardHeader>
                      <CardTitle className="text-lg">{template.name}</CardTitle>
                      <CardDescription>{template.description}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {template.amount && (
                          <div className="text-lg font-semibold">
                            {template.amount} UAH
                          </div>
                        )}
                        <Badge variant="outline">{template.payment_type}</Badge>
                        <Button size="sm" className="w-full">
                          Використати шаблон
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
