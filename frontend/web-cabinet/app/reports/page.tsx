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
import { AlertCircle, FileText, Plus, Download, Eye, CheckCircle, XCircle, Clock, RefreshCw, Edit, Trash2 } from "lucide-react";

interface Report {
  id: number;
  name: string;
  description: string;
  report_type: string;
  format: string;
  status: string;
  created_at: string;
  generated_at?: string;
  signed_at?: string;
  submitted_at?: string;
  template: {
    name: string;
    report_type: string;
    format: string;
  };
  fop_profile: {
    name: string;
  };
  tax_period: {
    name: string;
  };
}

interface ReportTemplate {
  id: number;
  name: string;
  description: string;
  report_type: string;
  format: string;
  version: string;
  is_public: boolean;
}

interface FOPProfile {
  id: number;
  name: string;
  fop_code: string;
  fop_group: string;
}

interface TaxPeriod {
  id: number;
  name: string;
  start_date: string;
  end_date: string;
}

export default function ReportsPage() {
  const { data: session } = useSession();
  const [reports, setReports] = useState<Report[]>([]);
  const [templates, setTemplates] = useState<ReportTemplate[]>([]);
  const [fopProfiles, setFopProfiles] = useState<FOPProfile[]>([]);
  const [taxPeriods, setTaxPeriods] = useState<TaxPeriod[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateReport, setShowCreateReport] = useState(false);

  // Форма створення звіту
  const [reportForm, setReportForm] = useState({
    template_id: "",
    fop_profile_id: "",
    tax_period_id: "",
    name: "",
    description: ""
  });

  useEffect(() => {
    if (session) {
      fetchReports();
      fetchTemplates();
      fetchFopProfiles();
      fetchTaxPeriods();
    }
  }, [session]);

  const fetchReports = async () => {
    try {
      const response = await fetch("/api/reports/reports/", {
        headers: {
          "Authorization": `Bearer ${session?.accessToken}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setReports(data.results || data);
      }
    } catch (error) {
      console.error("Помилка завантаження звітів:", error);
    }
  };

  const fetchTemplates = async () => {
    try {
      const response = await fetch("/api/reports/templates/", {
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

  const fetchFopProfiles = async () => {
    try {
      const response = await fetch("/api/fop/profiles/", {
        headers: {
          "Authorization": `Bearer ${session?.accessToken}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setFopProfiles(data.results || data);
      }
    } catch (error) {
      console.error("Помилка завантаження профілів ФОП:", error);
    }
  };

  const fetchTaxPeriods = async () => {
    try {
      const response = await fetch("/api/fop/tax-periods/", {
        headers: {
          "Authorization": `Bearer ${session?.accessToken}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setTaxPeriods(data.results || data);
      }
    } catch (error) {
      console.error("Помилка завантаження податкових періодів:", error);
    }
  };

  const handleCreateReport = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch("/api/reports/templates/create_report/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${session?.accessToken}`
        },
        body: JSON.stringify(reportForm)
      });

      if (response.ok) {
        setShowCreateReport(false);
        setReportForm({ template_id: "", fop_profile_id: "", tax_period_id: "", name: "", description: "" });
        fetchReports();
      }
    } catch (error) {
      console.error("Помилка створення звіту:", error);
    }
  };

  const handleGenerateReport = async (reportId: number) => {
    try {
      const response = await fetch(`/api/reports/reports/${reportId}/generate/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${session?.accessToken}`
        },
        body: JSON.stringify({})
      });

      if (response.ok) {
        fetchReports();
      }
    } catch (error) {
      console.error("Помилка генерації звіту:", error);
    }
  };

  const handleDownloadReport = async (reportId: number) => {
    try {
      const response = await fetch(`/api/reports/reports/${reportId}/download/`, {
        headers: {
          "Authorization": `Bearer ${session?.accessToken}`
        }
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `report_${reportId}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error("Помилка завантаження звіту:", error);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      draft: { color: "bg-gray-100 text-gray-800", icon: Edit },
      generating: { color: "bg-blue-100 text-blue-800", icon: RefreshCw },
      ready: { color: "bg-green-100 text-green-800", icon: CheckCircle },
      signed: { color: "bg-purple-100 text-purple-800", icon: CheckCircle },
      submitted: { color: "bg-indigo-100 text-indigo-800", icon: CheckCircle },
      rejected: { color: "bg-red-100 text-red-800", icon: XCircle },
      error: { color: "bg-red-100 text-red-800", icon: XCircle }
    };

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.draft;
    const Icon = config.icon;

    return (
      <Badge className={config.color}>
        <Icon className="w-3 h-3 mr-1" />
        {status}
      </Badge>
    );
  };

  const getReportTypeDisplay = (reportType: string) => {
    const types = {
      single_tax: 'Єдиний податок (ЄП)',
      social_contribution: 'Єдиний соціальний внесок (ЄСВ)',
      vat: 'Податок на додану вартість (ПДВ)',
      income_tax: 'Податок на доходи фізичних осіб',
      custom: 'Користувацький звіт'
    };
    return types[reportType as keyof typeof types] || reportType;
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
          <h1 className="text-3xl font-bold text-gray-900">Звіти</h1>
          <p className="text-gray-600">Генерація та управління податковими звітами</p>
        </div>
        <Dialog open={showCreateReport} onOpenChange={setShowCreateReport}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Створити звіт
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle>Створити звіт</DialogTitle>
              <DialogDescription>
                Створіть новий звіт на основі шаблону
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleCreateReport} className="space-y-4">
              <div>
                <Label htmlFor="template">Шаблон звіту</Label>
                <Select
                  value={reportForm.template_id}
                  onValueChange={(value) => setReportForm({ ...reportForm, template_id: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Оберіть шаблон" />
                  </SelectTrigger>
                  <SelectContent>
                    {templates.map((template) => (
                      <SelectItem key={template.id} value={template.id.toString()}>
                        {template.name} ({template.format.toUpperCase()})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="fop_profile">Профіль ФОП</Label>
                <Select
                  value={reportForm.fop_profile_id}
                  onValueChange={(value) => setReportForm({ ...reportForm, fop_profile_id: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Оберіть профіль ФОП" />
                  </SelectTrigger>
                  <SelectContent>
                    {fopProfiles.map((profile) => (
                      <SelectItem key={profile.id} value={profile.id.toString()}>
                        {profile.name} ({profile.fop_code})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="tax_period">Податковий період</Label>
                <Select
                  value={reportForm.tax_period_id}
                  onValueChange={(value) => setReportForm({ ...reportForm, tax_period_id: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Оберіть період" />
                  </SelectTrigger>
                  <SelectContent>
                    {taxPeriods.map((period) => (
                      <SelectItem key={period.id} value={period.id.toString()}>
                        {period.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="name">Назва звіту</Label>
                <Input
                  id="name"
                  value={reportForm.name}
                  onChange={(e) => setReportForm({ ...reportForm, name: e.target.value })}
                  required
                />
              </div>
              <div>
                <Label htmlFor="description">Опис</Label>
                <Textarea
                  id="description"
                  value={reportForm.description}
                  onChange={(e) => setReportForm({ ...reportForm, description: e.target.value })}
                />
              </div>
              <Button type="submit" className="w-full">
                Створити звіт
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Tabs defaultValue="reports" className="space-y-6">
        <TabsList>
          <TabsTrigger value="reports">Звіти</TabsTrigger>
          <TabsTrigger value="templates">Шаблони</TabsTrigger>
        </TabsList>

        <TabsContent value="reports">
          <Card>
            <CardHeader>
              <CardTitle>Мої звіти</CardTitle>
              <CardDescription>
                Всі створені звіти та їх статуси
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>ID</TableHead>
                    <TableHead>Назва</TableHead>
                    <TableHead>Тип</TableHead>
                    <TableHead>Формат</TableHead>
                    <TableHead>Статус</TableHead>
                    <TableHead>Профіль ФОП</TableHead>
                    <TableHead>Період</TableHead>
                    <TableHead>Створено</TableHead>
                    <TableHead>Дії</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {reports.map((report) => (
                    <TableRow key={report.id}>
                      <TableCell className="font-medium">#{report.id}</TableCell>
                      <TableCell>
                        <div>
                          <div className="font-medium">{report.name}</div>
                          {report.description && (
                            <div className="text-sm text-gray-500">{report.description}</div>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>{getReportTypeDisplay(report.report_type)}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{report.format.toUpperCase()}</Badge>
                      </TableCell>
                      <TableCell>{getStatusBadge(report.status)}</TableCell>
                      <TableCell>{report.fop_profile.name}</TableCell>
                      <TableCell>{report.tax_period.name}</TableCell>
                      <TableCell>
                        {new Date(report.created_at).toLocaleDateString('uk-UA')}
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          {report.status === 'draft' && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleGenerateReport(report.id)}
                            >
                              <RefreshCw className="w-3 h-3 mr-1" />
                              Генерувати
                            </Button>
                          )}
                          {report.status === 'ready' && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleDownloadReport(report.id)}
                            >
                              <Download className="w-3 h-3 mr-1" />
                              Завантажити
                            </Button>
                          )}
                          <Button size="sm" variant="outline">
                            <Eye className="w-3 h-3 mr-1" />
                            Переглянути
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="templates">
          <Card>
            <CardHeader>
              <CardTitle>Шаблони звітів</CardTitle>
              <CardDescription>
                Доступні шаблони для створення звітів
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
                        <div className="flex items-center gap-2">
                          <Badge variant="outline">{template.report_type}</Badge>
                          <Badge variant="secondary">{template.format.toUpperCase()}</Badge>
                        </div>
                        <div className="text-sm text-gray-500">
                          Версія: {template.version}
                        </div>
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
