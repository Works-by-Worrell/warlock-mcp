from unittest.mock import MagicMock

import pytest

from worksbyworrell.warlock.tools.governance import fetch_org_agent


@pytest.mark.anyio
async def test_fetch_org_agent_success(mocker):
    """Verify fetch_org_agent retrieves agent prompt via AgentRepository."""
    mock_repo = MagicMock()
    mock_repo.get_agent.return_value = {
        "agent_id": "torque",
        "system_prompt": "You are Torque, a high-performance engine agent.",
    }

    mocker.patch(
        "worksbyworrell.warlock.tools.governance.get_agent_repository",
        return_value=mock_repo,
    )

    result = await fetch_org_agent("torque")

    assert result == "You are Torque, a high-performance engine agent."
    mock_repo.get_agent.assert_called_once_with("torque")


@pytest.mark.anyio
async def test_fetch_org_agent_not_found(mocker):
    """Verify fetch_org_agent returns a clear error when agent is not found."""
    mock_repo = MagicMock()
    mock_repo.get_agent.return_value = {
        "agent_id": "unknown_agent",
        "system_prompt": "Error: No configuration found for agent 'unknown_agent'",
    }

    mocker.patch(
        "worksbyworrell.warlock.tools.governance.get_agent_repository",
        return_value=mock_repo,
    )

    result = await fetch_org_agent("unknown_agent")

    assert "Error" in result
    assert "unknown_agent" in result
    mock_repo.get_agent.assert_called_once_with("unknown_agent")


@pytest.mark.anyio
async def test_fetch_org_agent_missing_system_prompt(mocker):
    """Verify fetch_org_agent returns clear error when system prompt is missing."""
    mock_repo = MagicMock()
    mock_repo.get_agent.return_value = {"agent_id": "empty_agent"}

    mocker.patch(
        "worksbyworrell.warlock.tools.governance.get_agent_repository",
        return_value=mock_repo,
    )

    result = await fetch_org_agent("empty_agent")

    assert "Error" in result
    assert "empty_agent" in result
    mock_repo.get_agent.assert_called_once_with("empty_agent")


@pytest.mark.anyio
async def test_fetch_org_agent_exception_handled(mocker):
    """Verify fetch_org_agent handles repository exceptions gracefully."""
    mock_repo = MagicMock()
    mock_repo.get_agent.side_effect = Exception("Repository connection failure")

    mocker.patch(
        "worksbyworrell.warlock.tools.governance.get_agent_repository",
        return_value=mock_repo,
    )

    result = await fetch_org_agent("failing_agent")

    assert "Error" in result
    assert "Repository connection failure" in result
    mock_repo.get_agent.assert_called_once_with("failing_agent")
