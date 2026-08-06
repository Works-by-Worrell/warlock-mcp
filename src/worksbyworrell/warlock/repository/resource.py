import os
from typing import Any, Dict

from worksbyworrell.warlock.repository.github import fetch_github_file
from worksbyworrell.warlock.repository.parser import parse_content, parse_file
from worksbyworrell.warlock.repository.base import ResourceRepository

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


class GithubResourceRepository(ResourceRepository):
    """Strategy to read resources from GitHub API."""

    def __init__(self):
        pass

    def get_resource(self, resource_id: str) -> Dict[str, Any]:
        """Get a resource from GitHub API."""
        filename = LocalResourceRepository.RESOURCE_MAP.get(resource_id, f"{resource_id}.md")
        raw = fetch_github_file("wbw-config-private", f"resources/{filename}")
        if not raw:
            return {
                "resource_id": resource_id,
                "system_prompt": f"Error: Resource ID '{resource_id}' not found in GitHub.",
            }
        
        data = parse_content(raw)
        return {"resource_id": resource_id, **data}
