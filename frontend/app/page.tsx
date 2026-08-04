'use client';

import { useEffect, useState } from 'react';

type Service = {
  name: string;
  path: string;
  description: string;
  owner: string;
  tags: string[];
  enabled: boolean;
};

type Policy = {
  name: string;
  category: string;
  description: string;
  enabled: boolean;
};

type Summary = {
  service_count: number;
  api_count: number;
  tenant_count: number;
  summary: string;
};

type RAGResponse = {
  answer: string;
  sources: Array<{ source: string; page?: number; relevance?: number }>;
  confidence: number;
  latency_ms: number;
  citations: Array<{ source: string; page?: number; relevance?: number }>;
};

const apiBase = 'http://127.0.0.1:8000';

const endpointCards = [
  {
    title: '/health',
    subtitle: 'Service heartbeat',
    accent: 'mint',
    sample: '{ "status": "healthy" }',
  },
  {
    title: '/gateway/services',
    subtitle: 'Registered service catalog',
    accent: 'amber',
    sample: '[ { "name": "ai-gateway" }, { "name": "ai-security" } ]',
  },
  {
    title: '/gateway/policies',
    subtitle: 'Security policy registry',
    accent: 'blue',
    sample: '[ { "name": "Prompt Injection Defense" } ]',
  },
  {
    title: '/gateway/model/register',
    subtitle: 'Supply-chain registration',
    accent: 'violet',
    sample: '{ "approved": true, "risk_score": 0.1 }',
  },
  {
    title: '/generate',
    subtitle: 'Prompt generation and scoring',
    accent: 'rose',
    sample: '{ "response": "simulated model output" }',
  },
  {
    title: '/rag',
    subtitle: 'Grounded retrieval response',
    accent: 'cyan',
    sample: '{ "answer": "verified context" }',
  },
];

const tenantAccessCards = [
  {
    tenant: 'Finance',
    endpoint: '/generate',
    model: 'gpt-4.1-finance-safe',
    access: 'Tier 1',
    purpose: 'Quarterly reporting, memo drafting, and earnings Q&A.',
    payload: '{"tenant_id":"finance","model":"gpt-4.1-finance-safe","prompt":"Summarize Q3 revenue risk"}',
  },
  {
    tenant: 'Legal',
    endpoint: '/generate',
    model: 'llama-3.3-70b-legal',
    access: 'Tier 2',
    purpose: 'Contract clause review and policy interpretation.',
    payload: '{"tenant_id":"legal","model":"llama-3.3-70b-legal","prompt":"Highlight indemnification concerns"}',
  },
  {
    tenant: 'Operations',
    endpoint: '/generate',
    model: 'mixtral-ops-8x22b',
    access: 'Tier 2',
    purpose: 'SOP generation, incident recap, and workload planning.',
    payload: '{"tenant_id":"ops","model":"mixtral-ops-8x22b","prompt":"Draft response plan for outage"}',
  },
  {
    tenant: 'Customer Support',
    endpoint: '/generate',
    model: 'gpt-4.1-mini-support',
    access: 'Tier 3',
    purpose: 'Ticket response drafts and escalation triage.',
    payload: '{"tenant_id":"support","model":"gpt-4.1-mini-support","prompt":"Generate empathetic resolution response"}',
  },
];

