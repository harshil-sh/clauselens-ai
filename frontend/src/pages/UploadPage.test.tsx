import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { UploadPage } from "./UploadPage";
import { renderWithProviders } from "../test/testUtils";
import { analyseDocument } from "../api/client";

const navigateMock = vi.fn();

vi.mock("../api/client", () => ({
  analyseDocument: vi.fn(),
}));

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual<typeof import("react-router-dom")>("react-router-dom");

  return {
    ...actual,
    useNavigate: () => navigateMock,
  };
});

describe("UploadPage", () => {
  beforeEach(() => {
    navigateMock.mockReset();
    vi.mocked(analyseDocument).mockReset();
  });

  it("uploads a file and navigates to the analysis result", async () => {
    vi.mocked(analyseDocument).mockResolvedValue({
      document_id: "doc_123",
      filename: "contract.txt",
      document_type: "txt",
      summary: { short_summary: "", key_points: [] },
      clauses: [],
      risk_flags: [],
      created_at: "2026-03-30T09:00:00Z",
    });

    renderWithProviders(<UploadPage />);

    const user = userEvent.setup();
    const fileInput = screen.getByLabelText(/select a document/i);
    const file = new File(["contract body"], "contract.txt", { type: "text/plain" });

    await user.upload(fileInput, file);
    await user.click(screen.getByRole("button", { name: /analyse document/i }));

    await waitFor(() => {
      expect(analyseDocument).toHaveBeenCalledWith(file);
      expect(navigateMock).toHaveBeenCalledWith("/analyses/doc_123");
    });
  });

  it("renders a submit error when analysis fails", async () => {
    vi.mocked(analyseDocument).mockRejectedValue(new Error("Backend unavailable"));

    renderWithProviders(<UploadPage />);

    const user = userEvent.setup();
    const fileInput = screen.getByLabelText(/select a document/i);
    const file = new File(["contract body"], "contract.txt", { type: "text/plain" });

    await user.upload(fileInput, file);
    await user.click(screen.getByRole("button", { name: /analyse document/i }));

    expect(await screen.findByText("Analysis failed")).toBeInTheDocument();
    expect(screen.getByText("Backend unavailable")).toBeInTheDocument();
    expect(navigateMock).not.toHaveBeenCalled();
  });
});
