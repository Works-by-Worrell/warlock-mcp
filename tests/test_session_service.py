from unittest.mock import MagicMock

# We expect this import to fail initially (Red TDD phase)
from worksbyworrell.warlock.service.session_service import AgentSessionService


def test_build_session_prompt_compiles_correctly():
    """
    Verify AgentSessionService fetches data from all three repositories
    and compiles the unified system prompt.
    """
    # 1. Arrange Mocks (Mockito equivalents)
    mock_agent_repo = MagicMock()
    mock_profile_repo = MagicMock()
    mock_skill_repo = MagicMock()

    mock_agent_repo.get_agent.return_value = {
        "agent_id": "torque",
        "name": "Torque Agent",
        "system_prompt": "You are Torque, the orchestration agent.",
    }

    mock_profile_repo.get_profile.return_value = {
        "username": "raworre",
        "role": "Lead Engineer",
        "public_prompt": "Public profile lore text.",
        "private_prompt": "Private profile constraints text.",
    }

    mock_skill_repo.get_skill.return_value = {
        "skill_id": "antigravity-guide",
        "system_prompt": "Guides the agent on using Antigravity.",
    }

    # 2. Act
    service = AgentSessionService(
        agent_repo=mock_agent_repo, profile_repo=mock_profile_repo, skill_repo=mock_skill_repo
    )
    prompt = service.build_session_prompt(
        agent_name="torque", username="raworre", skills="antigravity-guide"
    )

    # 3. Assert prompt content is stitched correctly
    assert "You are Torque, the orchestration agent." in prompt
    assert "Public profile lore text." in prompt
    assert "Private profile constraints text." in prompt
    assert "Guides the agent on using Antigravity." in prompt

    # Verify repository interactions
    mock_agent_repo.get_agent.assert_called_once_with("torque")
    mock_profile_repo.get_profile.assert_called_once_with("raworre")
    mock_skill_repo.get_skill.assert_called_once_with("antigravity-guide")


def test_build_session_prompt_handles_missing_skills():
    """Verify session service handles empty or whitespace skills strings gracefully."""
    mock_agent_repo = MagicMock()
    mock_profile_repo = MagicMock()
    mock_skill_repo = MagicMock()

    mock_agent_repo.get_agent.return_value = {"system_prompt": "Agent prompt"}
    mock_profile_repo.get_profile.return_value = {
        "public_prompt": "Public",
        "private_prompt": "Private",
    }

    service = AgentSessionService(
        agent_repo=mock_agent_repo, profile_repo=mock_profile_repo, skill_repo=mock_skill_repo
    )

    # Act with empty skills string
    prompt = service.build_session_prompt(agent_name="torque", username="raworre", skills="")

    # Assert
    assert "Agent prompt" in prompt
    assert "No specialized skills loaded" in prompt
    mock_skill_repo.get_skill.assert_not_called()
