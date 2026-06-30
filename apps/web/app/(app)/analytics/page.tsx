"use client";

import { DistributionChart } from "@/components/charts/distribution-chart";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAnalytics } from "@/lib/hooks/use-analytics";

export default function AnalyticsPage() {
  const { data } = useAnalytics();

  const sections = [
    { title: "Equipment by status", data: data?.equipment_status ?? {} },
    { title: "Equipment by criticality", data: data?.equipment_criticality ?? {} },
    { title: "Documents by status", data: data?.document_status ?? {} },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Analytics</h1>
        <p className="text-sm text-muted-foreground">
          Asset health, maintenance, and compliance trends across your organization.
        </p>
      </div>
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {sections.map((s) => (
          <Card key={s.title}>
            <CardHeader>
              <CardTitle className="text-base">{s.title}</CardTitle>
            </CardHeader>
            <CardContent>
              <DistributionChart data={s.data} />
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
