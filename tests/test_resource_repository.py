from unittest.mock import MagicMock

# We expect these imports to fail initially (Red TDD phase)
from worksbyworrell.warlock.repository.resource import (
    FirestoreResourceRepository,
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

def test_firestore_resource_repository_success(mocker):
    """Verify FirestoreResourceRepository retrieves documents from system_resources collection."""
    # Arrange
    mock_db = MagicMock()
    
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {
        "title": "Definition of Ready",
        "system_prompt": "# Firestore DoR content."
    }
    
    # Document ID should match the normalized resource path (e.g. definitions_ready)
    mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
    
    # Act
    repo = FirestoreResourceRepository(client=mock_db)
    data = repo.get_resource("definitions/ready")
    
    # Assert
    assert data["resource_id"] == "definitions/ready"
    assert data["title"] == "Definition of Ready"
    assert data["system_prompt"] == "# Firestore DoR content."
    
    # Verify collection boundaries (system_resources)
    mock_db.collection.assert_called_with("system_resources")
    # Slashing mapping check: "definitions/ready" can be stored as document ID "definitions_ready"
    # or the raw string. We will check that the doc ID matches the strategy.
    mock_db.collection.return_value.document.assert_called_with("definitions_ready")


def test_firestore_resource_repository_handles_missing_docs(mocker):
    """Verify Firestore repo returns fallback message when resource does not exist in DB."""
    # Arrange
    mock_db = MagicMock()
    
    mock_doc = MagicMock()
    mock_doc.exists = False
    mock_doc.to_dict.return_value = None
    
    mock_db.collection.return_value.document.return_value.get.return_value = mock_doc
    
    # Act
    repo = FirestoreResourceRepository(client=mock_db)
    data = repo.get_resource("definitions/ghost")
    
    # Assert
    assert data["resource_id"] == "definitions/ghost"
    assert "Error" in data["system_prompt"]
