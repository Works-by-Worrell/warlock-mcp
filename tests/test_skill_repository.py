import os
from unittest.mock import MagicMock
import pytest

# We expect these imports to fail initially (Red TDD phase)
from worksbyworrell.warlock.repository.skill import (
    LocalSkillMetadataRepository,
    FirestoreSkillMetadataRepository
)

# ============================================================================
# 1. LOCAL SKILL METADATA REPOSITORY TESTS
# ============================================================================

def test_local_skill_repository_success(tmp_path):
    """Verify LocalSkillMetadataRepository parses SKILL.md inside skill directories."""
    # Set up mock skills directory structure
    public_dir = tmp_path / "skills"
    skill_dir = public_dir / "antigravity-guide"
    skill_dir.mkdir(parents=True)
    
    # Write SKILL.md file
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(
        "---\n"
        "description: Guides the agent on tool usage\n"
        "---\n"
        "Instructions on using Antigravity."
    )
    
    # Act
    repo = LocalSkillMetadataRepository(public_dir=str(public_dir))
    data = repo.get_skill("antigravity-guide")
    
    # Assert
    assert data["skill_id"] == "antigravity-guide"
    assert data["description"] == "Guides the agent on tool usage"
    assert data["system_prompt"] == "Instructions on using Antigravity."


def test_local_skill_repository_missing_graceful_fallback(tmp_path):
    """Verify local repo returns fallback message when skill directory or file is absent."""
    public_dir = tmp_path / "skills"
    public_dir.mkdir()
    
    repo = LocalSkillMetadataRepository(public_dir=str(public_dir))
    data = repo.get_skill("unknown-skill")
    
    assert data["skill_id"] == "unknown-skill"
    assert "Error" in data["system_prompt"]


# ============================================================================
# 2. FIRESTORE SKILL METADATA REPOSITORY TESTS
# ============================================================================

def test_firestore_skill_repository_success(mocker):
    """Verify FirestoreSkillMetadataRepository retrieves documents from skill_metadata collection."""
    # Arrange
    mock_db = MagicMock()
    
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {
        "description": "Guides the agent",
        "system_prompt": "Firestore instruction contents."
    }
    
    mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
    
    # Act
    repo = FirestoreSkillMetadataRepository(client=mock_db)
    data = repo.get_skill("antigravity-guide")
    
    # Assert
    assert data["skill_id"] == "antigravity-guide"
    assert data["description"] == "Guides the agent"
    assert data["system_prompt"] == "Firestore instruction contents."
    
    # Verify collection boundary is "skill_metadata"
    mock_db.collection.assert_called_with("skill_metadata")
    mock_db.collection.return_value.document.assert_called_with("antigravity-guide")


def test_firestore_skill_repository_handles_missing_docs(mocker):
    """Verify Firestore repo returns fallback message when document does not exist in DB."""
    # Arrange
    mock_db = MagicMock()
    
    mock_doc = MagicMock()
    mock_doc.exists = False
    mock_doc.to_dict.return_value = None
    
    mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
    
    # Act
    repo = FirestoreSkillMetadataRepository(client=mock_db)
    data = repo.get_skill("unknown-db-skill")
    
    # Assert
    assert data["skill_id"] == "unknown-db-skill"
    assert "Error" in data["system_prompt"]
