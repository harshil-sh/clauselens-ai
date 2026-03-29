import { useState } from "react";

type Props = {
  onSubmit: (file: File) => Promise<void>;
};

export function FileUploadForm({ onSubmit }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string>("");

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!file) {
      setError("Please select a document first.");
      return;
    }

    setSubmitting(true);
    setError("");

    try {
      await onSubmit(file);
    } catch {
      setError("Document analysis failed.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} style={{ border: "1px solid #ddd", padding: "16px", borderRadius: "8px" }}>
      <p>Supported file types: PDF, DOCX, TXT</p>
      <input
        type="file"
        accept=".pdf,.docx,.txt"
        onChange={(event) => setFile(event.target.files?.[0] ?? null)}
      />
      <div style={{ marginTop: "12px" }}>
        <button type="submit" disabled={submitting}>
          {submitting ? "Analysing..." : "Analyse document"}
        </button>
      </div>
      {error ? <p style={{ color: "crimson" }}>{error}</p> : null}
    </form>
  );
}
