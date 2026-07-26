import os
from unittest.mock import MagicMock
import pytest

from worksbyworrell.warlock.repository.agent import (
    LocalAgentRepository,
    FirestoreAgentRepository,
    _merge
)
from worksbyworrell.warlock.repository.parser import extract_frontmatter_and_body

# ============================================================================
# 1. PURE HELPER METHOD TESTS
# ============================================================================

def test_extract_frontmatter_and_body_with_frontmatter():
    """Verify markdown content parsing splits frontmatter and body cleanly."""
    content = (
        "---\n"
        "name: Torque\n"
        "model: gemini-2.0-flash\n"
        "---\n"
        "This is the core instructions prompt."
    )
    fm, body = extract_frontmatter_and_body(content)
    
    assert "name: Torque" in fm
    assert "model: gemini-2.0-flash" in fm
    assert body.strip() == "This is the core instructions prompt."


def test_extract_frontmatter_and_body_no_frontmatter():
    """Verify raw content without frontmatter returns empty frontmatter and full body."""
    content = "This is a simple system prompt without YAML header."
    fm, body = extract_frontmatter_and_body(content)
    
    assert fm == ""
    assert body == content



def test_merge_combines_and_overrides():
    """Verify private overrides public keys and injects fallback checks."""
    public = {"name": "Torque", "system_prompt": "Public Base Prompt", "model": "gemini-1.5"}
    private = {"system_prompt": "Private Overlay Prompt", "token": "sec_123"}
    
    merged = _merge("torque", public, private)
    
    assert merged["agent_id"] == "torque"
    assert merged["name"] == "Torque"
    # Private should override public
    assert merged["system_prompt"] == "Private Overlay Prompt"
    assert merged["model"] == "gemini-1.5"
    assert merged["token"] == "sec_123"


# ============================================================================
# 2. LOCAL AGENT REPOSITORY TESTS
# ============================================================================

def test_local_agent_repository_reads_and_merges_symmetrically(tmp_path):
    """
    Verify LocalAgentRepository parses public/private directories symmetrically.
    Using pytest's built-in tmp_path fixture to avoid fragile open mocks.
    """
    # Set up mock folder structure
    public_dir = tmp_path / "public"
    private_dir = tmp_path / "private"
    public_dir.mkdir()
    private_dir.mkdir()
    
    # Write public configuration file
    public_file = public_dir / "torque.md"
    public_file.write_text(
        "---\n"
        "name: Public Torque\n"
        "model: gemini-2.0-pro\n"
        "---\n"
        "System prompt instructions."
    )
    
    # Write private override configuration file
    private_file = private_dir / "torque.md"
    private_file.write_text(
        "---\n"
        "api_key: sec_999\n"
        "---\n"
        "Overlay prompt instructions override."
    )
    
    repo = LocalAgentRepository(public_dir=str(public_dir), private_dir=str(private_dir))
    data = repo.get_agent("torque")
    
    assert data["agent_id"] == "torque"
    assert data["name"] == "Public Torque"
    assert data["model"] == "gemini-2.0-pro"
    assert data["api_key"] == "sec_999"
    # Private body should take precedence
    assert data["system_prompt"] == "Overlay prompt instructions override."


def test_local_agent_repository_missing_files_graceful_fallback(tmp_path):
    """Verify local repo returns fallback prompt rather than crashing when files are absent."""
    public_dir = tmp_path / "public"
    private_dir = tmp_path / "private"
    public_dir.mkdir()
    private_dir.mkdir()
    
    repo = LocalAgentRepository(public_dir=str(public_dir), private_dir=str(private_dir))
    data = repo.get_agent("unknown-agent")
    
    assert data["agent_id"] == "unknown-agent"
    assert "Error" in data["system_prompt"]


# ============================================================================
# 3. FIRESTORE AGENT REPOSITORY TESTS
# ============================================================================

def test_firestore_agent_repository_queries_and_merges(mocker):
    """
    Verify FirestoreAgentRepository fetches snapshots from appropriate collections
    and merges them without throwing PyCharm/static-analysis warnings.
    """
    # Arrange
    mock_db = MagicMock()
    
    # Mock public snapshot return
    mock_pub_doc = MagicMock()
    mock_pub_doc.exists = True
    mock_pub_doc.to_dict.return_value = {"name": "Firestore Torque", "system_prompt": "Base"}
    
    # Mock private snapshot return
    mock_priv_doc = MagicMock()
    mock_priv_doc.exists = True
    mock_priv_doc.to_dict.return_value = {"system_prompt": "Overlay", "api_key": "sec_888"}
    
    # Stub collections mapping (Mockito equivalent: when().thenReturn())
    def mock_collection_routing(collection_name):
        mock_coll = MagicMock()
        if collection_name == "agent_configurations":
            mock_coll.document.return_value.get.return_value = mock_pub_doc
        elif collection_name == "agent_overlays":
            mock_coll.document.return_value.get.return_value = mock_priv_doc
        return mock_coll
        
    mock_db.collection.side_effect = mock_collection_routing
    
    # Act
    repo = FirestoreAgentRepository(client=mock_db)
    data = repo.get_agent("torque")
    
    # Assert
    assert data["agent_id"] == "torque"
    assert data["name"] == "Firestore Torque"
    assert data["api_key"] == "sec_888"
    assert data["system_prompt"] == "Overlay"
    
    # Verify calls
    mock_db.collection.assert_any_call("agent_configurations")
    mock_db.collection.assert_any_call("agent_overlays")


def test_firestore_agent_repository_handles_missing_docs_gracefully(mocker):
    """Verify Firestore repo handles empty snapshot references gracefully using Null Coalescing."""
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
    repo = FirestoreAgentRepository(client=mock_db)
    data = repo.get_agent("ghost")
    
    # Assert
    assert data["agent_id"] == "ghost"
    assert "Error" in data["system_prompt"]
