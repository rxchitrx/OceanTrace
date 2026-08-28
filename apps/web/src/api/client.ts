import type { AnalysisResult, CasePayload, CaseSummary } from "../types";
import { fallbackCasePayload, fallbackCases, fallbackResult } from "../demoData";

const API_BASE = "http://127.0.0.1:8000/api";

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, init);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return (await response.json()) as T;
}

export function fetchCases(): Promise<CaseSummary[]> {
  return requestJson<CaseSummary[]>("/cases").catch(() => fallbackCases);
}

export function fetchCase(caseId: string): Promise<CasePayload> {
  return requestJson<CasePayload>(`/cases/${caseId}`).catch(() => ({
    ...fallbackCasePayload,
    manifest: {
      ...fallbackCasePayload.manifest,
      id: caseId,
    },
  }));
}

export function runCase(caseId: string): Promise<AnalysisResult> {
  return requestJson<AnalysisResult>(`/cases/${caseId}/run`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      mode: "full",
      seed: 26143,
      use_cached_result: true,
    }),
  }).catch(() => ({
    ...fallbackResult,
    run_id: `${caseId}-seed-26143`,
  }));
}
