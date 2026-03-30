import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { getAnalysis } from "../api/client";
import { Badge } from "../components/ui/Badge";
import { Card } from "../components/ui/Card";
import { EmptyState } from "../components/ui/EmptyState";
import { SectionHeading } from "../components/ui/SectionHeading";

function formatAnalysisDate(value: string) {
  return new Date(value).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

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
  const createdAtLabel = formatAnalysisDate(analysis.created_at);
  const clausesCount = analysis.clauses.length;
  const risksCount = analysis.risk_flags.length;
  const keyPointsCount = analysis.summary.key_points.length;

  return (
    <section className="page-section analysis-page">
      <SectionHeading
        eyebrow="Analysis"
        title={analysis.filename}
        description={
          <>
            Reviewed on <strong>{createdAtLabel}</strong> as a <strong>{analysis.document_type}</strong> document.
          </>
        }
      />

      <div className="analysis-page__hero">
        <Card className="analysis-page__summary-card">
          <div className="analysis-page__card-heading">
            <Badge tone="accent">Executive summary</Badge>
            <span className="analysis-page__timestamp">Analysis ready</span>
          </div>
          <p className="analysis-page__summary-lede">{analysis.summary.short_summary}</p>
          <div className="analysis-page__metrics" aria-label="Analysis coverage">
            <article className="analysis-page__metric">
              <strong>{keyPointsCount}</strong>
              <span>key points</span>
            </article>
            <article className="analysis-page__metric">
              <strong>{clausesCount}</strong>
              <span>clauses extracted</span>
            </article>
            <article className="analysis-page__metric">
              <strong>{risksCount}</strong>
              <span>risk flags detected</span>
            </article>
          </div>
          <div className="analysis-page__insights">
            <h2>What stands out</h2>
            {analysis.summary.key_points.length > 0 ? (
              <ul className="analysis-page__key-points">
                {analysis.summary.key_points.map((point) => (
                  <li key={point}>{point}</li>
                ))}
              </ul>
            ) : (
              <p>No specific key points were returned for this analysis.</p>
            )}
          </div>
        </Card>

        <Card className="analysis-page__overview-card">
          <h2>Document overview</h2>
          <dl className="analysis-page__meta-list">
            <div>
              <dt>Document ID</dt>
              <dd>{analysis.document_id}</dd>
            </div>
            <div>
              <dt>Type</dt>
              <dd>{analysis.document_type}</dd>
            </div>
            <div>
              <dt>Generated</dt>
              <dd>{createdAtLabel}</dd>
            </div>
          </dl>
        </Card>
      </div>

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
