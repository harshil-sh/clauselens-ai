import { NavLink, Outlet } from "react-router-dom";
import { Badge } from "./ui/Badge";

export function PageShell() {
  return (
    <div className="page-shell">
      <header className="page-shell__header">
        <div>
          <div className="page-shell__brand-row">
            <h1>ClauseLens AI</h1>
            <Badge tone="accent">Phase 1</Badge>
          </div>
          <p className="page-shell__lede">
            AI document analysis for contracts and policy documents, with a clear path
            from upload to structured review.
          </p>
        </div>
        <nav className="page-shell__nav" aria-label="Primary">
          <NavLink
            to="/"
            end
            className={({ isActive }) => (isActive ? "page-shell__nav-link is-active" : "page-shell__nav-link")}
          >
            Upload
          </NavLink>
          <NavLink
            to="/recent"
            className={({ isActive }) => (isActive ? "page-shell__nav-link is-active" : "page-shell__nav-link")}
          >
            Recent analyses
          </NavLink>
        </nav>
      </header>
      <main className="page-shell__main">
        <Outlet />
      </main>
      <footer className="page-shell__footer">
        <p>Frontend foundation for upload, analysis, and history workflows.</p>
      </footer>
    </div>
  );
}
