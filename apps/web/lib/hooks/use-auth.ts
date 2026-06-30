"use client";

import { useMutation } from "@tanstack/react-query";

import { apiFetch } from "@/lib/api";
import { useAuthStore } from "@/lib/auth-store";
import type { AuthResult, LoginPayload, RegisterPayload } from "@/lib/types";

/** Login mutation; on success stores the session. */
export function useLogin() {
  const setSession = useAuthStore((s) => s.setSession);
  return useMutation({
    mutationFn: (payload: LoginPayload) =>
      apiFetch<AuthResult>("/auth/login", { method: "POST", body: payload }),
    onSuccess: (data) => setSession(data.user, data.tokens),
  });
}

/** Registration mutation; on success stores the session. */
export function useRegister() {
  const setSession = useAuthStore((s) => s.setSession);
  return useMutation({
    mutationFn: (payload: RegisterPayload) =>
      apiFetch<AuthResult>("/auth/register", { method: "POST", body: payload }),
    onSuccess: (data) => setSession(data.user, data.tokens),
  });
}
