from unittest.mock import MagicMock

# We expect these imports to fail initially (Red TDD phase)
from worksbyworrell.warlock.repository.skill import (
    LocalSkillMetadataRepository,
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


