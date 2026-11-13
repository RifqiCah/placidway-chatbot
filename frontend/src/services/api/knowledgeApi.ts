import type { HealthResponse, RefreshResponse } from "../../types/knowledge";

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch("/api/health");
  if (!response.ok) throw new Error(`Health request failed (${response.status})`);
  return response.json() as Promise<HealthResponse>;
}

export async function refreshKnowledge(token: string): Promise<RefreshResponse> {
  const response = await fetch("/api/refresh", {
    method: "POST",
    headers: { "X-Refresh-Token": token },
  });
  const body = (await response.json()) as RefreshResponse & { detail?: string };
  if (!response.ok) throw new Error(body.detail ?? `Refresh failed (${response.status})`);
  return body;
}

export function formatKnowledgeStatus(health: HealthResponse, locale?: string): string {
  if (health.status !== "ok" || !health.refreshed_at) return "Knowledge status unavailable";
  const date = new Date(health.refreshed_at).toLocaleDateString(locale, {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
  const mode = health.llm_configured
    ? `${health.llm_provider ?? "LLM"} / ${health.llm_model ?? "configured model"}`
    : "Safe extractive mode";
  return `Updated ${date} · ${health.chunks ?? 0} passages · ${mode}`;
}

