import json
import os

from google.cloud import firestore

from ..core import mcp


def _load_from_firestore(agent_id: str, client=None) -> dict:
    """
    Load public config configurations and private overlays from Firestore.
    To be fully implemented in Phase 4.
    """
    if client is None:
        client = firestore.Client()

    public_ref = client.collection("agent_configurations").document(agent_id).get()
    private_ref = client.collection("agent_overlays").document(agent_id).get()

    base = public_ref.to_dict() if public_ref.exists else {}
    overlay = private_ref.to_dict() if private_ref.exists else {}

    return {**base, **overlay}


def _load_from_local_fs(agent_id: str) -> dict:
    """
    Fallback loader reading configuration from local JSON files.
    """
    mock_path = os.path.join("tests", "mock_data", f"{agent_id}.json")
    if not os.path.exists(mock_path):
        return {"name": agent_id, "public_scope": "Fallback Demo Mode Enabled"}

    with open(mock_path, "r") as f:
        return json.load(f)


STORAGE_STRATEGIES = {"prod": _load_from_firestore, "local": _load_from_local_fs}


def get_agent_config(agent_id: str) -> dict:
    """
    Resolves storage strategy based on environmental markers.
    """
    if os.environ.get("GCP_PROJECT_ID"):
        return _load_from_firestore(agent_id)
    return _load_from_local_fs(agent_id)


@mcp.resource("warlock://config/{agent_id}")
def serialize_agent_config(agent_id: str) -> str:
    """
    Resolves agent config and sanitizes before responding
    """
    merged = get_agent_config(agent_id)

    markdown_output = f"# Integrated Configuration Strategy for: `{agent_id}`\n\n"
    markdown_output += "### Structural Metadata Profiles\n"
    for key, value in merged.items():
        if "key" in key or "token" in key:
            markdown_output += f"* **`{key}`**: `[ENCRYPTED/RESTRICTED_BOUNDARIES]`\n"
        else:
            markdown_output += f"* **`{key}`**: `{value}`\n"

    return markdown_output


def save_document(collection_name: str, doc_id: str, data: dict, client=None) -> None:
    """
    Persist or overwrite a document payload in the specified Firestore collection.
    """
    if client is None:
        client = firestore.Client()
    client.collection(collection_name).document(str(doc_id)).set(data)
