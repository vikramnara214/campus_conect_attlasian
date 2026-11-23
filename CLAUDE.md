# CampusContext — Zero-Onboarding Knowledge Graph Platform

## Project Overview
A unified context and contributor-routing platform targeting two hackathons:
1. **Sprint 1 (Due Dec 11, 2026): Relate by Neo4j Hackathon** — Embedded `.rl` knowledge graph (`./data/campus.rl`), automated Git ingestion, MCP server, and lightweight Campus Discovery Web UI.
2. **Sprint 2 (Due Dec 23, 2026): Atlassian Codegeist 2026** — Atlassian Forge app (`jira:issuePanel`, `rovo:agent`, `rovo:mcp`, `action`) connecting to the Sprint 1 backend via **Forge Remote**.

## Strict Zero-Cost Guardrails (DO NOT VIOLATE)
- **NEVER** use Atlassian Forge LLMs or Forge Containers (both bill from the first call).
- **ALWAYS** route Forge app calls to our external Node.js/Python backend via `Forge Remote` (`remotes:` in `manifest.yml`).
- Keep `console.log()` minimal in Forge functions to stay under the 1 GB/month free log quota.
- Use Relate's embedded single-file storage (`./data/campus.rl`)—do not spin up paid cloud Neo4j AuraDB instances unless explicitly requested.

## Tech Stack & Monorepo Layout
- `/backend` — Node.js (TypeScript) or Python (FastAPI) API wrapping **Relate by Neo4j** (`./data/campus.rl`), handling Git webhooks, Cypher queries, and exposing REST + MCP endpoints.
- `/web` — Lightweight Next.js / React Campus Discovery Portal (Sprint 1 demo).
- `/forge-app` — Atlassian Forge app (`manifest.yml`, `jira:issuePanel`, `rovo:agent`, `rovo:mcp`, `action` modules) (Sprint 2 demo).
- `/data` — Local `.rl` database files (`campus.rl`) and seed scripts (git-ignored except small demo fixtures).

## Knowledge Graph Schema (Relate / openCypher)
- **Ingested automatically via `relate run git-to-graph` & `fs-to-graph`:** commits, people/authors, files, folders (`TOUCHED`, `CO_CHANGED`, `CONTAINS`).
- **Custom Application Nodes:** `(:Project)`, `(:Feature)`, `(:Suggestion)`, `(:Skill)`
- **Custom Relationships:** `[:BELONGS_TO]`, `[:NEEDS_SKILL]`, `[:SUGGESTED_FOR]`, `[:COLLABORATES_ON]`

## Coding Standards (Ponytail / YAGNI)
- Prefer standard libraries and Relate's native CLI/extensions (`git-to-graph`, `fs-to-graph`, `relate serve --mcp`) over custom wrappers.
- Keep endpoints thin and stateless; let Cypher do the relationship traversal.
- Every new Cypher query must include a `LIMIT` clause so agent responses stay fast and within token budgets.
- Do not add auth/RBAC boilerplate in Sprint 1; use mock campus user profiles until Sprint 2 Forge OAuth.

## Commands
- Ingest a sample repo: `relate run git-to-graph <repo-dir> -d ./data/campus.rl`
- Run Relate MCP server: `relate serve --mcp stdio --database ./data/campus.rl --read-only`
- Forge deploy (Sprint 2): `cd forge-app && forge deploy && forge install`