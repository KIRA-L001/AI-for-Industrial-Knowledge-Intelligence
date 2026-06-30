"use client";

import { useQuery } from "@tanstack/react-query";

import { API_BASE_URL } from "@/lib/api";
import { useAuthStore } from "@/lib/auth-store";
import { useApi } from "@/lib/hooks/use-api";

export interface ReportType {
  key: string;
  title: string;
}

export function useReportTypes() {
  const api = useApi();
  return useQuery({
    queryKey: ["report-types"],
    queryFn: () => api<ReportType[]>("/reports/types"),
  });
}

/** Download a generated PDF report as a file. */
export function useDownloadReport() {
  const token = useAuthStore((s) => s.accessToken);
  return async function download(reportType: string): Promise<void> {
    const res = await fetch(`${API_BASE_URL}/reports/generate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ report_type: reportType }),
    });
    if (!res.ok) throw new Error("Report generation failed");
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `kira-${reportType}-report.pdf`;
    a.click();
    URL.revokeObjectURL(url);
  };
}
