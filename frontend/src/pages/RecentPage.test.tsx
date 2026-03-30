import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { listRecentAnalyses } from "../api/client";
import { RecentPage } from "./RecentPage";
import { renderWithProviders } from "../test/testUtils";

vi.mock("../api/client", () => ({
  listRecentAnalyses: vi.fn(),
}));

describe("RecentPage", () => {
  beforeEach(() => {
    vi.mocked(listRecentAnalyses).mockReset();
  });

  it("renders the empty state when there are no recent analyses", async () => {
    vi.mocked(listRecentAnalyses).mockResolvedValue({ items: [] });

    renderWithProviders(<RecentPage />);

    expect(await screen.findByText("No analyses yet")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /analyse a document/i })).toHaveAttribute("href", "/");
  });

  it("renders recent analysis items returned by the API", async () => {
    vi.mocked(listRecentAnalyses).mockResolvedValue({
      items: [
        {
          document_id: "doc_123",
          filename: "msa-contract.pdf",
          document_type: "pdf",
          created_at: "2026-03-30T09:00:00Z",
        },
      ],
    });

    renderWithProviders(<RecentPage />);

    expect(await screen.findByText("msa-contract.pdf")).toBeInTheDocument();
    expect(screen.getByText("Document ID: doc_123")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /view analysis/i })).toHaveAttribute("href", "/analyses/doc_123");
  });

  it("shows an error state and retries the recent analysis request", async () => {
    vi.mocked(listRecentAnalyses)
      .mockRejectedValueOnce(new Error("Backend unavailable"))
      .mockResolvedValueOnce({
        items: [
          {
            document_id: "doc_456",
            filename: "nda.txt",
            document_type: "txt",
            created_at: "2026-03-30T10:00:00Z",
          },
        ],
      });

    renderWithProviders(<RecentPage />);

    expect(await screen.findByText("Recent analyses unavailable")).toBeInTheDocument();
    expect(screen.getByText("Backend unavailable")).toBeInTheDocument();

    await userEvent.setup().click(screen.getByRole("button", { name: /try again/i }));

    expect(await screen.findByText("nda.txt")).toBeInTheDocument();
    expect(listRecentAnalyses).toHaveBeenCalledTimes(2);
  });
});
