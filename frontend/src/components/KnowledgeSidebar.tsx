import { useCallback, useEffect, useState } from "react";

import { formatKnowledgeStatus, getHealth, refreshKnowledge } from "../services/api/knowledgeApi";
import { Brand } from "./Brand";

const sources = [
  ["01", "ITC clinic profile", "Clinic information"],
  ["02", "Adenocarcinoma package", "Treatment package"],
  ["03", "Adrenal cancer package", "Treatment package"],
  ["04", "Anal cancer package", "Treatment package"],
  ["05", "ITC clinic videos", "Video library"],
  ["06", "ITC price list", "Pricing information"],
  ["07", "Cost comparison", "Alternative medicine"],
] as const;

interface Props {
  open: boolean;
}

export function KnowledgeSidebar({ open }: Props) {
  const [status, setStatus] = useState("Checking knowledge base…");
  const [refreshing, setRefreshing] = useState(false);

  const loadHealth = useCallback(async () => {
    try {
      setStatus(formatKnowledgeStatus(await getHealth()));
    } catch {
      setStatus("Knowledge status unavailable");
    }
  }, []);

  useEffect(() => { void loadHealth(); }, [loadHealth]);

  async function handleRefresh() {
    const token = window.prompt("Enter the refresh token. Refreshing all seven pages takes about 20 seconds.");
    if (!token) return;
    setRefreshing(true);
    try {
      const result = await refreshKnowledge(token);
      window.alert(`Knowledge refreshed: ${result.sources} sources, ${result.chunks} passages.`);
      await loadHealth();
    } catch (error) {
      window.alert(error instanceof Error ? error.message : "Refresh failed");
    } finally {
      setRefreshing(false);
    }
  }

  return (
    <aside className={`sidebar ${open ? "open" : ""}`} aria-label="Knowledge base information">
      <Brand />
      <div className="trust-card">
        <span className="trust-icon" aria-hidden="true">✓</span>
        <div><strong>Grounded answers</strong><p>Every answer is limited to the approved pages and links back to its source.</p></div>
      </div>
      <section className="sources-section">
        <div className="section-heading"><span>Knowledge base</span><span className="source-count">7 sources</span></div>
        <ul className="source-list">
          {sources.map(([number, title, type]) => (
            <li key={number}>
              <span className="source-icon">{number}</span>
              <span>{title}<small>{type}</small></span>
            </li>
          ))}
        </ul>
      </section>
      <div className="sidebar-footer">
        <button className="refresh-button" type="button" onClick={handleRefresh} disabled={refreshing}>
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 11a8.1 8.1 0 0 0-15.5-2M4 4v5h5M4 13a8.1 8.1 0 0 0 15.5 2M20 20v-5h-5" /></svg>
          {refreshing ? "Refreshing…" : "Refresh knowledge"}
        </button>
        <p>{status}</p>
      </div>
    </aside>
  );
}

