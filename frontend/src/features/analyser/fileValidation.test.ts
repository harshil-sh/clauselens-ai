import { describe, expect, it } from "vitest";
import { getUploadConstraints, validateSelectedFile } from "./fileValidation";

describe("fileValidation", () => {
  it("returns the configured upload constraints", () => {
    expect(getUploadConstraints()).toEqual({
      accept: ".pdf,.docx,.txt",
      maxUploadBytes: 10 * 1024 * 1024,
      maxUploadLabel: "10 MB",
      supportedFileTypesLabel: "PDF, DOCX, TXT",
    });
  });

  it("rejects missing, unsupported, empty, and oversized files", () => {
    expect(validateSelectedFile(null)).toBe("Please select a document first.");
    expect(validateSelectedFile(new File(["contract"], "contract.csv"))).toBe(
      "Only PDF, DOCX, and TXT files are supported."
    );
    expect(validateSelectedFile(new File([], "contract.txt"))).toBe("The selected file is empty.");
    expect(
      validateSelectedFile({
        name: "contract.txt",
        size: (10 * 1024 * 1024) + 1,
      } as File)
    ).toBe("The selected file exceeds the 10 MB limit.");
  });

  it("accepts supported extensions regardless of case", () => {
    expect(validateSelectedFile(new File(["contract"], "MASTER.DOCX"))).toBeNull();
  });
});