export default function Home() {
  const [services, setServices] = useState<Service[]>([]);
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [ragResult, setRagResult] = useState<RAGResponse | null>(null);
  const [query, setQuery] = useState('What is enterprise AI governance?');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch(`${apiBase}/gateway/services`)
      .then((response) => response.json())
      .then(setServices)
      .catch(console.error);

    fetch(`${apiBase}/gateway/policies`)
      .then((response) => response.json())
      .then(setPolicies)
      .catch(console.error);

    fetch(`${apiBase}/gateway/summary`)
      .then((response) => response.json())
      .then(setSummary)
      .catch(console.error);
  }, []);

  async function runRag() {
    setLoading(true);
    setRagResult(null);

    const response = await fetch(`${apiBase}/rag`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, tenant_id: 'default' }),
    });

    const data = await response.json();
    setRagResult(data);
    setLoading(false);
  }

  return (
    <main className="shell">
      <section className="hero panel">
        <div>
          <p className="eyebrow">Enterprise AI General Management Platform</p>
          <h1>Operate AI APIs like a real platform, not a collection of scripts.</h1>
          <p className="lede">
            This dashboard exposes the gateway, policy layer, model governance, RAG path, and agent orchestration in one place.
          </p>
        </div>

        <div className="hero-stats">
          <div className="stat-card">
            <span>Services</span>
            <strong>{summary?.service_count ?? '...'}</strong>
          </div>
          <div className="stat-card">
            <span>APIs</span>
            <strong>{summary?.api_count ?? '...'}</strong>
          </div>
          <div className="stat-card">
            <span>Tenants</span>
            <strong>{summary?.tenant_count ?? '...'}</strong>
          </div>
        </div>
      </section>

      <section className="panel summary-panel">
        <div>
          <h2>Platform summary</h2>
          <p>{summary?.summary ?? 'Loading platform summary...'}</p>
        </div>
        <div className="summary-badges">
          <span>Gateway</span>
          <span>Security</span>
          <span>Registry</span>
          <span>RAG</span>
          <span>Agent</span>
        </div>
      </section>

      <section className="endpoint-grid">
        {endpointCards.map((card) => (
          <article key={card.title} className={`endpoint-card panel accent-${card.accent}`}>
            <p className="endpoint-title">{card.title}</p>
            <p className="endpoint-subtitle">{card.subtitle}</p>
            <pre className="endpoint-sample">{card.sample}</pre>
          </article>
        ))}
      </section>

      <section className="two-column">
        <div className="panel">
          <h2>Registered API services</h2>
          <div className="stack">
            {services.length ? (
              services.map((service) => (
                <article key={service.name} className="list-card">
                  <div className="list-card-top">
                    <h3>{service.name}</h3>
                    <span>{service.enabled ? 'Enabled' : 'Disabled'}</span>
                  </div>
                  <p>{service.description}</p>
                  <p><strong>Path:</strong> {service.path}</p>
                  <p><strong>Owner:</strong> {service.owner}</p>
                  <p><strong>Tags:</strong> {service.tags.join(', ')}</p>
                </article>
              ))
            ) : (
              <p>Loading services...</p>
            )}
          </div>
        </div>

        <div className="panel">
          <h2>Security & policy catalog</h2>
          <div className="stack">
            {policies.length ? (
              policies.map((policy) => (
                <article key={policy.name} className="list-card">
                  <div className="list-card-top">
                    <h3>{policy.name}</h3>
                    <span>{policy.category}</span>
                  </div>
                  <p>{policy.description}</p>
                  <p><strong>Enabled:</strong> {policy.enabled ? 'Yes' : 'No'}</p>
                </article>
              ))
            ) : (
              <p>Loading policies...</p>
            )}
          </div>
        </div>
      </section>

      <section className="panel tenant-panel">
        <div className="tenant-heading">
          <div>
            <h2>Multi-tenant model access with one shared API</h2>
            <p>
              Every enterprise team calls the same interface, while governance and routing policies choose a tenant-appropriate LLM.
            </p>
          </div>
          <div className="tenant-shared-endpoint">
            <span>Shared endpoint</span>
            <strong>POST /generate</strong>
          </div>
        </div>

        <div className="tenant-grid">
          {tenantAccessCards.map((card) => (
            <article key={card.tenant} className="tenant-card">
              <div className="tenant-card-top">
                <h3>{card.tenant}</h3>
                <span>{card.access}</span>
              </div>
              <p><strong>Model:</strong> {card.model}</p>
              <p><strong>Use case:</strong> {card.purpose}</p>
              <p><strong>API:</strong> {card.endpoint}</p>
              <pre>{card.payload}</pre>
            </article>
          ))}
        </div>
      </section>

      <section className="panel rag-panel">
        <div className="rag-header">
          <div>
            <h2>Live RAG query</h2>
            <p>Send a prompt to the backend and inspect the grounded response, latency, and citations.</p>
          </div>
          <button onClick={runRag} disabled={loading} className="action-button">
            {loading ? 'Running...' : 'Run RAG query'}
          </button>
        </div>

        <textarea
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          rows={5}
          className="query-box"
        />

        {ragResult ? (
          <div className="rag-result">
            <h3>RAG response</h3>
            <p><strong>Answer:</strong> {ragResult.answer}</p>
            <div className="result-meta">
              <span>Confidence {ragResult.confidence}</span>
              <span>Latency {ragResult.latency_ms.toFixed(1)} ms</span>
              <span>{ragResult.sources.length} sources</span>
            </div>
            <div>
              <strong>Citations</strong>
              <ul>
                {ragResult.citations.length ? ragResult.citations.map((citation, index) => (
                  <li key={index}>{citation.source} (relevance: {citation.relevance ?? 'n/a'})</li>
                )) : <li>No citations generated</li>}
              </ul>
            </div>
          </div>
        ) : null}
      </section>
    </main>
  );
}
