from unittest.mock import MagicMock

# We expect these imports to fail initially (Red TDD phase)
from worksbyworrell.warlock.repository.resource import (
    LocalResourceRepository,
)

# ============================================================================
# 1. LOCAL RESOURCE REPOSITORY TESTS
# ============================================================================

def test_local_resource_repository_success(tmp_path):
    """
    Verify LocalResourceRepository maps resource IDs to filenames
    and reads the contents cleanly.
    """
    # Arrange resources folder
    public_dir = tmp_path / "resources"
    public_dir.mkdir()
    
    # Write a definition of ready resource file
    ready_file = public_dir / "DEFINITION_OF_READY.md"
    ready_file.write_text(
        "# Definition of Ready\n"
        "- Task must have acceptance criteria."
    )
    
    # Act
    repo = LocalResourceRepository(public_dir=str(public_dir))
    data = repo.get_resource("definitions/ready")
    
    # Assert
    assert data["resource_id"] == "definitions/ready"
    assert "Definition of Ready" in data["system_prompt"]


def test_local_resource_repository_missing_graceful_fallback(tmp_path):
    """Verify local repo returns fallback message when resource files are absent."""
    public_dir = tmp_path / "resources"
    public_dir.mkdir()
    
    repo = LocalResourceRepository(public_dir=str(public_dir))
    data = repo.get_resource("definitions/unknown")
    
    assert data["resource_id"] == "definitions/unknown"
    assert "Error" in data["system_prompt"]


# ============================================================================
# 2. FIRESTORE RESOURCE REPOSITORY TESTS
# ============================================================================


