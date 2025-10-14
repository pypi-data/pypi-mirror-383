Lifesaver Lite LLM

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/lifesaver-lite-llm.svg)](https://pypi.org/project/lifesaver-lite-llm/)

Overview
- Lightweight toolkit to ingest, analyze, and optimize LLM usage. Includes a simple dashboard, CLI analytics, and optional mitmweb-based live ingestion.
- Offline-friendly with vendored assets and deterministic tests. No secrets or large models committed.

Prerequisites
- Python 3.10+
- Optional: Docker (for mitmweb), make

Quickstart
- Create env and install
  - python -m venv .venv && source .venv/bin/activate
  - pip install -r requirements.txt -r requirements-dev.txt
  - pip install -e .
- CLI analytics (ingest + analyze)
  - lifesaver-lite-llm --db data/analysis.db ingest --input examples/sample_requests.json
  - lifesaver-lite-llm --db data/analysis.db analyze --out reports/report.md
- Dashboard (upload mode)
  - ./run.sh dashboard --upload examples/sample.har
- Live follow (mitmweb)
  - make mitm-up  # mitmweb UI at http://localhost:8081, proxy :8080
  - MITMWEB_URL=http://localhost:8081 ./run.sh dashboard --upload ""
 - Health checks
   - make health           # router + dashboard + mitmweb
   - make health-router    # GET http://localhost:4000/health
   - make health-dashboard # GET /api/status
   - make health-mitm      # GET MITMWEB_URL (default :8081)

Run Tests & Lint
- pytest -q  (ensure package is installed with pip install -e .; alternatively run with PYTHONPATH=src)
- ruff check .
- black .

CLI Highlights
- Ingest HAR/.mitm/JSON and analyze usage
  - make all INPUT=examples/sample_requests.json
  - lifesaver-lite-llm export flows --out exports/flows.json --since now-1h --redact 1
- magic-cli (agentic REPL + router helpers)
  - docs/AGENT.md
  - Agent via router (no provider-specific CLI):
    - make agent-router-repl MODEL=gpt-4o-mini
    - make agent-router-chat MSG="Hello" MODEL=gpt-4o-mini
    - Claude via router: make agent-claude-repl MODEL=claude-3-haiku-20240307
      and make agent-claude-chat MSG="Hello" MODEL=claude-3-haiku-20240307

Dashboard
- Pages: /, /flows, /timeline, /graph, /techniques
- APIs: /api/status, /api/flows, /api/graph, /api/techniques, /api/flow/{id}
- Basic Auth: set DASH_BASIC_USER and DASH_BASIC_PASS
 - Health: make health-dashboard

Environment
- Core: LITELLM_MASTER_KEY, LITELLM_SALT_KEY, STORE_MODEL_IN_DB, DATABASE_URL, PORT
- Dashboard: DASHBOARD_PORT, DB_PATH, PROVIDERS_PATH, MITMWEB_URL, MITMWEB_COOKIE, DASH_BASIC_USER/PASS

Docs
- Start with docs/INTRODUCTION.md and docs/GETTING_STARTED.md
- See docs/DASHBOARD.md, docs/ARCHITECTURE.md, docs/INGESTION.md, docs/SECURITY.md
- One-file context: docs/PROJECT_CONTEXT.md (combined docs/prompts)
 - Health checks and liftoff scenarios are documented in Makefile (make menu)

Project Layout
- src/lifesaver_lite_llm/: core package modules
- tests/: unit/integration tests
- configs/: provider presets and settings
- examples/: minimal inputs
- assets/: vendored static assets
- scripts/: helper scripts

License
- MIT. See LICENSE for details.
