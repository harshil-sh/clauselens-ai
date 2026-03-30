import type { Analysis, RecentAnalysesResponse } from "../types/analysis";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8001/api/v1";

type ApiErrorResponse = {
  error?: {
    message?: string;
  };
};

async function readErrorMessage(response: Response, fallbackMessage: string): Promise<string> {
  try {
    const data = (await response.json()) as ApiErrorResponse;
    return data.error?.message ?? fallbackMessage;
  } catch {
    return fallbackMessage;
  }
}

export async function analyseDocument(file: File): Promise<Analysis> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/documents/analyse`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "Failed to analyse document."));
  }

  return response.json();
}

export async function getAnalysis(documentId: string): Promise<Analysis> {
  const response = await fetch(`${API_BASE_URL}/documents/${documentId}`);
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "Failed to fetch analysis."));
  }
  return response.json();
}

export async function listRecentAnalyses(): Promise<RecentAnalysesResponse> {
  const response = await fetch(`${API_BASE_URL}/documents`);
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "Failed to fetch recent analyses."));
  }
  return response.json();
}
