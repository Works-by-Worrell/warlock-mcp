import logging

import pytest
from pydantic import ValidationError

# We import the functions to test (these will initially fail to import during Red-TDD)
try:
    from worksbyworrell.warlock.pipeline.validator import (
        validate_agent_config,
        validate_agent_overlay,
        validate_skill_metadata,
        validate_system_resource,
        validate_user_profile,
    )
except ImportError:
    validate_agent_config = None
    validate_agent_overlay = None
    validate_user_profile = None
    validate_system_resource = None
    validate_skill_metadata = None


# Ensure mock functions/modules exist for RED TDD execution
def test_validator_modules_are_defined():
    assert validate_agent_config is not None, "validate_agent_config is not yet defined."
    assert validate_agent_overlay is not None, "validate_agent_overlay is not yet defined."
    assert validate_user_profile is not None, "validate_user_profile is not yet defined."
    assert validate_system_resource is not None, "validate_system_resource is not yet defined."
    assert validate_skill_metadata is not None, "validate_skill_metadata is not yet defined."


# ============================================================================
# 1. AGENT CONFIG VALIDATION TESTS
# ============================================================================

@pytest.mark.skipif(validate_agent_config is None, reason="Validator module not yet implemented.")
def test_validate_agent_config_success():
    valid_data = {
        "agent_id": "torque-agent",
        "name": "Torque",
        "system_prompt": "You are Torque.",
        "metadata": {"model": "gemini-2.0"}
    }
    result = validate_agent_config(valid_data)
    assert result["agent_id"] == "torque-agent"
    assert result["name"] == "Torque"
    assert result["system_prompt"] == "You are Torque."


@pytest.mark.skipif(validate_agent_config is None, reason="Validator module not yet implemented.")
def test_validate_agent_config_invalid(caplog):
    invalid_data = {
        "agent_id": "Torque_Agent!",  # Invalid character (regex constraint)
        "name": "",                  # Empty name (min_length constraint)
        "system_prompt": "Prompt"
    }
    with caplog.at_level(logging.ERROR):
        with pytest.raises(ValidationError):
            validate_agent_config(invalid_data)
    
    # Assert that detailed error was logged to stderr/logging
    assert len(caplog.records) > 0
    assert any("validation" in r.message.lower() for r in caplog.records)


# ============================================================================
# 2. AGENT OVERLAY VALIDATION TESTS
# ============================================================================

@pytest.mark.skipif(validate_agent_overlay is None, reason="Validator module not yet implemented.")
def test_validate_agent_overlay_success():
    valid_data = {
        "agent_id": "torque-overlay",
        "system_prompt": "Override prompt.",
        "metadata": {"custom": "value"}
    }
    result = validate_agent_overlay(valid_data)
    assert result["agent_id"] == "torque-overlay"
    assert result["system_prompt"] == "Override prompt."


@pytest.mark.skipif(validate_agent_overlay is None, reason="Validator module not yet implemented.")
def test_validate_agent_overlay_invalid(caplog):
    invalid_data = {
        "agent_id": "invalid/id",  # Invalid character
        "system_prompt": ""
    }
    with caplog.at_level(logging.ERROR):
        with pytest.raises(ValidationError):
            validate_agent_overlay(invalid_data)
    
    assert len(caplog.records) > 0


# ============================================================================
# 3. USER PROFILE VALIDATION TESTS
# ============================================================================

@pytest.mark.skipif(validate_user_profile is None, reason="Validator module not yet implemented.")
def test_validate_user_profile_success():
    valid_data = {
        "username": "raworre",
        "system_prompt": "User details.",
        "metadata": {"role": "Lead Engineer"}
    }
    result = validate_user_profile(valid_data)
    assert result["username"] == "raworre"
    assert result["system_prompt"] == "User details."


@pytest.mark.skipif(validate_user_profile is None, reason="Validator module not yet implemented.")
def test_validate_user_profile_invalid(caplog):
    invalid_data = {
        "username": "raworre space!",  # Invalid spaces/chars
        "system_prompt": "Prompt"
    }
    with caplog.at_level(logging.ERROR):
        with pytest.raises(ValidationError):
            validate_user_profile(invalid_data)
            
    assert len(caplog.records) > 0


# ============================================================================
# 4. SYSTEM RESOURCE VALIDATION TESTS
# ============================================================================

@pytest.mark.skipif(validate_system_resource is None, reason="Validator module not yet implemented.")
def test_validate_system_resource_success():
    valid_data = {
        "resource_id": "definition-of-done",
        "name": "Definition of Done",
        "system_prompt": "Done checklist.",
        "metadata": {"uri": "resource://done", "mime_type": "text/markdown"}
    }
    result = validate_system_resource(valid_data)
    assert result["resource_id"] == "definition-of-done"
    assert result["name"] == "Definition of Done"


@pytest.mark.skipif(validate_system_resource is None, reason="Validator module not yet implemented.")
def test_validate_system_resource_invalid(caplog):
    invalid_data = {
        "resource_id": "invalid_id_value",
        "name": "",  # Missing/empty name
        "system_prompt": "Prompt"
    }
    with caplog.at_level(logging.ERROR):
        with pytest.raises(ValidationError):
            validate_system_resource(invalid_data)
            
    assert len(caplog.records) > 0


# ============================================================================
# 5. SKILL METADATA VALIDATION TESTS
# ============================================================================

@pytest.mark.skipif(validate_skill_metadata is None, reason="Validator module not yet implemented.")
def test_validate_skill_metadata_success():
    valid_data = {
        "skill_id": "git-operations",
        "system_prompt": "Helper instructions.",
        "metadata": {"tags": ["git"]}
    }
    result = validate_skill_metadata(valid_data)
    assert result["skill_id"] == "git-operations"
    assert result["system_prompt"] == "Helper instructions."


@pytest.mark.skipif(validate_skill_metadata is None, reason="Validator module not yet implemented.")
def test_validate_skill_metadata_invalid(caplog):
    invalid_data = {
        "skill_id": "Git_Operations_Invalid!",
        "system_prompt": ""
    }
    with caplog.at_level(logging.ERROR):
        with pytest.raises(ValidationError):
            validate_skill_metadata(invalid_data)
            
    assert len(caplog.records) > 0
