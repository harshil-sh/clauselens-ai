import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { getAnalysis } from "../api/client";
import { Badge } from "../components/ui/Badge";
import { Card } from "../components/ui/Card";
import { EmptyState } from "../components/ui/EmptyState";
import { SectionHeading } from "../components/ui/SectionHeading";

export function AnalysisPage() {
  const { documentId = "" } = useParams();
  const query = useQuery({
    queryKey: ["analysis", documentId],
    queryFn: () => getAnalysis(documentId),
    enabled: Boolean(documentId),
  });

  if (query.isLoading) {
    return <EmptyState title="Loading analysis" description="Fetching document summary, clauses, and risks." />;
  }

  if (query.isError || !query.data) {
    return <EmptyState title="Analysis unavailable" description="The requested analysis could not be loaded." />;
  }

  const analysis = query.data;

  return (
    <section className="page-section">
      <SectionHeading
        eyebrow="Analysis"
        title={analysis.filename}
        description={
          <>
            Document type: <strong>{analysis.document_type}</strong>
          </>
        }
      />

      <Card>
        <h2>Executive summary</h2>
        <p>{analysis.summary.short_summary}</p>
        <ul className="content-list">
          {analysis.summary.key_points.map((point) => (
            <li key={point}>{point}</li>
          ))}
        </ul>
      </Card>

      <Card>
        <h2>Clauses</h2>
        {analysis.clauses.map((clause) => (
          <article key={clause.clause_id} className="stacked-item">
            <strong>{clause.heading}</strong>
            <p>
              <em>{clause.category}</em>
            </p>
            <p>{clause.extracted_text}</p>
          </article>
        ))}
      </Card>

      <Card>
        <h2>Risk flags</h2>
        {analysis.risk_flags.map((risk) => (
          <article key={risk.risk_id} className="stacked-item">
            <div className="risk-flag__header">
              <strong>{risk.title}</strong>
              <Badge tone={risk.severity.toLowerCase() === "high" ? "warning" : "neutral"}>
                {risk.severity}
              </Badge>
            </div>
            <p>{risk.description}</p>
            <p>
              <strong>Recommendation:</strong> {risk.recommendation}
            </p>
          </article>
        ))}
      </Card>
    </section>
  );
}
