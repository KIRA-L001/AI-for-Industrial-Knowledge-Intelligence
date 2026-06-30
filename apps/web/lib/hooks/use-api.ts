"use client";

import { apiFetch, type RequestOptions } from "@/lib/api";
import { useAuthStore } from "@/lib/auth-store";

/** Returns an authed fetcher that injects the current access token. */
export function useApi() {
  const token = useAuthStore((s) => s.accessToken);
  return function authedFetch<T>(path: string, options: RequestOptions = {}) {
    return apiFetch<T>(path, { ...options, token });
  };
}

/** Standard paginated response envelope from the API. */
export interface Page<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}
