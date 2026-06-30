"use client";

import { Download, FileBarChart } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useDownloadReport, useReportTypes } from "@/lib/hooks/use-reports";

export default function ReportsPage() {
  const { data: types } = useReportTypes();
  const download = useDownloadReport();
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function onDownload(key: string) {
    setBusy(key);
    setError(null);
    try {
      await download(key);
    } catch {
      setError("Could not generate the report.");
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Reports</h1>
        <p className="text-sm text-muted-foreground">
          Generate and export PDF reports from your knowledge base.
        </p>
      </div>
      {error && <p className="text-sm text-destructive">{error}</p>}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {(types ?? []).map((t) => (
          <Card key={t.key}>
            <CardHeader className="flex flex-row items-center gap-3 space-y-0">
              <FileBarChart className="h-5 w-5 text-primary" />
              <CardTitle className="text-base">{t.title}</CardTitle>
            </CardHeader>
            <CardContent>
              <Button
                variant="outline"
                className="w-full"
                disabled={busy === t.key}
                onClick={() => onDownload(t.key)}
              >
                <Download className="h-4 w-4" />
                {busy === t.key ? "Generating…" : "Download PDF"}
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
