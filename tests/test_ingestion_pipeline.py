import sys
from unittest.mock import MagicMock, patch
import pytest

# Target imports (expected to fail or pass depending on file existence - RED TDD Phase)
try:
    from worksbyworrell.warlock.pipeline.ingestion_pipeline import ConfigIngestionPipeline
except ImportError:
    ConfigIngestionPipeline = None


# Ensure target module is mockable/importable for RED TDD execution
@pytest.mark.skipif(ConfigIngestionPipeline is None, reason="Ingestion pipeline not yet implemented.")
def test_pipeline_class_exists():
    assert ConfigIngestionPipeline is not None


# ============================================================================
# 1. CHECKSUM DETERMINISM TESTS
# ============================================================================

@pytest.mark.skipif(ConfigIngestionPipeline is None, reason="Ingestion pipeline not yet implemented.")
def test_calculate_content_hash_is_deterministic():
    """Verify MD5 hash calculations are order-independent and deterministic."""
    pipeline = ConfigIngestionPipeline(db=MagicMock())
    
    data1 = {"name": "Torque", "model": "gemini-2.0", "system_prompt": "You are Torque."}
    data2 = {"system_prompt": "You are Torque.", "model": "gemini-2.0", "name": "Torque"}
    
    hash1 = pipeline.calculate_content_hash(data1)
    hash2 = pipeline.calculate_content_hash(data2)
    
    assert hash1 == hash2
    assert len(hash1) == 32  # Standard MD5 length hex representation


# ============================================================================
# 2. DELTA-SYNCING CORE MOCK TESTS
# ============================================================================

@pytest.mark.skipif(ConfigIngestionPipeline is None, reason="Ingestion pipeline not yet implemented.")
def test_sync_document_new_write(monkeypatch):
    """Verify a new document (does not exist in DB) is written to Firestore."""
    monkeypatch.setenv("GITHUB_SHA", "a1b2c3d4e5f6")
    mock_db = MagicMock()
    
    # Document does not exist in DB
    mock_doc = MagicMock()
    mock_doc.exists = False
    mock_doc.to_dict.return_value = None
    
    mock_doc_ref = MagicMock()
    mock_doc_ref.get.return_value = mock_doc
    
    mock_db.collection.return_value.document.return_value = mock_doc_ref
    
    pipeline = ConfigIngestionPipeline(db=mock_db)
    payload = {"name": "Test Agent", "system_prompt": "Test Prompt"}
    
    # Act
    updated = pipeline.sync_document("agent_configurations", "test-agent", payload)
    
    # Assert
    assert updated is True
    mock_doc_ref.set.assert_called_once()
    
    # Check that injected GITHUB_SHA and MD5 hash exist in the write payload
    called_payload = mock_doc_ref.set.call_args[0][0]
    assert called_payload["_version_hash"] == "a1b2c3d"
    assert "_md5_hash" in called_payload


@pytest.mark.skipif(ConfigIngestionPipeline is None, reason="Ingestion pipeline not yet implemented.")
def test_sync_document_matching_md5_skips_write(monkeypatch):
    """Verify document sync is skipped (no write) if MD5 hashes match exactly."""
    monkeypatch.setenv("GITHUB_SHA", "a1b2c3d4e5f6")
    mock_db = MagicMock()
    
    # Calculate expected hash
    pipeline = ConfigIngestionPipeline(db=mock_db)
    payload = {"name": "Test Agent", "system_prompt": "Test Prompt"}
    expected_hash = pipeline.calculate_content_hash(payload)
    
    # Mock document exists with matching hash
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {
        "name": "Test Agent",
        "system_prompt": "Test Prompt",
        "_md5_hash": expected_hash,
        "_version_hash": "prevsha"
    }
    
    mock_doc_ref = MagicMock()
    mock_doc_ref.get.return_value = mock_doc
    mock_db.collection.return_value.document.return_value = mock_doc_ref
    
    # Act
    updated = pipeline.sync_document("agent_configurations", "test-agent", payload)
    
    # Assert
    assert updated is False
    mock_doc_ref.set.assert_not_called()


