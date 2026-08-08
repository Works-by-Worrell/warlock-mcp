import sys
from unittest.mock import ANY, MagicMock, patch

import pytest

# We import the CLI entrypoint (this will initially fail to import during Red-TDD)
try:
    from worksbyworrell.warlock.pipeline.cli import main
except ImportError:
    main = None


# Ensure mock functions/modules exist for RED TDD execution
def test_cli_entrypoint_is_defined():
    assert main is not None, "CLI main entrypoint is not yet defined."


# ============================================================================
# CLI PARSING & ORCHESTRATION TESTS
# ============================================================================

@pytest.mark.skipif(main is None, reason="CLI entrypoint not yet implemented.")
@patch("worksbyworrell.warlock.pipeline.cli.ConfigIngestionPipeline")
@patch("google.cloud.firestore.Client")
def test_cli_orchestration_flow(mock_firestore, mock_pipeline_class, tmp_path):
    """Verify that cli.main correctly parses arguments and orchestrates the synchronization flow."""
    # Set up mock folders
    public_dir = tmp_path / "public"
    public_dir.mkdir()
    (public_dir / "agents").mkdir()
    (public_dir / "profiles").mkdir()
    (public_dir / "resources").mkdir()
    (public_dir / "skills").mkdir()
    
    private_dir = tmp_path / "private"
    private_dir.mkdir()
    (private_dir / "agents").mkdir()
    (private_dir / "profiles").mkdir()
    
    # Mock pipeline instance
    mock_pipeline = MagicMock()
    mock_pipeline_class.return_value = mock_pipeline
    
    # Prepare sys.argv mock arguments
    test_args = [
        "warlock-mcp-syncer",
        "--public-dir", str(public_dir),
        "--private-dir", str(private_dir),
        "--project-id", "test-project",
        "--github-sha", "test-sha-12345",
    ]
    
    with patch.object(sys, "argv", test_args):
        # Act
        main()
        
    # Assert: Firestore client was initialized with the project ID and database
    mock_firestore.assert_called_once_with(project="test-project", database="(default)")
    
    # Assert: ConfigIngestionPipeline was initialized with dry_run=False
    mock_pipeline_class.assert_called_once_with(db=mock_firestore.return_value, dry_run=False)
    
    # Assert: All standard domains were synced
    mock_pipeline.sync_standard_directory.assert_any_call(
        collection_name="agent_configurations",
        directory_path=str(public_dir / "agents"),
        validator_fn=ANY
    )
    mock_pipeline.sync_standard_directory.assert_any_call(
        collection_name="user_profiles",
        directory_path=str(public_dir / "profiles"),
        validator_fn=ANY
    )
    mock_pipeline.sync_standard_directory.assert_any_call(
        collection_name="system_resources",
        directory_path=str(public_dir / "resources"),
        validator_fn=ANY
    )
    
    # Assert: Skills were synced
    mock_pipeline.sync_skills_directory.assert_any_call(
        collection_name="skill_metadata",
        directory_path=str(public_dir / "skills"),
        validator_fn=ANY
    )
    
    # Assert: Private overlays were synced
    mock_pipeline.sync_standard_directory.assert_any_call(
        collection_name="agent_overlays",
        directory_path=str(private_dir / "agents"),
        validator_fn=ANY
    )
    mock_pipeline.sync_standard_directory.assert_any_call(
        collection_name="user_profile_overlays",
        directory_path=str(private_dir / "profiles"),
        validator_fn=ANY
    )


@pytest.mark.skipif(main is None, reason="CLI entrypoint not yet implemented.")
@patch("worksbyworrell.warlock.pipeline.cli.ConfigIngestionPipeline")
@patch("google.cloud.firestore.Client")
def test_cli_dry_run_propagation(mock_firestore, mock_pipeline_class, tmp_path):
    """Verify that passing --dry-run propagates the flag correctly to the pipeline instantiation."""
    public_dir = tmp_path / "public"
    public_dir.mkdir()
    
    # Prepare sys.argv mock arguments with dry-run flag
    test_args = [
        "warlock-mcp-syncer",
        "--public-dir", str(public_dir),
        "--dry-run"
    ]
    
    with patch.object(sys, "argv", test_args):
        # Act
        main()
        
    # Assert: ConfigIngestionPipeline was initialized with dry_run=True
    mock_pipeline_class.assert_called_once_with(db=mock_firestore.return_value, dry_run=True)
