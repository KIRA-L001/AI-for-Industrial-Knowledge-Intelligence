"use client";

import { useMutation, useQuery } from "@tanstack/react-query";

import { useApi } from "@/lib/hooks/use-api";

export interface Citation {
  index: number;
  chunk_id: string;
  document_id: string;
  page_number: number | null;
  text: string;
  score: number;
}

export interface ChatResponse {
  agent: string;
  answer: string;
  confidence: number;
  confidence_label: string;
  citations: Citation[];
}

export interface AgentInfo {
  key: string;
  title: string;
}

export interface ChatTurn {
  role: "user" | "assistant";
  content: string;
}

export function useAgents() {
  const api = useApi();
  return useQuery({
    queryKey: ["agents"],
    queryFn: () => api<AgentInfo[]>("/agents"),
  });
}

export function useChat() {
  const api = useApi();
  return useMutation({
    mutationFn: (body: { message: string; agent?: string | null; history: ChatTurn[] }) =>
      api<ChatResponse>("/chat", { method: "POST", body }),
  });
}
