import type { FormEvent } from "react";
import { useState } from "react";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { getUploadConstraints, validateSelectedFile } from "./fileValidation";

type Props = {
  onSubmit: (file: File) => Promise<void>;
};

export function FileUploadForm({ onSubmit }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string>("");
  const constraints = getUploadConstraints();

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
            <span>{(file.size / 1024).toFixed(1)} KB selected</span>
          </div>
        ) : null}
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
