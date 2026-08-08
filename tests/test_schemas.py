import pytest
from pydantic import ValidationError

from worksbyworrell.warlock.schemas.agent import AgentConfigSchema
from worksbyworrell.warlock.schemas.profile import UserProfileSchema
from worksbyworrell.warlock.schemas.resource import ResourceSchema
from worksbyworrell.warlock.schemas.skill import SkillMetadataSchema

# ============================================================================
# 1. AGENT SCHEMAS TESTS
# ============================================================================

def test_agent_config_schema_valid():
    """Verify valid agent configurations compile cleanly."""
    data = {
        "agent_id": "torque-agent",
        "name": "Torque Orchestration Agent",
        "system_prompt": "You are Torque.",
        "metadata": {"model": "gemini-2.0"}
    }
    schema = AgentConfigSchema(**data)
    assert schema.agent_id == "torque-agent"
    assert schema.name == "Torque Orchestration Agent"


def test_agent_config_schema_invalid_id():
    """Verify agent_id enforces strict kebab-case constraints."""
    invalid_data = {
        "agent_id": "Torque_Agent!",  # Violates '^[a-z0-9-_]+$'
        "name": "Torque",
        "system_prompt": "Prompt"
    }
    with pytest.raises(ValidationError):
        AgentConfigSchema(**invalid_data)


def test_agent_config_schema_missing_fields():
    """Verify missing required fields raise ValidationError."""
    with pytest.raises(ValidationError):
        AgentConfigSchema(agent_id="torque")  # Missing name and system_prompt


# ============================================================================
# 2. USER PROFILE SCHEMAS TESTS
# ============================================================================

def test_user_profile_schema_valid():
    """Verify user profile schema compiles with valid inputs."""
    data = {
        "username": "raworre",
        "system_prompt": "Lore and alignment details.",
        "metadata": {"role": "Lead Engineer"}
    }
    schema = UserProfileSchema(**data)
    assert schema.username == "raworre"
    assert schema.metadata.get("role") == "Lead Engineer"


def test_user_profile_schema_invalid_username():
    """Verify username enforces alphanumeric boundaries."""
    invalid_data = {
        "username": "raworre space!",  # Invalid characters
        "system_prompt": "Public Lore details."
    }
    with pytest.raises(ValidationError):
        UserProfileSchema(**invalid_data)


# ============================================================================
# 3. SKILL SCHEMAS TESTS
# ============================================================================

def test_skill_metadata_schema_valid():
    """Verify skill metadata parses correctly."""
    data = {
        "skill_id": "antigravity-guide",
        "name": "Antigravity Guide",
        "description": "Guides the agent on using Antigravity.",
        "system_prompt": "Skill prompt details."
    }
    schema = SkillMetadataSchema(**data)
    assert schema.skill_id == "antigravity-guide"


# ============================================================================
# 4. RESOURCE SCHEMAS TESTS
# ============================================================================

def test_resource_schema_valid():
    """Verify system resource schema validation."""
    data = {
        "resource_id": "definition-of-ready",
        "name": "Definition of Ready",
        "system_prompt": "Definition of ready checklist.",
        "metadata": {
            "description": "Repository definition of ready.",
            "uri": "resource://definition-of-ready",
            "mime_type": "text/markdown"
        }
    }
    schema = ResourceSchema(**data)
    assert schema.resource_id == "definition-of-ready"
