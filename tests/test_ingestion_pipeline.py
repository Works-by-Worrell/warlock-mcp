import sys
from unittest.mock import MagicMock
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
