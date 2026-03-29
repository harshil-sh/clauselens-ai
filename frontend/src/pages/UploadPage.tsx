import { useNavigate } from "react-router-dom";
import { analyseDocument } from "../api/client";
import { FileUploadForm } from "../features/analyser/FileUploadForm";

export function UploadPage() {
  const navigate = useNavigate();

  async function handleSubmit(file: File) {
    const result = await analyseDocument(file);
    navigate(`/analyses/${result.document_id}`);
  }

  return (
    <section>
      <h2>Upload a contract or policy document</h2>
      <p>Get a structured summary, clause extraction, and risk flags.</p>
      <FileUploadForm onSubmit={handleSubmit} />
    </section>
  );
}
