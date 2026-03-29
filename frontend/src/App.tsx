const supportedTypes = ["PDF", "DOCX", "TXT"];

export function App() {
  return (
    <main className="app-shell">
      <section className="hero">
        <p className="eyebrow">Phase 1 foundation</p>
        <h1>ClauseLens AI</h1>
        <p className="lede">
          Upload contracts and policy documents for structured AI analysis.
          This frontend skeleton establishes the application shell for later
          upload, results, and recent-analyses flows.
        </p>
      </section>

      <section className="panel" aria-labelledby="skeleton-heading">
        <h2 id="skeleton-heading">Frontend scaffold ready</h2>
        <p>
          The Vite + React + TypeScript app is configured and ready for the next
          UI tasks.
        </p>

        <div className="callout">
          <strong>Planned next capabilities</strong>
          <ul>
            <li>Document upload workflow</li>
            <li>Analysis results experience</li>
            <li>Recent analyses view</li>
          </ul>
        </div>

        <div>
          <strong>Supported document types</strong>
          <ul className="tag-list">
            {supportedTypes.map((type) => (
              <li key={type} className="tag">
                {type}
              </li>
            ))}
          </ul>
        </div>
      </section>
    </main>
  );
}
