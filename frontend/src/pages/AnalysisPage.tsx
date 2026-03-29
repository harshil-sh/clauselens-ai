import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { getAnalysis } from "../api/client";

export function AnalysisPage() {
  const { documentId = "" } = useParams();
  const query = useQuery({
    queryKey: ["analysis", documentId],
    queryFn: () => getAnalysis(documentId),
    enabled: Boolean(documentId),
  });

  if (query.isLoading) {
    return <p>Loading analysis...</p>;
  }

  if (query.isError || !query.data) {
    return <p>Unable to load analysis.</p>;
  }

  const analysis = query.data;

  return (
    <section>
      <h2>{analysis.filename}</h2>
      <p><strong>Type:</strong> {analysis.document_type}</p>

      <section style={{ marginTop: "20px" }}>
        <h3>Executive summary</h3>
        <p>{analysis.summary.short_summary}</p>
        <ul>
          {analysis.summary.key_points.map((point) => (
            <li key={point}>{point}</li>
          ))}
        </ul>
      </section>

      <section style={{ marginTop: "20px" }}>
        <h3>Clauses</h3>
        {analysis.clauses.map((clause) => (
          <article key={clause.clause_id} style={{ borderTop: "1px solid #eee", paddingTop: "12px", marginTop: "12px" }}>
            <strong>{clause.heading}</strong>
            <p><em>{clause.category}</em></p>
            <p>{clause.extracted_text}</p>
          </article>
        ))}
      </section>

      <section style={{ marginTop: "20px" }}>
        <h3>Risk flags</h3>
        {analysis.risk_flags.map((risk) => (
          <article key={risk.risk_id} style={{ borderTop: "1px solid #eee", paddingTop: "12px", marginTop: "12px" }}>
            <strong>{risk.title}</strong> — <span>{risk.severity}</span>
            <p>{risk.description}</p>
            <p><strong>Recommendation:</strong> {risk.recommendation}</p>
          </article>
        ))}
      </section>
    </section>
  );
}
