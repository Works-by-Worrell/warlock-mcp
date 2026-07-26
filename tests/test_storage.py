from unittest.mock import MagicMock

from worksbyworrell.warlock.storage.firestore_client import (
    _load_from_firestore,
    get_agent_config,
    save_document,
    serialize_agent_config,
)


def test_load_from_firestore_success(mock_firestore_client):
    """
    Verify Firestore integration fetches config fields correctly when mocked.
    """
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {"overlay_id": "sse_preview", "restricted_mode": False}
    mock_firestore_client.collection.return_value.document.return_value.get.return_value = mock_doc

    result = _load_from_firestore(agent_id="warlock-prime", client=mock_firestore_client)

    assert result["restricted_mode"] is False


def test_save_document_success(mock_firestore_client):
    """
    Verify save_document writes data payload to the specified Firestore collection and document ID.
    """
    payload = {"title": "Phase 5 Ingress", "progress_percentage": 25.0}
    save_document("portfolio_milestones", "5", payload, client=mock_firestore_client)

    mock_firestore_client.collection.assert_called_once_with("portfolio_milestones")
    mock_firestore_client.collection.return_value.document.assert_called_once_with("5")
    mock_firestore_client.collection.return_value.document.return_value.set.assert_called_once_with(
        payload
    )


def test_get_agent_config_routes_to_firestore_when_gcp_project_set(monkeypatch, mocker):
    """
    Verify strategy router selects _load_from_firestore when GCP_PROJECT_ID is present in
    environment.
    """
    # ARRANGE
    monkeypatch.setenv("GCP_PROJECT_ID", "dummy-project-id")
    mock_firestore_loader = mocker.patch(
        "worksbyworrell.warlock.storage.firestore_client._load_from_firestore",
        return_value={
            "name": "Warlock Core Agent",
            "public_scope": "Portfolio automation and public task triage orchestration",
            "underlying_model_target": "gemini-1.5-pro",
        },
    )

    # ACT
    result = get_agent_config("warlock-prime")

    # ASSERT
    mock_firestore_loader.assert_called_once_with("warlock-prime")
    assert result["name"] == "Warlock Core Agent"
    assert result["underlying_model_target"] == "gemini-1.5-pro"


def test_get_agent_config_routes_to_local_fs_when_gcp_project_absent(monkeypatch, mocker):
    """
    Verify strategy router falls back to local filesystem strategy when GCP_PROJECT_ID is missing.
    """
    # ARRANGE
    monkeypatch.delenv("GCP_PROJECT_ID", raising=False)
    mock_firestore_loader = mocker.patch(
        "worksbyworrell.warlock.storage.firestore_client._load_from_firestore"
    )
    mock_local_loader = mocker.patch(
        "worksbyworrell.warlock.storage.firestore_client._load_from_local_fs",
        return_value={"name": "Warlock Local Fallback", "public_scope": "Demo Mode"},
    )

    # ACT
    result = get_agent_config("warlock-prime")

    # ASSERT
    mock_local_loader.assert_called_once_with("warlock-prime")
    mock_firestore_loader.assert_not_called()
    assert result["name"] == "Warlock Local Fallback"
    assert result["public_scope"] == "Demo Mode"


# --- 3. MCP RESOURCE SERIALIZATION & SECRET REDACTION ---


def test_serialize_agent_config_redacts_sensitive_keys(mocker):
    """
    Verify serialize_agent_config formats Markdown output while sanitizing any dictionary keys
    containing 'key' or 'token'.
    """
    # ARRANGE
    mock_config = {
        "name": "Warlock Core Agent",
        "public_scope": "Portfolio automation and public task triage orchestration",
        "github_token": "ghp_secret_token_12345",
        "private_app_key": "sec_enc_0x83F9",
    }

    mock_get_config = mocker.patch(
        "worksbyworrell.warlock.storage.firestore_client.get_agent_config", return_value=mock_config
    )

    # ACT
    output = serialize_agent_config("warlock-prime")

    # ASSERT
    assert "ghp_secret_token_12345" not in output
    assert "sec_enc_0x83F9" not in output
    assert "* **`github_token`**: `[ENCRYPTED/RESTRICTED_BOUNDARIES]`" in output
    assert "* **`private_app_key`**: `[ENCRYPTED/RESTRICTED_BOUNDARIES]`" in output
    assert "Warlock Core Agent" in output
    mock_get_config.assert_called_once_with("warlock-prime")
