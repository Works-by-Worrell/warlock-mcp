# Works-by-Worrell: Warlock MCP Application Core (`warlock-mcp`)

This repository houses the core application logic, domain models, and ingestion pipelines for **Warlock**, a specialized Model Context Protocol (MCP) server built on top of the FastMCP Python framework.

---

## 1. System Architecture & Design Patterns

The codebase is refactored following **Domain-Driven Design (DDD)** and architectural decoupling patterns to isolate dependencies and support flexible environments:

```
warlock-mcp/
├── .githooks/                # Shared, version-controlled git validation hooks
│   └── commit-msg            # Enforces Conventional Commit standards with issue tags
├── python-app/
│   ├── src/
│   │   └── worksbyworrell/
│   │       └── warlock/
│   │           ├── main.py   # FastMCP application entry point (ASGI server bootstrap)
│   │           ├── pipeline/ # Decoupled Ingestion Pipelines (Clean Ingress)
│   │           ├── repository/ # DDD Data Repository Contracts & Implementations
│   │           │   ├── agent.py
│   │           │   ├── profile.py
│   │           │   ├── resource.py
│   │           │   └── skill.py
│   │           └── service/  # Facade Pattern Business Logic Layer
│   │               └── session.py
│   └── tests/                # Automated pytest suites (Yellowstone-compliant)
└── Dockerfile                # Multi-stage image build for server & CLI runner
```

### Core Design Patterns
*   **Domain-Driven Design (DDD) Repositories:** All data access is mediated by specific repository interfaces (`AgentRepository`, `UserProfileRepository`, etc.). This separates business logic from data storage mechanisms.
*   **Strategy Pattern (Storage Resolution):** The repositories support both a `Firestore` backend (using Google Cloud Firestore API) and a `Local` backend (utilizing local JSON/markdown files). Storage strategy resolution is bound strictly to the `GCP_PROJECT_ID` environment variable. If unset, it cleanly falls back to local strategies.
*   **Facade Pattern (Service Layer):** The `AgentSessionService` injects multiple repositories to orchestrate session creation, prompt tokenization, and metadata assembly under a unified interface (`agent_session()`).
*   **Pipeline Pattern (Framework Isolation):** The `ConfigIngestionPipeline` handles synchronization of public and private configurations to the database. It is completely isolated from the FastMCP runtime engine, allowing independent imports and zero-dependency command line executions.

---

## 2. Config Sync CLI & Ingestion Pipeline

The CLI module `worksbyworrell.warlock.pipeline` executes configuration seeding and synchronizations.

### Key Ingestion Features
*   **Zero-Dependency Execution:** Ingestion helper libraries do not import FastMCP, ensuring lightweight CLI executions.
*   **MD5 Delta-Syncing:** Calculates MD5 checksums of local config files and applies updates to Firestore only when data has drifted, saving database writes.
*   **Strict Traceability:** Ingests document properties alongside their Git `$GITHUB_SHA` hash as a version flag for configuration auditing.

---

## 3. Local Development & Testing

### Installation
Set up a python virtual environment and install the development dependencies:
```bash
cd python-app
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Running Tests
Execute the unit testing suite to verify repository mocks and domain models:
```bash
PYTHONPATH=src pytest tests/
```

---

## 4. CI/CD Build & Container Packaging

The build pipeline publishes two specialized container images utilizing **double-tagging** (pinning every release to both a semantic version and a Git short-SHA):

1.  **`warlock-mcp` (ASGI Server runtime):** Serves FastMCP actions over the Streamable-HTTP ASGI transport.
2.  **`warlock-mcp-syncer` (Sync CLI client):** Standalone container runner that mounts configuration directories and runs sync commands in GitOps workflows.