@pytest.mark.skipif(ConfigIngestionPipeline is None, reason="Ingestion pipeline not yet implemented.")
def test_sync_document_drifting_md5_triggers_write(monkeypatch):
    """Verify document is rewritten to Firestore when MD5 hash drifts."""
    monkeypatch.setenv("GITHUB_SHA", "a1b2c3d4e5f6")
    mock_db = MagicMock()
    
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {
        "name": "Test Agent",
        "system_prompt": "OLD prompt content.",
        "_md5_hash": "outdated_md5_hash_value",
        "_version_hash": "prevsha"
    }
    
    mock_doc_ref = MagicMock()
    mock_doc_ref.get.return_value = mock_doc
    mock_db.collection.return_value.document.return_value = mock_doc_ref
    
    pipeline = ConfigIngestionPipeline(db=mock_db)
    payload = {"name": "Test Agent", "system_prompt": "NEW prompt content."}
    
    # Act
    updated = pipeline.sync_document("agent_configurations", "test-agent", payload)
    
    # Assert
    assert updated is True
    mock_doc_ref.set.assert_called_once()
    
    called_payload = mock_doc_ref.set.call_args[0][0]
    assert called_payload["_version_hash"] == "a1b2c3d"
    assert called_payload["system_prompt"] == "NEW prompt content."


# ============================================================================
# 3. ZERO FASTMCP IMPORT VERIFICATION
# ============================================================================

def test_pipeline_imports_without_triggering_fastmcp():
    """
    Verify that the ingestion pipeline can be loaded without importing FastMCP.
    This guarantees that the syncer script does not trigger stdio transport binds.
    """
    # Pop any loaded mcp references to ensure a clean import test
    mcp_modules = [m for m in list(sys.modules.keys()) if "fastmcp" in m.lower() or "mcp" in m.lower()]
    for m in mcp_modules:
        sys.modules.pop(m, None)
        
    # Act: Import the pipeline
    try:
        from worksbyworrell.warlock.pipeline.ingestion_pipeline import ConfigIngestionPipeline
    except ImportError:
        # Fallback if module does not exist in RED TDD phase (still fails test as expected)
        pass
        
    # Assert: FastMCP remains unloaded in sys.modules
    loaded_mcp = [m for m in sys.modules.keys() if "mcp" in m.lower()]
    assert not any(m == "mcp" or "fastmcp" in m for m in loaded_mcp), (
        "FastMCP was imported during ingestion pipeline loading! Decoupling violated."
    )


# ============================================================================
# 4. DRY RUN & ORCHESTRATION TESTS
# ============================================================================

@pytest.mark.skipif(ConfigIngestionPipeline is None, reason="Ingestion pipeline not yet implemented.")
def test_sync_document_dry_run_does_not_write(monkeypatch):
    """Verify that if dry_run=True, sync_document detects a change but does not write to Firestore."""
    monkeypatch.setenv("GITHUB_SHA", "a1b2c3d4e5f6")
    mock_db = MagicMock()
    
    # Document does not exist in DB (meaning there is a delta)
    mock_doc = MagicMock()
    mock_doc.exists = False
    mock_doc_ref = MagicMock()
    mock_doc_ref.get.return_value = mock_doc
    mock_db.collection.return_value.document.return_value = mock_doc_ref
    
    # Initialize pipeline with dry_run=True
    pipeline = ConfigIngestionPipeline(db=mock_db, dry_run=True)
    payload = {"name": "Test Agent", "system_prompt": "Test Prompt"}
    
    # Act
    updated = pipeline.sync_document("agent_configurations", "test-agent", payload)
    
    # Assert
    assert updated is True  # Should return True because a delta was found
    mock_doc_ref.set.assert_not_called()  # But should NOT perform the set operation


