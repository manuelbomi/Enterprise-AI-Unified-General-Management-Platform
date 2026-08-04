# Enterprise AI Unified General Management Platform

This repository contains a scaffold generator for enterprise AI services.
The purpose of this platform is to standardize how AI solutions are packaged,
deployed, monitored, and governed across an organization.

## At a glance

```mermaid
flowchart LR
  U[User / Product Team] --> G[FastAPI Gateway]
  G --> S[Security Layer]
  G --> M[Model Registry]
  G --> R[RAG Pipeline]
  G --> A[Agent Orchestrator]
  G --> F[Next.js Dashboard]

  S --> P[Prompt Injection Defense]
  S --> T[Tenant Isolation]
  M --> C[Model Supply Chain Checks]
  R --> D[Grounded Answers + Citations]
  A --> E[Plan / Execute / Evaluate]
```

This diagram is the quickest way to understand the repository: it is an
enterprise AI management platform, not just a single model demo.

## What this project does

The generator in `main.py` creates a set of baseline artifacts for an AI service:

- Infrastructure-as-Code (Terraform) to provision cloud resources
- Container build definition (`Dockerfile`) for consistent runtime packaging
- GitHub Actions CI/CD workflow for automated validation and deployment
- Monitoring dashboard and alerting configuration for production observability
- Evaluation test scaffolding for quality, safety, and compliance checks
- FastAPI-based service entrypoint scaffold with multi-tenant, security,
  and model-routing concepts

## Enterprise AI scaffolding goals

This platform is designed to help enterprises onboard AI services with:

- consistent cloud architecture patterns
- reusable deployment automation
- built-in observability and safety checks
- explicit separation of infrastructure, model, and API concerns
- support for multiple AI service types: LLM, RAG, and agent

## Core use cases

| Use case | What you see | Why it matters |
| --- | --- | --- |
| API gateway management | Registered services, summary, and policies | Shows how teams can catalog and govern internal AI APIs |
| Prompt safety | Validation endpoint and policy catalog | Demonstrates prompt injection defense and governance |
| Model governance | Model registration endpoint and risk scoring | Shows supply-chain checks before model use |
| RAG assistant | Live query box in the frontend | Demonstrates grounded answers with citations |
| Agent workflow | Agent endpoint and orchestration layer | Shows plan/execute/evaluate behavior |

## Comparison with enterprise API platforms (for example, Kong/Konnect)

This project is intentionally a reference implementation and accelerator.
Kong/Konnect and similar enterprise API management products are mature,
production-hardened platforms with broad ecosystem support.

The table below is directional (not a benchmark) and helps teams choose the
right starting point.

| Dimension | This repository (Enterprise AI Service Generator) | Kong/Konnect-style enterprise platform |
| --- | --- | --- |
| Primary goal | Fast internal bootstrap for AI gateway patterns, guardrails, and multi-tenant LLM routing | Full enterprise API management and gateway operations at scale |
| Upfront licensing cost | Low software cost (open code), higher engineering ownership | Commercial pricing (varies by edition/usage), lower platform build burden |
| Operational complexity | Moderate-to-high for your team because you own architecture and operations | Moderate, with strong vendor defaults, tooling, and managed options |
| Time to first deployment | Fast for prototypes and internal pilots | Fast to moderate, depending on enterprise onboarding and policy setup |
| Production hardening | Partial by default; requires additional reliability, security, and SRE controls | High; broadly tested patterns, production features, and support programs |
| API governance depth | Focused on AI use cases in this repo (prompt safety, tenant controls, model checks) | Deep API lifecycle/governance capabilities across many API types |
| Plugin/integration ecosystem | Custom development required for most integrations | Large integration ecosystem and established extension model |
| Multi-team/enterprise scaling | Works well for controlled internal scope; scaling requires additional platform work | Designed for multi-team enterprise use with established scaling practices |
| Vendor support and trust posture | Community/internal support only | Vendor-backed support, tested releases, and enterprise trust programs |

### Practical guidance

- Choose this repository when:
  - You want to learn quickly, prototype AI governance patterns, or build an
    internal platform customized to your organization.
  - You have engineering capacity to own operations, reliability, and long-term
    maintenance.

- Choose Kong/Konnect-style platforms when:
  - You need proven enterprise maturity now (SLA expectations, audited controls,
    support contracts, and broad integration coverage).
  - You prefer buying a trusted platform capability instead of building and
    operating one end-to-end.

### Decision checklist

Use this quick checklist with your architecture, platform, and security teams.

1. Do you need enterprise-grade SLA/support contracts in the next 1-2 quarters?
2. Do you need compliance-ready controls and audit evidence immediately?
3. Is your team able to own 24/7 operations (on-call, upgrades, incident response)?
4. Do you need broad third-party integrations out of the box right now?
5. Is minimizing initial license spend more important than minimizing internal build effort?
6. Do you need to ship a working AI gateway prototype in days rather than months?
7. Is long-term platform customization a strategic advantage for your organization?

