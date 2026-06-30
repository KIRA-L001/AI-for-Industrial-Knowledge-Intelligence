"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { API_BASE_URL, ApiError, type ApiErrorBody } from "@/lib/api";
import { useAuthStore } from "@/lib/auth-store";
import { useApi, type Page } from "@/lib/hooks/use-api";

export interface DocumentRecord {
  id: string;
  filename: string;
  content_type: string;
  size_bytes: number;
  status: string;
  page_count: number | null;
  created_at: string;
}

export function useDocuments() {
  const api = useApi();
  return useQuery({
    queryKey: ["documents"],
    queryFn: () => api<Page<DocumentRecord>>("/documents"),
  });
}

/** Upload a file via multipart/form-data (fetch directly to set the body). */
export function useUploadDocument() {
  const token = useAuthStore((s) => s.accessToken);
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (file: File) => {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch(`${API_BASE_URL}/documents/upload`, {
        method: "POST",
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
        body: form,
      });
      if (!res.ok) {
        const body = (await res.json().catch(() => null)) as { error?: ApiErrorBody } | null;
        throw new ApiError(res.status, body?.error ?? { code: "unknown", message: res.statusText });
      }
      return (await res.json()) as DocumentRecord;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["documents"] }),
  });
}
