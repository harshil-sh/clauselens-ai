import { useNavigate } from "react-router-dom";
import { analyseDocument } from "../api/client";
import { Badge } from "../components/ui/Badge";
import { SectionHeading } from "../components/ui/SectionHeading";
import { FileUploadForm } from "../features/analyser/FileUploadForm";
import { getUploadConstraints } from "../features/analyser/fileValidation";

export function UploadPage() {
  const navigate = useNavigate();
  const constraints = getUploadConstraints();

  async function handleSubmit(file: File) {
    const result = await analyseDocument(file);
    navigate(`/analyses/${result.document_id}`);
  }

  return (
    <section className="page-section">
      <SectionHeading
        eyebrow="Upload"
        title="Upload a contract or policy document"
        description={`Get a structured summary, clause extraction, and risk flags from a single document workflow. Upload PDF, DOCX, or TXT files up to ${constraints.maxUploadLabel}.`}
      />
      <div className="upload-page__badges" aria-label="Supported file types">
        <Badge>PDF</Badge>
        <Badge>DOCX</Badge>
        <Badge>TXT</Badge>
      </div>
      <FileUploadForm onSubmit={handleSubmit} />
    </section>
  );
}