Interpretation:
1. If you answered "yes" to most of 1-4, a Kong/Konnect-style platform is usually the lower-risk path.
2. If you answered "yes" to most of 5-7, this repository is usually the faster and more flexible starting point.
3. Hybrid approach: start with this repository for discovery/prototyping, then migrate to or integrate with an enterprise gateway as scale and compliance demands increase.

### Executive summary by role

| Role | Primary concern | This repository is strongest when... | Kong/Konnect-style platform is strongest when... |
| --- | --- | --- | --- |
| CTO | Delivery speed, strategic flexibility, total platform direction | You need rapid AI platform learning/prototyping and want to shape a custom internal architecture | You need predictable enterprise delivery outcomes with mature platform capabilities now |
| CISO | Risk posture, auditability, control coverage | You can incrementally build controls with close engineering-security collaboration and phased hardening | You need immediate enterprise trust posture, tested controls, and vendor-supported compliance operations |
| Platform Lead | Operability, scale, integration effort, team burden | You have platform engineering bandwidth to own reliability, integrations, and lifecycle operations | You want to reduce operational burden via proven gateway tooling, ecosystem integrations, and support channels |

Recommended alignment model:
1. Use this repository as a discovery and architecture accelerator in early phases.
2. Decide by milestone whether to continue self-managed hardening or adopt an enterprise gateway.
3. Keep API contracts and tenant-routing abstractions portable to preserve optionality.

## How it works

The `AIServiceGenerator` class in `main.py` accepts:

- `service_name`: the logical name of the AI service
- `service_type`: the service type (`llm`, `rag`, or `agent`)

When executed, the generator produces directories and files such as:

- `terraform/<service_name>/main.tf`
- `services/<service_name>/Dockerfile`
- `services/<service_name>/src/main.py`
- `services/<service_name>/tests/evaluation/test_evaluation.py`
- `.github/workflows/<service_name>.yml`
- `monitoring/<service_name>-dashboard.json`

## Getting started

1. Install required Python dependencies:

```powershell
pip install -r requirements.txt
```

2. Run the backend platform server:

```powershell
python main.py --serve
```

3. Open the API documentation at `http://127.0.0.1:8000/docs`.

4. Run the Next.js frontend to visualize the platform:

```powershell
cd frontend
npm install
npm run dev
```

5. Open the UI at `http://127.0.0.1:3000` to see service registration,
   security policies, platform summary, and a live RAG query demo.

## Visual tour

The frontend dashboard is designed to make the platform understandable at a
glance:

- the top hero shows the platform summary and key counts
- endpoint cards summarize the main API surfaces
- the service and policy panels show how governance is organized
- the RAG panel demonstrates a user-facing enterprise use case

6. Optionally generate sample service scaffolding artifacts:

```powershell
python main.py --generate
```

7. Inspect the generated service directories and customize them for your
  enterprise environment.

## Screenshot gallery

These screenshots were captured from the live frontend running against the
backend in this repository.

The middle and lower screenshots show infrastructure, security, provenance, and
tenant-aware routing patterns across the platform.

| Platform view | What it shows |
| --- | --- |
| ![Enterprise platform hero visual (SVG)](assets/readme/01-enterprise-platform-hero.svg) | Vector version of the same hero visual for crisp scaling in documentation and presentations. |
| ![Full dashboard with tenant access](assets/readme/02-full-dashboard-tenant-access.png) | Full-page platform view showing summary, governance, and multi-tenant model access together. |
| ![Tenant routing companion visual](assets/readme/02b-tenant-routing-companion.svg) | Companion visual for the shared endpoint view, showing tenant-specific model resolution, policy checks, and outcome telemetry. |
| ![Live RAG use case](assets/readme/03-live-rag-use-case.png) | A real prompt submitted through the dashboard and the grounded response returned by the backend. |


| ![Tenant access section focus](assets/readme/06-tenant-shared-api-focus.png) | Focused view of the tenant access section where one API is shared and policy tiers differ by team. |

| ![Swagger API docs for shared endpoint](assets/readme/08-api-docs-shared-endpoint.png) | The backend API docs that expose the shared POST /generate interface used by all tenants. |

### Tenant payload examples (same API, different LLM routing)

```json
POST /generate
{"tenant_id":"finance","model":"gpt-4.1-finance-safe","prompt":"Summarize Q3 revenue risk"}
```

```json
POST /generate
{"tenant_id":"legal","model":"llama-3.3-70b-legal","prompt":"Highlight indemnification concerns"}
```

```json
POST /generate
{"tenant_id":"support","model":"gpt-4.1-mini-support","prompt":"Generate empathetic resolution response"}
```

## Notes

- The generator is intentionally prototype-style and focuses on enterprise
  standardization rather than complete production readiness.
- The generated service code contains placeholder logic for security,
  model routing, and evaluation. It should be adapted to your actual
  model framework, cloud account, and governance policies.
- The current implementation assumes AWS infrastructure and GitHub Actions
  deployment patterns.

## Recommended next steps

- Add real Terraform variables, state management, and provider configuration.
- Replace stubbed model invocation and evaluation classes with your AI platform.
- Harden API security, authentication, and tenant isolation.
- Extend the generator to support additional enterprise patterns such as
  audit logging, feature flags, and multi-region deployment.
