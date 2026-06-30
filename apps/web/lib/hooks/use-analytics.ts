"use client";

import { useQuery } from "@tanstack/react-query";

import { useApi } from "@/lib/hooks/use-api";

export interface AnalyticsOverview {
  kpis: { documents: number; equipment: number; projects: number; entities: number };
  document_status: Record<string, number>;
  equipment_status: Record<string, number>;
  equipment_criticality: Record<string, number>;
}

export function useAnalytics() {
  const api = useApi();
  return useQuery({
    queryKey: ["analytics"],
    queryFn: () => api<AnalyticsOverview>("/analytics/overview"),
  });
}
