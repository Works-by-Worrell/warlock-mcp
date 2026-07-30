import os
from typing import Any, Dict

from google.cloud import firestore

from worksbyworrell.warlock.repository.base import ResourceRepository
from worksbyworrell.warlock.repository.parser import parse_file

SYSTEM_RESOURCES = "system_resources"


class LocalResourceRepository(ResourceRepository):
    """Strategy to read resources from the local filesystem."""

    RESOURCE_MAP = {
        "definitions/ready": "DEFINITION_OF_READY.md",
        "ready": "DEFINITION_OF_READY.md",
    }

    def __init__(self, public_dir: str | None = None):
        self.public_dir = public_dir or os.environ.get("WARLOCK_CONFIG_DIR", "./.public/resources")

    def get_resource(self, resource_id: str) -> Dict[str, Any]:
        """Get a resource from the local filesystem."""
        filename = self.RESOURCE_MAP.get(resource_id)
        if not filename:
            return {
                "resource_id": resource_id,
                "system_prompt": f"Error: Resource ID '{resource_id}' not mapped in local storage.",
            }

        path = os.path.join(self.public_dir, filename)
        data = parse_file(path)

        return {"resource_id": resource_id, **data}


class FirestoreResourceRepository(ResourceRepository):
    """Strategy to read resources from the local filesystem."""

    def __init__(self, client: firestore.Client):
        self.client = client

    def get_resource(self, resource_id: str) -> Dict[str, Any]:
        """Get a resource from Firestore collection."""
        doc_id = resource_id.replace("/", "_")
        ref = self.client.collection(SYSTEM_RESOURCES).document(doc_id).get()
        data = ref.to_dict() or {}

        if not ref.exists:
            data["system_prompt"] = (
                f"Error: Resource ID '{resource_id}' not found in Firestore collection."
            )

        return {"resource_id": resource_id, **data}
