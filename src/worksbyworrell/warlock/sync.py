import datetime
import glob
import json
import os
import subprocess

import httpx
import yaml
from google.cloud import firestore

from worksbyworrell.warlock.core import PROJECT_ROOT
from worksbyworrell.warlock.storage.firestore_client import save_document


def get_target_repository() -> str:
    """
    Dynamically resolve target GitHub repository (owner/repo).
    Checks GITHUB_REPOSITORY (CI), GH_REPO (env), git remote origin, and fallback.
    """
    env_repo = os.environ.get("GITHUB_REPOSITORY") or os.environ.get("GH_REPO")
    if env_repo:
        return env_repo

    try:
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True,
            timeout=2.0,
        )
        if result.returncode == 0 and result.stdout.strip():
            url = result.stdout.strip()
            if "github.com" in url:
                repo_path = url.split("github.com")[-1].lstrip(":/")
                if repo_path.endswith(".git"):
                    repo_path = repo_path[:-4]
                if repo_path:
                    return repo_path
    except Exception:
        pass

    raise ValueError(
        "Unable to resolve target GitHub repository. "
        "Please set GITHUB_REPOSITORY or GH_REPO environment variable."
    )


def fetch_github_milestones(repo: str | None = None, token: str | None = None) -> list[dict]:
    """
    Fetch milestones for the target repository from GitHub REST API.
    """
    repo_path = repo or get_target_repository()
    url = f"https://api.github.com/repos/{repo_path}/milestones?state=all"
    token = token or os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Authorization": f"Bearer {token}",
    }

    with httpx.Client() as client:
        resp = client.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json()


def parse_agent_markdown(file_path: str) -> dict:
    """
    Parse YAML frontmatter and Markdown body from an agent specification file.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = yaml.safe_load(parts[1]) or {}
            body = parts[2].strip()
            return {**frontmatter, "system_prompt": body}

    return {"system_prompt": content.strip()}


def sync_github_milestones_to_firestore(
    repo: str | None = None, token: str | None = None, output_dir: str = "."
) -> list[dict]:
    """
    Fetch GitHub milestones, write to Firestore (if configured), and dump static JSON cache.
    """
    milestones = fetch_github_milestones(repo, token)

    processed = []

    db = (
        firestore.Client()
        if os.environ.get("GCP_PROJECT_ID") or os.environ.get("GOOGLE_CLOUD_PROJECT")
        else None
    )

    for milestone in milestones:
        open_issues = milestone.get("open_issues", 0)
        closed_issues = milestone.get("closed_issues", 0)
        total = open_issues + closed_issues
        progress = round((closed_issues / total * 100), 2) if total > 0 else 0.0

        payload = {
            "milestone_id": milestone["number"],
            "title": milestone["title"],
            "description": milestone.get("description") or "",
            "state": milestone["state"],
            "open_issues": open_issues,
            "closed_issues": closed_issues,
            "progress_percentage": progress,
            "github_url": milestone.get("html_url", ""),
            "updated_at": milestone.get("updated_at"),
            "synced_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }

        processed.append(payload)

        if db:
            save_document("portfolio_milestones", milestone["number"], payload, client=db)

    os.makedirs(output_dir, exist_ok=True)
    cache_path = os.path.join(output_dir, "milestones.json")
    with open(cache_path, "w") as f:
        json.dump(processed, f, indent=2)
    return processed


def sync_agent_specs_to_firestore(
    public_dir: str = ".public/agents", private_dir: str = ".private/agents", output_dir: str = "."
) -> list[dict]:
    """
    Parse public agent specs into Firestore agent_configurations and private overlays into
    agent_overlays.
    """
    db = (
        firestore.Client()
        if os.environ.get("GCP_PROJECT_ID") or os.environ.get("GOOGLE_CLOUD_PROJECT")
        else None
    )
    public_agents = []

    if not os.path.isabs(public_dir) and not os.path.exists(public_dir):
        alt_public = os.path.join(PROJECT_ROOT, public_dir)
        if os.path.exists(alt_public):
            public_dir = alt_public

    if not os.path.isabs(private_dir) and not os.path.exists(private_dir):
        alt_private = os.path.join(PROJECT_ROOT, private_dir)
        if os.path.exists(alt_private):
            private_dir = alt_private

    for spec_file in sorted(glob.glob(os.path.join(public_dir, "*.md"))):
        agent_id = os.path.splitext(os.path.basename(spec_file))[0]
        data = parse_agent_markdown(spec_file)
        data["agent_id"] = agent_id
        public_agents.append(data)

        if db:
            save_document("agent_configurations", agent_id, data, client=db)

    for spec_file in sorted(glob.glob(os.path.join(private_dir, "*.md"))):
        agent_id = os.path.splitext(os.path.basename(spec_file))[0]
        data = parse_agent_markdown(spec_file)
        data["agent_id"] = agent_id

        if db:
            save_document("agent_overlays", agent_id, data, client=db)

    os.makedirs(output_dir, exist_ok=True)
    cache_path = os.path.join(output_dir, "agents.json")
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(public_agents, f, indent=2)

    return public_agents


def sync_all(
    repo: str | None = None,
    token: str | None = None,
    public_dir: str = ".public/agents",
    private_dir: str = ".private/agents",
    output_dir: str = ".",
) -> None:
    """
    Execute full synchronization pipeline for milestones and agent specs.
    """
    sync_github_milestones_to_firestore(repo=repo, token=token, output_dir=output_dir)
    sync_agent_specs_to_firestore(
        public_dir=public_dir, private_dir=private_dir, output_dir=output_dir
    )
