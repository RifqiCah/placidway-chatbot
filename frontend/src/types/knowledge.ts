export interface HealthResponse {
  status: "ok" | "degraded";
  sources?: number;
  chunks?: number;
  refreshed_at?: string;
  llm_configured?: boolean;
  llm_provider?: string;
  llm_model?: string;
  reason?: string;
}

export interface RefreshResponse {
  status: string;
  sources: number;
  chunks: number;
  refreshed_at: string;
}

