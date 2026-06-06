import type { AgentChatResponse, BusinessProfile, RagPreview } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8001";

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || `Erreur API ${res.status}`);
  }

  return res.json() as Promise<T>;
}

export function getApiUrl(): string {
  return API_URL;
}

export async function fetchBusiness(slug: string): Promise<BusinessProfile> {
  return apiFetch<BusinessProfile>(`/api/agents/business/${slug}`);
}

export async function fetchRagPreview(
  slug: string,
  intent: string
): Promise<RagPreview> {
  return apiFetch<RagPreview>(
    `/api/agents/business/${slug}/rag-preview?intent=${encodeURIComponent(intent)}`
  );
}

export async function sendChatMessage(payload: {
  business_slug: string;
  message: string;
  conversation_id?: string;
}): Promise<AgentChatResponse> {
  return apiFetch<AgentChatResponse>("/api/agents/chat", {
    method: "POST",
    body: JSON.stringify({
      channel: "web",
      ...payload,
    }),
  });
}

export async function fetchHealth(): Promise<{ status: string; supabase: boolean }> {
  return apiFetch("/health");
}
