import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { listRecentAnalyses } from "../api/client";
import { Badge } from "../components/ui/Badge";
import { Card } from "../components/ui/Card";
import { EmptyState } from "../components/ui/EmptyState";
import { SectionHeading } from "../components/ui/SectionHeading";

export function RecentPage() {
  const query = useQuery({
    queryKey: ["recent-analyses"],
    queryFn: listRecentAnalyses,
  });

  if (query.isLoading) {
    return <EmptyState title="Loading recent analyses" description="Fetching previously analysed documents." />;
  }

  if (query.isError || !query.data) {
    return <EmptyState title="Recent analyses unavailable" description="The recent document list could not be loaded." />;
  }

  if (query.data.items.length === 0) {
    return <EmptyState title="No analyses yet" description="Completed analyses will appear here once documents are processed." />;
  }

  return (
    <section className="page-section">
      <SectionHeading
        eyebrow="History"
        title="Recent analyses"
        description="Review the latest uploaded documents and return to their analysis pages."
      />
      <Card>
        <ul className="content-list recent-list">
        {query.data.items.map((item) => (
          <li key={item.document_id} className="recent-list__item">
            <div>
              <Link to={`/analyses/${item.document_id}`} className="recent-list__link">
                {item.filename}
              </Link>
              <p>{new Date(item.created_at).toLocaleString()}</p>
            </div>
            <Badge>{item.document_type}</Badge>
          </li>
        ))}
        </ul>
      </Card>
    </section>
  );
}
