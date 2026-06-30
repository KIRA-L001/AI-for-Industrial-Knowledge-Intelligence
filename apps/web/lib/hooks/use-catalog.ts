"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { useApi, type Page } from "@/lib/hooks/use-api";

export interface Equipment {
  id: string;
  tag: string;
  name: string;
  equipment_type: string | null;
  status: string;
  criticality: string;
}

export interface Project {
  id: string;
  name: string;
  description: string | null;
  status: string;
  created_at: string;
}

export function useEquipment() {
  const api = useApi();
  return useQuery({
    queryKey: ["equipment"],
    queryFn: () => api<Page<Equipment>>("/equipment"),
  });
}

export function useCreateEquipment() {
  const api = useApi();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: { tag: string; name: string; criticality?: string }) =>
      api<Equipment>("/equipment", { method: "POST", body }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["equipment"] }),
  });
}

export function useProjects() {
  const api = useApi();
  return useQuery({
    queryKey: ["projects"],
    queryFn: () => api<Page<Project>>("/projects"),
  });
}

export function useCreateProject() {
  const api = useApi();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: { name: string; description?: string }) =>
      api<Project>("/projects", { method: "POST", body }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["projects"] }),
  });
}
