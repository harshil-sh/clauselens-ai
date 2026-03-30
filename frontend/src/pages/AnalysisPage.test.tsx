import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AnalysisPage } from "./AnalysisPage";
import { renderWithProviders } from "../test/testUtils";
import { getAnalysis } from "../api/client";
import type { Analysis } from "../types/analysis";

vi.mock("../api/client", () => ({
  getAnalysis: vi.fn(),
}));

const analysisFixture: Analysis = {
  document_id: "doc_123",
  filename: "msa-contract.pdf",
  document_type: "pdf",
  created_at: "2026-03-30T09:00:00Z",
  summary: {
    short_summary: "Vendor access is permitted with weak termination language.",
    key_points: ["Auto-renewal applies unless notice is given."],
  },
  clauses: [
    {
      clause_id: "clause_1",
      heading: "Termination for convenience",
      category: "termination",
      extracted_text: "Either party may terminate with 90 days notice.",
      confidence: 0.92,
      page_reference: 4,
    },
  ],
  risk_flags: [
    {
      risk_id: "risk_1",
      severity: "high",
      title: "Long termination notice",
      description: "The agreement requires 90 days notice before termination.",
      recommendation: "Reduce the notice window to 30 days.",
      impacted_clause_id: "clause_1",
    },
  ],
};

describe("AnalysisPage", () => {
  beforeEach(() => {
    vi.mocked(getAnalysis).mockReset();
  });

  it("renders the fetched analysis summary, clauses, and risks", async () => {
    vi.mocked(getAnalysis).mockResolvedValue(analysisFixture);

    renderWithProviders(
      <Routes>
        <Route path="/analyses/:documentId" element={<AnalysisPage />} />
      </Routes>,
      { route: "/analyses/doc_123" }
    );

    expect(await screen.findByText("msa-contract.pdf")).toBeInTheDocument();
    expect(screen.getByText("Vendor access is permitted with weak termination language.")).toBeInTheDocument();
    expect(screen.getByText("Termination")).toBeInTheDocument();
    expect(screen.getByText("Termination for convenience")).toBeInTheDocument();
    expect(screen.getByText("Long termination notice")).toBeInTheDocument();
    expect(screen.getByText("High severity")).toBeInTheDocument();
    expect(screen.getByText(/related clause: termination for convenience/i)).toBeInTheDocument();
  });

  it("shows an error state and retries the analysis fetch", async () => {
    vi.mocked(getAnalysis)
      .mockRejectedValueOnce(new Error("Analysis not found"))
      .mockResolvedValue(analysisFixture);

    renderWithProviders(
      <Routes>
        <Route path="/analyses/:documentId" element={<AnalysisPage />} />
      </Routes>,
      { route: "/analyses/doc_123" }
    );

    expect(await screen.findByText("Analysis unavailable")).toBeInTheDocument();
    expect(screen.getByText("Analysis not found")).toBeInTheDocument();

    await userEvent.setup().click(screen.getByRole("button", { name: /try again/i }));

    expect(await screen.findByText("msa-contract.pdf")).toBeInTheDocument();
    expect(getAnalysis).toHaveBeenCalledTimes(2);
  });
});
