import json
from unittest.mock import MagicMock

import pytest

from worksbyworrell.warlock.sync import (
    fetch_github_milestones,
    get_target_repository,
    parse_agent_markdown,
    sync_agent_specs_to_firestore,
    sync_all,
    sync_github_milestones_to_firestore,
)

# ============================================================================
# 1. TARGET REPOSITORY RESOLUTION TESTS
# ============================================================================


def test_get_target_repository_from_github_repository_env(monkeypatch):
    """
    Verify GITHUB_REPOSITORY environment variable takes top precedence (CI runner).
    """
    monkeypatch.setenv("GITHUB_REPOSITORY", "forked-org/custom-warlock-agents")
    monkeypatch.setenv("GH_REPO", "ignored-org/ignored-repo")

    repo = get_target_repository()
    assert repo == "forked-org/custom-warlock-agents"


def test_get_target_repository_from_gh_repo_env(monkeypatch):
    """
    Verify GH_REPO environment variable is resolved when GITHUB_REPOSITORY is absent.
    """
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
    monkeypatch.setenv("GH_REPO", "developer-user/warlock-agents-dev")

    repo = get_target_repository()
    assert repo == "developer-user/warlock-agents-dev"


def test_get_target_repository_from_git_remote(monkeypatch, mocker):
    """
    Verify local git remote origin URL is parsed when environment variables are missing.
    """
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
    monkeypatch.delenv("GH_REPO", raising=False)

    mock_completed_proc = MagicMock()
    mock_completed_proc.returncode = 0
    mock_completed_proc.stdout = "git@github.com:Works-by-Worrell/warlock-agents.git\n"

    mocker.patch("subprocess.run", return_value=mock_completed_proc)

    repo = get_target_repository()
    assert repo == "Works-by-Worrell/warlock-agents"


def test_get_target_repository_raises_value_error_when_unresolved(monkeypatch, mocker):
    """
    Verify ValueError is raised fail-fast when repository context cannot be resolved.
    """
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
    monkeypatch.delenv("GH_REPO", raising=False)

    mock_completed_proc = MagicMock()
    mock_completed_proc.returncode = 1
    mock_completed_proc.stdout = ""

    mocker.patch("subprocess.run", return_value=mock_completed_proc)

    with pytest.raises(ValueError) as exc_info:
        get_target_repository()

    assert "Unable to resolve target GitHub repository" in str(exc_info.value)


# ============================================================================
# 2. REST API & MARKDOWN PARSING TESTS
# ============================================================================


def test_fetch_github_milestones_success(mocker):
    """
    Verify fetch_github_milestones queries GitHub REST API and parses response array.
    """
    mock_milestones = [
        {
            "number": 1,
            "title": "Phase 1: Workspace Strategy",
            "state": "closed",
            "open_issues": 0,
            "closed_issues": 8,
            "html_url": "https://github.com/Works-by-Worrell/warlock-agents/milestone/1",
        }
    ]

    mock_response = MagicMock()
    mock_response.json.return_value = mock_milestones
    mock_response.raise_for_status.return_value = None

    mock_client = MagicMock()
    mock_client.get.return_value = mock_response
    mock_client.__enter__.return_value = mock_client
    mock_client.__exit__.return_value = None

    mocker.patch("httpx.Client", return_value=mock_client)

    result = fetch_github_milestones(repo="Works-by-Worrell/warlock-agents", token="dummy-pat")

    assert len(result) == 1
    assert result[0]["title"] == "Phase 1: Workspace Strategy"
    mock_client.get.assert_called_once_with(
        "https://api.github.com/repos/Works-by-Worrell/warlock-agents/milestones?state=all",
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Authorization": "Bearer dummy-pat",
        },
    )


def test_parse_agent_markdown_with_frontmatter(tmp_path):
    """
    Verify parse_agent_markdown parses YAML header attributes and markdown body.
    """
    spec_file = tmp_path / "clutch.md"
    spec_file.write_text(
        "---\n"
        "name: Clutch Core Agent\n"
        "model: gemini-1.5-pro\n"
        "---\n"
        "### Operational Instructions\n"
        "You are the primary orchestration agent."
    )

    parsed = parse_agent_markdown(str(spec_file))

    assert parsed["name"] == "Clutch Core Agent"
    assert parsed["model"] == "gemini-1.5-pro"
    assert "You are the primary orchestration agent." in parsed["system_prompt"]


