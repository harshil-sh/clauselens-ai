import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { listRecentAnalyses } from "../api/client";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { EmptyState } from "../components/ui/EmptyState";
import { SectionHeading } from "../components/ui/SectionHeading";

function formatCreatedAt(value: string) {
  return new Date(value).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export function RecentPage() {
  const query = useQuery({
    queryKey: ["recent-analyses"],
    queryFn: listRecentAnalyses,
    retry: false,
  });

  if (query.isLoading) {
    return (
      <EmptyState
        tone="loading"
        title="Loading recent analyses"
        description="Fetching previously analysed documents."
      />
    );
  }

  if (query.isError || !query.data) {
    return (
      <EmptyState
        tone="error"
        title="Recent analyses unavailable"
        description={
          query.error instanceof Error ? query.error.message : "The recent document list could not be loaded."
        }
        action={
          <Button type="button" onClick={() => query.refetch()}>
            Try again
          </Button>
        }
      />
    );
  }

  if (query.data.items.length === 0) {
    return (
      <section className="page-section">
        <SectionHeading
          eyebrow="History"
          title="Recent analyses"
          description="Review the latest uploaded documents and return to their analysis pages."
        />
        <EmptyState
          title="No analyses yet"
          description="Completed analyses will appear here once documents are processed."
          action={
            <Link to="/" className="ui-button">
              Analyse a document
            </Link>
          }
        />
      </section>
    );
  }

  return (
    <section className="page-section">
      <SectionHeading
        eyebrow="History"
        title="Recent analyses"
        description={`Review the latest uploaded documents and return to their analysis pages. ${query.data.items.length} ${
          query.data.items.length === 1 ? "analysis" : "analyses"
        } available.`}
      />
      <Card>
        <ul className="content-list recent-list">
          {query.data.items.map((item) => (
            <li key={item.document_id} className="recent-list__item">
              <div className="recent-list__content">
                <div className="recent-list__meta">
                  <Badge>{item.document_type}</Badge>
                  <span>{formatCreatedAt(item.created_at)}</span>
                </div>
                <Link to={`/analyses/${item.document_id}`} className="recent-list__link">
                  {item.filename}
                </Link>
                <p className="recent-list__document-id">Document ID: {item.document_id}</p>
              </div>
              <Link to={`/analyses/${item.document_id}`} className="recent-list__action">
                View analysis
              </Link>
            </li>
          ))}
        </ul>
      </Card>
    </section>
  );
}
