import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { listRecentAnalyses } from "../api/client";

export function RecentPage() {
  const query = useQuery({
    queryKey: ["recent-analyses"],
    queryFn: listRecentAnalyses,
  });

  if (query.isLoading) {
    return <p>Loading recent analyses...</p>;
  }

  if (query.isError || !query.data) {
    return <p>Unable to load recent analyses.</p>;
  }

  if (query.data.items.length === 0) {
    return <p>No analyses yet.</p>;
  }

  return (
    <section>
      <h2>Recent analyses</h2>
      <ul>
        {query.data.items.map((item) => (
          <li key={item.document_id}>
            <Link to={`/analyses/${item.document_id}`}>{item.filename}</Link> — {item.document_type}
          </li>
        ))}
      </ul>
    </section>
  );
}
