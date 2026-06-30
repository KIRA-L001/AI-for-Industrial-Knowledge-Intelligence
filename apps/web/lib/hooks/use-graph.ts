"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { useApi } from "@/lib/hooks/use-api";

export interface GraphNode {
  id: string;
  label: string;
  name: string;
  properties: Record<string, string>;
}

export interface GraphEdge {
  source: string;
  target: string;
  rel_type: string;
}

export interface GraphView {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export function useGraph() {
  const api = useApi();
  return useQuery({
    queryKey: ["graph"],
    queryFn: () => api<GraphView>("/graph"),
  });
}

export function useSyncGraph() {
  const api = useApi();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api<{ nodes: number; edges: number }>("/graph/sync", { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["graph"] }),
  });
}
