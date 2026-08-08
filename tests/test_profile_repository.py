from unittest.mock import MagicMock

# We expect these imports to fail initially (Red TDD phase)
from worksbyworrell.warlock.repository.profile import (
    FirestoreUserProfileRepository,
    LocalUserProfileRepository,
    _merge,
)

# ============================================================================
# 1. MERGE LOGIC TESTS
# ============================================================================

def test_profile_merge_preserves_both_prompts():
    """
    Verify profile merge retains both public and private prompt contents
    rather than letting the private system_prompt overwrite the public one.
    """
    public = {"role": "Senior Engineer", "system_prompt": "Public Lore & Profile"}
    private = {"alias": "Warlock", "system_prompt": "Private Alignment Constraints"}
    
    merged = _merge("raworre", public, private)
    
    assert merged["username"] == "raworre"
    assert merged["role"] == "Senior Engineer"
    assert merged["alias"] == "Warlock"
    assert merged["public_prompt"] == "Public Lore & Profile"
    assert merged["private_prompt"] == "Private Alignment Constraints"


# ============================================================================
# 2. LOCAL USER PROFILE REPOSITORY TESTS
# ============================================================================

def test_local_profile_repository_reads_and_merges_symmetrically(tmp_path):
    """
    Verify LocalUserProfileRepository parses public/private directories
    symmetrically and compiles metadata and prompts.
    """
    # Arrange folders
    public_dir = tmp_path / "public"
    private_dir = tmp_path / "private"
    public_dir.mkdir()
    private_dir.mkdir()
    
    # Write public profile file
    public_file = public_dir / "raworre.md"
    public_file.write_text(
        "---\n"
        "name: Roger\n"
        "---\n"
        "Public profile content."
    )
    
    # Write private override file (symmetrically named)
    private_file = private_dir / "raworre.md"
    private_file.write_text(
        "---\n"
        "alignment: strict-sse\n"
        "---\n"
        "Private profile constraints."
    )
    
    # Act
    repo = LocalUserProfileRepository(public_dir=str(public_dir), private_dir=str(private_dir))
    data = repo.get_profile("raworre")
    
    # Assert
    assert data["username"] == "raworre"
    assert data["name"] == "Roger"
    assert data["alignment"] == "alignment" or data.get("alignment") == "strict-sse"
    assert data["public_prompt"] == "Public profile content."
    assert data["private_prompt"] == "Private profile constraints."


def test_local_profile_repository_missing_files_fallback(tmp_path):
    """Verify local profile repo falls back to empty strings when files do not exist."""
    public_dir = tmp_path / "public"
    private_dir = tmp_path / "private"
    public_dir.mkdir()
    private_dir.mkdir()
    
    repo = LocalUserProfileRepository(public_dir=str(public_dir), private_dir=str(private_dir))
    data = repo.get_profile("unknown-user")
    
    assert data["username"] == "unknown-user"
    assert data["public_prompt"] == ""
    assert data["private_prompt"] == ""


# ============================================================================
# 3. FIRESTORE USER PROFILE REPOSITORY TESTS
# ============================================================================

def test_firestore_profile_repository_queries_and_merges(mocker):
    """Verify FirestoreUserProfileRepository fetches and merges snapshots from firestore."""
    # Arrange
    mock_db = MagicMock()
    
    mock_pub_doc = MagicMock()
    mock_pub_doc.exists = True
    mock_pub_doc.to_dict.return_value = {"role": "SSE", "system_prompt": "Firestore Public Lore"}
    
    mock_priv_doc = MagicMock()
    mock_priv_doc.exists = True
    mock_priv_doc.to_dict.return_value = {"system_prompt": "Firestore Private Constraints"}
    
    def mock_collection_routing(collection_name):
        mock_coll = MagicMock()
        if collection_name == "user_profiles":
            mock_coll.document.return_value.get.return_value = mock_pub_doc
        elif collection_name == "user_profile_overlays":
            mock_coll.document.return_value.get.return_value = mock_priv_doc
        return mock_coll
        
    mock_db.collection.side_effect = mock_collection_routing
    
    # Act
    repo = FirestoreUserProfileRepository(client=mock_db)
    data = repo.get_profile("raworre")
    
    # Assert
    assert data["username"] == "raworre"
    assert data["role"] == "SSE"
    assert data["public_prompt"] == "Firestore Public Lore"
    assert data["private_prompt"] == "Firestore Private Constraints"
    
    # Verify collection boundaries
    mock_db.collection.assert_any_call("user_profiles")
    mock_db.collection.assert_any_call("user_profile_overlays")


def test_firestore_profile_repository_handles_missing_docs_gracefully(mocker):
    """Verify Firestore profile repo returns empty strings when snapshots do not exist."""
    # Arrange
    mock_db = MagicMock()
    
    mock_pub_doc = MagicMock()
    mock_pub_doc.exists = False
    mock_pub_doc.to_dict.return_value = None
    
    mock_priv_doc = MagicMock()
    mock_priv_doc.exists = False
    mock_priv_doc.to_dict.return_value = None
    
    mock_db.collection.return_value.document.return_value.get.side_effect = [mock_pub_doc, mock_priv_doc]
    
    # Act
    repo = FirestoreUserProfileRepository(client=mock_db)
    data = repo.get_profile("ghost")
    
    # Assert
    assert data["username"] == "ghost"
    assert data["public_prompt"] == ""
    assert data["private_prompt"] == ""
