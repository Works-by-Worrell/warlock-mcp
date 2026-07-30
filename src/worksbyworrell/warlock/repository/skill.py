import os
from typing import Any, Dict

from google.cloud import firestore

from worksbyworrell.warlock.repository.base import SkillMetadataRepository
from worksbyworrell.warlock.repository.parser import parse_file

SKILL_METADATA = "skill_metadata"


class LocalSkillMetadataRepository(SkillMetadataRepository):
    """Strategy to read skill metadata from the local filesystem."""

    def __init__(self, public_dir: str | None = None):
        self.skills_dir = public_dir or os.environ.get("WARLOCK_CONFIG_DIR", "./.skills")

    def get_skill(self, skill_id: str) -> Dict[str, Any]:
        """Read the skill metadata from the local filesystem."""
        skills_path = f"{self.skills_dir}/{skill_id}/SKILL.md"

        data = parse_file(skills_path)

        if "system_prompt" not in data:
            data["system_prompt"] = f"Error: Skill '{skill_id}' not found locally."

        return {"skill_id": skill_id, **data}


class FirestoreSkillMetadataRepository(SkillMetadataRepository):
    """Strategy to read skill metadata from the Firestore database."""

    def __init__(self, client: firestore.Client):
        self.client = client

    def get_skill(self, skill_id: str) -> Dict[str, Any]:
        """Read the skill metadata from the Firestore database."""
        ref = self.client.collection(SKILL_METADATA).document(skill_id).get()
        data = ref.to_dict() or {}

        if "system_prompt" not in data:
            data["system_prompt"] = f"Error: Skill '{skill_id}' not found locally."

        return {"skill_id": skill_id, **data}
