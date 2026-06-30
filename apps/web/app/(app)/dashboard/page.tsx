"use client";

import { Boxes, FileText, FolderKanban, Network } from "lucide-react";

import { DistributionChart } from "@/components/charts/distribution-chart";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAnalytics } from "@/lib/hooks/use-analytics";

export default function DashboardPage() {
  const { data, isLoading } = useAnalytics();

  const kpis = [
    { label: "Documents", value: data?.kpis.documents ?? 0, icon: FileText },
    { label: "Equipment", value: data?.kpis.equipment ?? 0, icon: Boxes },
    { label: "Projects", value: data?.kpis.projects ?? 0, icon: FolderKanban },
    { label: "Entities", value: data?.kpis.entities ?? 0, icon: Network },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
        <p className="text-sm text-muted-foreground">
          Overview of your industrial knowledge workspace.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {kpis.map(({ label, value, icon: Icon }) => (
          <Card key={label}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">{label}</CardTitle>
              <Icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-semibold">{isLoading ? "—" : value}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Equipment by criticality</CardTitle>
          </CardHeader>
          <CardContent>
            <DistributionChart data={data?.equipment_criticality ?? {}} />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Documents by status</CardTitle>
          </CardHeader>
          <CardContent>
            <DistributionChart data={data?.document_status ?? {}} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
