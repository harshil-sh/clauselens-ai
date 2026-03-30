import type { FormEvent } from "react";
import { useState } from "react";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { EmptyState } from "../../components/ui/EmptyState";
import { getUploadConstraints, validateSelectedFile } from "./fileValidation";

type Props = {
  onSubmit: (file: File) => Promise<void>;
};

export function FileUploadForm({ onSubmit }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string>("");
  const constraints = getUploadConstraints();
  const validationMessage = validateSelectedFile(file);
  const canSubmit = !submitting && Boolean(file) && !validationMessage;

  function handleFileChange(nextFile: File | null) {
    setFile(nextFile);
    setError(nextFile ? validateSelectedFile(nextFile) ?? "" : "");
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const validationError = validateSelectedFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }

    setSubmitting(true);
    setError("");

    try {
      await onSubmit(file);
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Document analysis failed.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Card>
      <form className="upload-form" onSubmit={handleSubmit}>
        <p className="upload-form__meta">
          Supported file types: {constraints.supportedFileTypesLabel} up to {constraints.maxUploadLabel}
        </p>
        {!file && !submitting ? (
          <EmptyState
            title="No document selected"
            description="Choose a PDF, DOCX, or TXT file to start the analysis workflow."
          />
        ) : null}
        <label className="upload-form__field">
          <span>Select a document</span>
          <input
            type="file"
            accept={constraints.accept}
            disabled={submitting}
            onChange={(event) => handleFileChange(event.target.files?.[0] ?? null)}
          />
        </label>
        {file ? (
          <div className="upload-form__selection" aria-live="polite">
            <strong>{file.name}</strong>
            <span>
              {(file.size / 1024).toFixed(1)} KB selected
              {submitting ? " • Analysis in progress" : ""}
            </span>
          </div>
        ) : null}
        {submitting ? (
          <EmptyState
            tone="loading"
            title="Analysing document"
            description="Uploading the file and generating the summary, clauses, and risk flags."
          />
        ) : null}
        <div className="upload-form__actions">
          <Button type="submit" disabled={!canSubmit}>
            {submitting ? "Analysing..." : "Analyse document"}
          </Button>
        </div>
        {error ? (
          <EmptyState
            tone="error"
            title="Analysis failed"
            description={error}
          />
        ) : null}
      </form>
    </Card>
  );
}