def test_parse_agent_markdown_without_frontmatter(tmp_path):
    """
    Verify parse_agent_markdown handles plain markdown without frontmatter boundaries.
    """
    spec_file = tmp_path / "simple.md"
    spec_file.write_text("Plain instructions without frontmatter.")

    parsed = parse_agent_markdown(str(spec_file))

    assert parsed["system_prompt"] == "Plain instructions without frontmatter."


# ============================================================================
# 3. FIRESTORE & STATIC CACHE INTEGRATION TESTS
# ============================================================================


def test_sync_github_milestones_to_firestore_and_cache(
    monkeypatch, mock_firestore_client, tmp_path, mocker
):
    """
    Verify sync_github_milestones_to_firestore persists progress to Firestore and dumps static
    cache JSON.
    """
    monkeypatch.setenv("GCP_PROJECT_ID", "test-project")
    monkeypatch.setenv("GITHUB_REPOSITORY", "Works-by-Worrell/warlock-agents")

    mock_milestones = [
        {
            "number": 5,
            "title": "Phase 5: Ingress & Automation",
            "state": "open",
            "open_issues": 3,
            "closed_issues": 1,
            "html_url": "https://github.com/Works-by-Worrell/warlock-agents/milestone/5",
            "updated_at": "2026-07-20T21:44:47Z",
        }
    ]

    mocker.patch(
        "worksbyworrell.warlock.sync.fetch_github_milestones", return_value=mock_milestones
    )

    out_dir = str(tmp_path)
    result = sync_github_milestones_to_firestore(output_dir=out_dir)

    assert len(result) == 1
    assert result[0]["progress_percentage"] == 25.0

    # Verify Firestore set call
    mock_firestore_client.collection.assert_called_with("portfolio_milestones")
    mock_firestore_client.collection.return_value.document.assert_called_with("5")
    mock_firestore_client.collection.return_value.document.return_value.set.assert_called_once()

    # Verify static cache milestones.json file
    cache_file = tmp_path / "milestones.json"
    assert cache_file.exists()
    cached_data = json.loads(cache_file.read_text())
    assert cached_data[0]["milestone_id"] == 5
    assert cached_data[0]["progress_percentage"] == 25.0


def test_sync_agent_specs_to_firestore_and_cache(monkeypatch, mock_firestore_client, tmp_path):
    """
    Verify public specs sync to agent_configurations & agents.json, private overlays sync to
    agent_overlays.
    """
    monkeypatch.setenv("GCP_PROJECT_ID", "test-project")

    public_dir = tmp_path / ".public" / "agents"
    private_dir = tmp_path / ".private" / "agents"
    public_dir.mkdir(parents=True)
    private_dir.mkdir(parents=True)

    (public_dir / "torque.md").write_text("---\nname: Torque\n---\nPublic Torque Spec")
    (private_dir / "torque_overlay.md").write_text("---\nkey: sec_123\n---\nPrivate Overlay Spec")
    (private_dir / "README.md").write_text("Ignore me")

    result = sync_agent_specs_to_firestore(
        public_dir=str(public_dir), private_dir=str(private_dir), output_dir=str(tmp_path)
    )

    assert len(result) == 1
    assert result[0]["agent_id"] == "torque"

    # Verify public agents.json cache
    agents_cache = tmp_path / "agents.json"
    assert agents_cache.exists()
    cached_agents = json.loads(agents_cache.read_text())
    assert cached_agents[0]["agent_id"] == "torque"

    # Verify Firestore collection calls
    mock_firestore_client.collection.assert_any_call("agent_configurations")
    mock_firestore_client.collection.assert_any_call("agent_overlays")


def test_sync_all_orchestrates_both_pipelines(mocker):
    """
    Verify sync_all orchestrates milestone sync and agent spec sync with custom params.
    """
    mock_milestones_sync = mocker.patch(
        "worksbyworrell.warlock.sync.sync_github_milestones_to_firestore"
    )
    mock_agent_sync = mocker.patch(
        "worksbyworrell.warlock.sync.sync_agent_specs_to_firestore"
    )

    sync_all(
        repo="Works-by-Worrell/warlock-agents",
        token="dummy-token",
        public_dir="/tmp/public",
        private_dir="/tmp/private",
        output_dir="/tmp/test"
    )

    mock_milestones_sync.assert_called_once_with(
        repo="Works-by-Worrell/warlock-agents", token="dummy-token", output_dir="/tmp/test"
    )
    mock_agent_sync.assert_called_once_with(
        public_dir="/tmp/public", private_dir="/tmp/private", output_dir="/tmp/test"
    )


