import { Link, Outlet } from "react-router-dom";

export function PageShell() {
  return (
    <div style={{ maxWidth: 960, margin: "0 auto", padding: "24px", fontFamily: "Arial, sans-serif" }}>
      <header style={{ marginBottom: "24px" }}>
        <h1 style={{ margin: 0 }}>ClauseLens AI</h1>
        <p style={{ color: "#555" }}>AI document analyser for contracts and policy documents</p>
        <nav style={{ display: "flex", gap: "16px", marginTop: "12px" }}>
          <Link to="/">Upload</Link>
          <Link to="/recent">Recent analyses</Link>
        </nav>
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  );
}
