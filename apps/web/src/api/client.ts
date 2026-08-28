import type { AnalysisResult, CasePayload, CaseSummary, SarBounds } from "../types";

const configuredBase = import.meta.env.VITE_API_BASE_URL as string | undefined;
export const API_BASE = (configuredBase || "/api").replace(/\/$/, "");

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, init);
  } catch {
    throw new Error("OceanTrace API is unreachable. Start the API service and retry.");
  }

  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) detail = body.detail;
    } catch {
      // The HTTP status is still useful when the server returns no JSON body.
    }
    throw new Error(detail);
  }
  return (await response.json()) as T;
}

export function fetchCases(): Promise<CaseSummary[]> {
  return requestJson<CaseSummary[]>("/cases");
}

export function fetchCase(caseId: string): Promise<CasePayload> {
  return requestJson<CasePayload>(`/cases/${encodeURIComponent(caseId)}`);
}

export function fetchSarBounds(caseId: string): Promise<SarBounds> {
  return requestJson<SarBounds>(`/cases/${encodeURIComponent(caseId)}/sar/bounds`);
}

export function sarImageUrl(caseId: string): string {
  return `${API_BASE}/cases/${encodeURIComponent(caseId)}/sar/image`;
}

export function runCase(caseId: string): Promise<AnalysisResult> {
  return requestJson<AnalysisResult>(`/cases/${encodeURIComponent(caseId)}/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mode: "full", seed: 26143, use_cached_result: false }),
  });
}
