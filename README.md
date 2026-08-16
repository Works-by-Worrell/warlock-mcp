# Works-by-Worrell: Warlock MCP Core (`warlock-mcp`)

This repository houses the core application logic and domain models for **Warlock**, a specialized Model Context Protocol (MCP) server built on top of the FastMCP Python framework. 

Warlock acts as the **Universal Cognitive Bootstrapper** for the Works-by-Worrell ecosystem. It bridges the gap between public execution tools (agents, IDEs) and the private GitOps data layer (prompts, rules, schemas) without requiring centralized cloud infrastructure.

---

## 1. System Architecture: The Local Gateway

Following the serverless extrication strategy ([ADR 0007](https://github.com/Works-by-Worrell/wbw-architecture/tree/main/initiatives/0007-local-mcp-extrication)), Warlock MCP is designed to run exclusively as a **decentralized, local edge-execution process**.

It exposes a standardized MCP interface over `stdio`, allowing any compliant client (e.g., Cursor, Claude Desktop, Antigravity CLI, or autonomous scripts like Eldritch Harvester) to seamlessly fetch organizational context and execute proprietary tools.

### Core Design Patterns
*   **Domain-Driven Design (DDD):** All data access is mediated by specific repository interfaces (`AgentRepository`, `UserProfileRepository`, etc.).
*   **API-Driven State:** Warlock fetches organizational configuration dynamically. By providing a `GITHUB_API_KEY`, Warlock natively queries the private GitOps config repositories via REST, entirely eliminating the need for Firestore or complex database syncing pipelines.
*   **Frictionless Transport:** By defaulting to `stdio`, Warlock integrates directly into IDEs as a subprocess, requiring no open ports, persistent HTTP servers, or complex network routing.

---

## 2. Containerized Execution (Frictionless Onboarding)

To enforce strict immutability and eliminate Python environment setup (`uv`/`venv`), the Warlock MCP Server is distributed as a public Docker container via the GitHub Container Registry (GHCR).

### Running Warlock MCP Locally
You can boot Warlock instantly from any machine with Docker installed:

```bash
docker run -i --rm \
  --env-file ~/.wbw/.env \
  ghcr.io/works-by-worrell/warlock-mcp:latest \
  --transport stdio
```

*Note: The `-i` (interactive) flag is required so standard I/O streams pass through correctly to the FastMCP server.*

> [!WARNING]
> **Windows/WSL Users:** You must have Docker Desktop running on your Windows host, and you must explicitly enable **WSL Integration** for your specific Linux distro (`Settings > Resources > WSL Integration > [x] Ubuntu`). If Docker is not running or integrated, the MCP connection will crash parsing the Docker error string.

---

## 3. Local Development

If you are actively developing new tools or resources for Warlock, you can run it natively using `uv`:

### Installation
Set up a python virtual environment and sync the development dependencies:
```bash
uv sync
```

### Running Tests
Execute the unit testing suite:
```bash
uv run pytest tests/
```

### Local CLI Execution
```bash
uv run python -m worksbyworrell.warlock.main --transport stdio
```

---

## 4. CI/CD Publishing Pipeline

The build pipeline automatically packages and publishes the `warlock-mcp` container image to **GHCR** on every push to the `main` branch. 

*   Images are double-tagged with both the semantic version from `pyproject.toml` and the Git short-SHA.
*   The legacy Google Artifact Registry and Cloud Run deployments have been fully deprecated and removed from the pipeline.
