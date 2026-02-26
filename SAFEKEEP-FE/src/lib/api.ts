import axios from "axios";

// API base URL is configured via Vite env: VITE_API_BASE_URL
// Fallback to https://127.0.0.1:8080 if not set.
export const API_BASE_URL =
  (import.meta as any).env?.VITE_API_BASE_URL ?? "https://127.0.0.1:8080";

export const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: false,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export async function login(email: string, password: string): Promise<AuthResponse> {
  const body = new URLSearchParams();
  body.append("username", email);
  body.append("password", password);

  const { data } = await api.post<AuthResponse>("/auth/login", body, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  return data;
}

export async function register(email: string, password: string) {
  const { data } = await api.post("/auth/register", { email, password });
  return data;
}

export interface Timer {
  user_id: string;
  status: "ACTIVE" | "TRIGGERED";
  timeout_days: number;
  last_checkin: string;
  deadline: string;
}

export async function getTimer(): Promise<Timer> {
  const { data } = await api.get<Timer>("/timer");
  return data;
}

export async function updateTimer(timeout_days: number): Promise<Timer> {
  const { data } = await api.put<Timer>("/timer", { timeout_days });
  return data;
}

export interface HeartbeatResponse {
  message: string;
  last_checkin: string;
  deadline: string;
}

export async function sendHeartbeat(): Promise<HeartbeatResponse> {
  const { data } = await api.post<HeartbeatResponse>("/heartbeat");
  return data;
}

export interface Vault {
  id: string;
  user_id: string;
  name: string;
  encrypted_data: string | null;
  client_salt: string | null;
}

export interface VaultPayload {
  name: string;
  encrypted_data?: string | null;
  client_salt?: string | null;
}

export async function listVaults(): Promise<Vault[]> {
  const { data } = await api.get<Vault[]>("/vaults");
  return data;
}

export async function createVault(payload: VaultPayload): Promise<Vault> {
  const { data } = await api.post<Vault>("/vaults", payload);
  return data;
}

export async function updateVault(id: string, payload: Partial<VaultPayload>): Promise<Vault> {
  const { data } = await api.put<Vault>(`/vaults/${id}`, payload);
  return data;
}

export async function deleteVault(id: string): Promise<void> {
  await api.delete(`/vaults/${id}`);
}

export interface Beneficiary {
  id: string;
  user_id: string;
  email: string;
  name: string;
}

export interface BeneficiaryPayload {
  email: string;
  name: string;
}

export interface BeneficiaryUpdatePayload {
  email?: string;
  name?: string;
}

export async function listBeneficiaries(): Promise<Beneficiary[]> {
  const { data } = await api.get<Beneficiary[]>("/beneficiaries");
  return data;
}

export async function createBeneficiary(payload: BeneficiaryPayload): Promise<Beneficiary> {
  const { data } = await api.post<Beneficiary>("/beneficiaries", payload);
  return data;
}

export async function updateBeneficiary(
  id: string,
  payload: BeneficiaryUpdatePayload,
): Promise<Beneficiary> {
  const { data } = await api.put<Beneficiary>(`/beneficiaries/${id}`, payload);
  return data;
}

export async function deleteBeneficiary(id: string): Promise<void> {
  await api.delete(`/beneficiaries/${id}`);
}

