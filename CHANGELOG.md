# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-08-15

### Added
- **Universal Cognitive Bootstrapper:** Official stabilization of the local `stdio` Transport mechanism for IDE integration.
- **GHCR Pipeline:** CI/CD pipeline now double-tags and publishes Docker containers directly to GitHub Container Registry, triggering strictly on semantic version tags (`v*.*.*`).
- GitHub REST API data provider for fetching the GitOps context layer without cloud persistence.

### Changed
- Refactored `warlock-mcp` to act exclusively as a local edge-execution agent gateway.
- Repurposed the `warlock-mcp` container image to eliminate Python/`uv` dependencies on end-user machines (Frictionless Onboarding).

### Removed
- **DEPRECATED:** Google Cloud Platform (GCP) infrastructure dependencies.
- **DEPRECATED:** Cloud Run ASGI Streamable-HTTP execution pipelines.
- **DEPRECATED:** Firestore database synchronization routines and `GCSCacheManager`.
- **DEPRECATED:** Google Artifact Registry and WIF authentication deployment pipelines.
