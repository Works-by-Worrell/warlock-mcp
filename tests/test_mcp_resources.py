from unittest.mock import MagicMock

# Target resources modules under test
from worksbyworrell.warlock.resources.agents import agent_session, get_agent_persona
from worksbyworrell.warlock.resources.definitions import get_definition_of_ready
from worksbyworrell.warlock.resources.profiles import (
    get_combined_profile,
    get_private_profile,
    get_public_profile,
)
from worksbyworrell.warlock.resources.skills import get_skill_instructions

# ============================================================================
# 1. AGENTS RESOURCES INTEGRATION TESTS
# ============================================================================

def test_get_agent_persona_calls_repository(mocker):
    """Verify get_agent_persona delegates to get_agent_repository strategy."""
    # Mock repository
    mock_repo = MagicMock()
    mock_repo.get_agent.return_value = {
        "agent_id": "torque",
        "system_prompt": "Mocked Agent Persona Content"
    }
    
    # Patch the factory resolver to return our mock repo
    mocker.patch(
        "worksbyworrell.warlock.resources.agents.get_agent_repository",
        return_value=mock_repo
    )
    
    result = get_agent_persona("torque")
    
    assert "Mocked Agent Persona Content" in result
    mock_repo.get_agent.assert_called_once_with("torque")


def test_agent_session_calls_session_service(mocker):
    """Verify agent_session prompt delegates to AgentSessionService facade."""
    # Patch the session service instance's build_session_prompt method
    mock_build = mocker.patch(
        "worksbyworrell.warlock.resources.agents.session_service.build_session_prompt",
        return_value="Mocked Unified Session Prompt"
    )
    
    result = agent_session(agent_name="torque", username="raworre", skills="antigravity-guide")
    
    assert result == "Mocked Unified Session Prompt"
    mock_build.assert_called_once_with(
        agent_name="torque",
        username="raworre",
        skills="antigravity-guide"
    )


# ============================================================================
# 2. PROFILES RESOURCES INTEGRATION TESTS
# ============================================================================

def test_profile_resources_call_repository(mocker):
    """Verify profiles resources fetch and separate public/private content using profile repo."""
    mock_repo = MagicMock()
    mock_repo.get_profile.return_value = {
        "username": "raworre",
        "public_prompt": "Mocked Public Profile Content",
        "private_prompt": "Mocked Private Profile Content"
    }
    
    mocker.patch(
        "worksbyworrell.warlock.resources.profiles.get_profile_repository",
        return_value=mock_repo
    )
    
    # 1. Test Public Profile Resource
    public_res = get_public_profile("raworre")
    assert public_res == "Mocked Public Profile Content"
    
    # 2. Test Private Profile Resource
    private_res = get_private_profile("raworre")
    assert private_res == "Mocked Private Profile Content"
    
    # 3. Test Combined Profile Resource
    combined_res = get_combined_profile("raworre")
    assert "Mocked Public Profile Content" in combined_res
    assert "Mocked Private Profile Content" in combined_res
    
    # Verify repository was queried for the profiles
    assert mock_repo.get_profile.call_count >= 3


# ============================================================================
# 3. SKILLS RESOURCES INTEGRATION TESTS
# ============================================================================

def test_get_skill_instructions_calls_repository(mocker):
    """Verify get_skill_instructions delegates to skill repository."""
    mock_repo = MagicMock()
    mock_repo.get_skill.return_value = {
        "skill_id": "antigravity-guide",
        "system_prompt": "Mocked Skill Instructions Content"
    }
    
    mocker.patch(
        "worksbyworrell.warlock.resources.skills.get_skill_repository",
        return_value=mock_repo
    )
    
    result = get_skill_instructions("antigravity-guide")
    
    assert result == "Mocked Skill Instructions Content"
    mock_repo.get_skill.assert_called_once_with("antigravity-guide")


# ============================================================================
# 4. DEFINITIONS RESOURCES INTEGRATION TESTS
# ============================================================================

def test_get_definition_of_ready_calls_repository(mocker):
    """Verify definition of ready delegates to resource repository."""
    mock_repo = MagicMock()
    mock_repo.get_resource.return_value = {
        "resource_id": "definitions/ready",
        "system_prompt": "Mocked Definition of Ready Checklist"
    }
    
    mocker.patch(
        "worksbyworrell.warlock.resources.definitions.get_resource_repository",
        return_value=mock_repo
    )
    
    result = get_definition_of_ready()
    
    assert result == "Mocked Definition of Ready Checklist"
    mock_repo.get_resource.assert_called_once_with("definitions/ready")
