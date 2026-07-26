import os
from typing import Any, Dict

from google.cloud import firestore

from worksbyworrell.warlock.repository.base import AgentRepository
from worksbyworrell.warlock.repository.parser import parse_file

AGENT_CONFIGURATIONS = "agent_configurations"
AGENT_OVERLAYS = "agent_overlays"


def _merge(
    agent_id: str, public_data: Dict[str, Any], private_data: Dict[str, Any]
) -> Dict[str, Any]:
    merged = {
        "agent_id": agent_id,
        **public_data,
        **private_data,
    }

    if "system_prompt" not in merged:
        merged["system_prompt"] = f"Error: No configuration found for agent '{agent_id}'"

    return merged


class LocalAgentRepository(AgentRepository):
    """Strategy to read agent configurations from the local filesystem."""

    def __init__(self, public_dir: str | None = None, private_dir: str | None = None):
        # Allow passing directories or fall back to local config env variables
        self.public_dir = public_dir or os.environ.get("WARLOCK_CONFIG_DIR", "./.public/agents")
        self.private_dir = private_dir or os.environ.get(
            "WARLOCK_PRIVATE_CONFIG_DIR", "./.private/agents"
        )

    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """Get merged agent configuration from local filesystem."""
        public_path = os.path.join(self.public_dir, f"{agent_id}.md")
        private_path = os.path.join(self.private_dir, f"{agent_id}.md")

        public_data = parse_file(public_path)
        private_data = parse_file(private_path)

        return _merge(agent_id, public_data, private_data)


class FirestoreAgentRepository(AgentRepository):
    """Strategy to read agent configurations from Firestore collections."""

    def __init__(self, client: firestore.Client | None = None):
        self.client = client or firestore.Client()

    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """Get merged agent configuration from Firestore collection."""
        public_ref = self.client.collection(AGENT_CONFIGURATIONS).document(agent_id).get()
        public_data = public_ref.to_dict() or {}

        private_ref = self.client.collection(AGENT_OVERLAYS).document(agent_id).get()
        private_data = private_ref.to_dict() or {}

        return _merge(agent_id, public_data, private_data)
