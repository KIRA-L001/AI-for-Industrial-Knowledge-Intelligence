"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

import type { TokenPair, User } from "./types";

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  setSession: (user: User, tokens: TokenPair) => void;
  setAccessToken: (token: string) => void;
  clear: () => void;
}

/** Persisted auth session (tokens + user) stored in localStorage. */
export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      setSession: (user, tokens) =>
        set({
          user,
          accessToken: tokens.access_token,
          refreshToken: tokens.refresh_token,
          isAuthenticated: true,
        }),
      setAccessToken: (token) => set({ accessToken: token }),
      clear: () =>
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
        }),
    }),
    { name: "kira-auth" },
  ),
);
