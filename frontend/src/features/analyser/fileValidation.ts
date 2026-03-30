const SUPPORTED_EXTENSIONS = [".pdf", ".docx", ".txt"] as const;
const MAX_UPLOAD_BYTES = 10 * 1024 * 1024;

function formatExtensions(): string {
  return SUPPORTED_EXTENSIONS.map((extension) => extension.replace(".", "").toUpperCase()).join(", ");
}

export function getUploadConstraints() {
  return {
    accept: SUPPORTED_EXTENSIONS.join(","),
    maxUploadBytes: MAX_UPLOAD_BYTES,
    maxUploadLabel: "10 MB",
    supportedFileTypesLabel: formatExtensions(),
  };
}

export function validateSelectedFile(file: File | null): string | null {
  if (!file) {
    return "Please select a document first.";
  }

  const extension = file.name.slice(file.name.lastIndexOf(".")).toLowerCase();
  if (!SUPPORTED_EXTENSIONS.includes(extension as (typeof SUPPORTED_EXTENSIONS)[number])) {
    return "Only PDF, DOCX, and TXT files are supported.";
  }

  if (file.size === 0) {
    return "The selected file is empty.";
  }

  if (file.size > MAX_UPLOAD_BYTES) {
    return "The selected file exceeds the 10 MB limit.";
  }

  return null;
}