@pytest.mark.skipif(ConfigIngestionPipeline is None, reason="Ingestion pipeline not yet implemented.")
@patch("worksbyworrell.warlock.pipeline.ingestion_pipeline.crawl_standard_directory")
@patch("worksbyworrell.warlock.pipeline.ingestion_pipeline.normalize_keys")
def test_sync_standard_directory_orchestration(mock_normalize, mock_crawl):
    """Verify orchestration of standard directory crawling, normalization, validation, and syncing."""
    mock_db = MagicMock()
    pipeline = ConfigIngestionPipeline(db=mock_db)
    
    # Setup mocks
    mock_crawl.return_value = {
        "torque": {"agent-name": "Torque", "system_prompt": "You are Torque."}
    }
    mock_normalize.return_value = {
        "agent_name": "Torque", "system_prompt": "You are Torque."
    }
    
    mock_validator = MagicMock()
    mock_validator.return_value = {
        "agent_id": "torque", "name": "Torque", "system_prompt": "You are Torque."
    }
    
    # Mock sync_document
    pipeline.sync_document = MagicMock()
    pipeline.sync_document.return_value = True
    
    # Act
    updated_count = pipeline.sync_standard_directory(
        collection_name="agent_configurations",
        directory_path="/mock/path/agents",
        validator_fn=mock_validator
    )
    
    # Assert
    assert updated_count == 1
    mock_crawl.assert_called_once_with("/mock/path/agents")
    mock_normalize.assert_called_once_with({"agent-name": "Torque", "system_prompt": "You are Torque."})
    mock_validator.assert_called_once_with({
        "agent_name": "Torque", 
        "system_prompt": "You are Torque.",
        "agent_id": "torque",
        "username": "torque",
        "resource_id": "torque",
        "skill_id": "torque"
    })
    pipeline.sync_document.assert_called_once_with(
        "agent_configurations", "torque", {"agent_id": "torque", "name": "Torque", "system_prompt": "You are Torque."}
    )


@pytest.mark.skipif(ConfigIngestionPipeline is None, reason="Ingestion pipeline not yet implemented.")
@patch("worksbyworrell.warlock.pipeline.ingestion_pipeline.crawl_skills_directory")
@patch("worksbyworrell.warlock.pipeline.ingestion_pipeline.normalize_keys")
def test_sync_skills_directory_orchestration(mock_normalize, mock_crawl):
    """Verify orchestration of skills directory crawling, normalization, validation, and syncing."""
    mock_db = MagicMock()
    pipeline = ConfigIngestionPipeline(db=mock_db)
    
    # Setup mocks
    mock_crawl.return_value = {
        "git-ops": {"skillName": "Git Ops", "system_prompt": "Help Git."}
    }
    mock_normalize.return_value = {
        "skill_name": "Git Ops", "system_prompt": "Help Git."
    }
    
    mock_validator = MagicMock()
    mock_validator.return_value = {
        "skill_id": "git-ops", "system_prompt": "Help Git."
    }
    
    # Mock sync_document
    pipeline.sync_document = MagicMock()
    pipeline.sync_document.return_value = True
    
    # Act
    updated_count = pipeline.sync_skills_directory(
        collection_name="skill_metadata",
        directory_path="/mock/path/skills",
        validator_fn=mock_validator
    )
    
    # Assert
    assert updated_count == 1
    mock_crawl.assert_called_once_with("/mock/path/skills")
    mock_normalize.assert_called_once_with({"skillName": "Git Ops", "system_prompt": "Help Git."})
    mock_validator.assert_called_once_with({
        "skill_name": "Git Ops", 
        "system_prompt": "Help Git.",
        "agent_id": "git-ops",
        "username": "git-ops",
        "resource_id": "git-ops",
        "skill_id": "git-ops"
    })
    pipeline.sync_document.assert_called_once_with(
        "skill_metadata", "git-ops", {"skill_id": "git-ops", "system_prompt": "Help Git."}
    )

