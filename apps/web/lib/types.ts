/** Shared API DTOs mirroring the backend Pydantic schemas. */

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: "viewer" | "engineer" | "admin" | "owner";
  is_active: boolean;
  organization_id: string;
  created_at: string;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface AuthResult {
  user: User;
  tokens: TokenPair;
}

export interface RegisterPayload {
  organization_name: string;
  email: string;
  full_name: string;
  password: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}
