import type { FormEvent } from "react";
import { useState } from "react";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";

type Props = {
  onSubmit: (file: File) => Promise<void>;
};

export function FileUploadForm({ onSubmit }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string>("");

  async function handleSubmit(event: FormEvent) {
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
    <Card>
      <form className="upload-form" onSubmit={handleSubmit}>
        <p className="upload-form__meta">Supported file types: PDF, DOCX, TXT</p>
        <label className="upload-form__field">
          <span>Select a document</span>
          <input
            type="file"
            accept=".pdf,.docx,.txt"
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          />
        </label>
        <div className="upload-form__actions">
          <Button type="submit" disabled={submitting}>
            {submitting ? "Analysing..." : "Analyse document"}
          </Button>
        </div>
        {error ? <p className="upload-form__error">{error}</p> : null}
      </form>
    </Card>
  );
}
