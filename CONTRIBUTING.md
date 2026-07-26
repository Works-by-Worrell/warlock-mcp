# Contributing to Warlock MCP Core (`warlock-mcp`)

This document outlines the branch taxonomy, commit message standards, and workflows specifically for the **warlock-mcp** application repository.

---

## 1. Branch Strategy & Taxonomy

All development work MUST occur on a feature or task branch before targeting the `main` branch. All branches MUST align with one of the following prefix categories:

### Branch Prefix Categories
*   `feat/` - Application feature delivery (e.g. FastMCP endpoints, services, repository layers)
*   `fix/` - Immediate bug triage, logic corrections, and error patches
*   `test/` - Verification frameworks, mock configurations, and test suite enhancements
*   `docs/` - Runbook updates, setup guides, and repository README documentation
*   `chore/` - Maintenance, dependency updates, and workspace configuration adjustments

### Branch Naming Convention
All branches MUST follow this format: 
`<type>/issue-<id>-<description>` or `<type>/phase<num>-<short-description>`

**Examples:**
*   `feat/phase4-ddd-repositories`
*   `fix/issue-2-schema-validation`
*   `test/issue-5-mock-tests`

---

## 2. Commit Message Conventions

We strictly adhere to the [Conventional Commits](https://www.conventionalcommits.org/) specification. This enables automated release notes, changelog generation, and clear system auditability.

### Commit Format
Commit messages MUST follow the structure:
```
<type>(<scope>): <short description> (#<issue-number>)

[Optional body explaining design rationale or context]
```
*Note: A git validation hook is configured to enforce that all commit messages end with a parenthesized issue reference (e.g. `(#1)`).*

### Scope Boundaries (Repository Specific)
When writing a commit, the `scope` MUST represent the logical area of this codebase:

| Scope | Logical Domain | Example |
| :--- | :--- | :--- |
| `mcp` | FastMCP server, ASGI transport setup, resources, and tools | `feat(mcp): implement streamable-http ASGI transport (#5)` |
| `repo` | DDD repositories (agent, user profile, skill metadata repos) | `feat(repo): add FirestoreAgentRepository implementation (#1)` |
| `pipeline` | Config sync ingestion pipeline logic | `feat(pipeline): calculate MD5 checksums for delta-sync (#3)` |
| `schema` | Schema definitions and Pydantic validators | `fix(schema): correct email format in UserProfile model (#2)` |
| `test` | Unit and integration test suites | `test(test): add mock tests for Firestore sync (#1)` |
| `gov` | Governance, blueprints, templates, or repository setup | `docs(gov): write developer setup guide in README (#6)` |

---

## 3. Local Git Hook Installation

To enforce these formatting rules locally and prevent commit aborts, you MUST configure your local repository to execute the shared git validation hook:

```bash
git config core.hooksPath .githooks
```
Once configured, the script [.githooks/commit-msg](.githooks/commit-msg) will run automatically before every commit to validate the message format.
