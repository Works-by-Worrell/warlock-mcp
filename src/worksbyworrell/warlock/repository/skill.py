import os
from typing import Any, Dict

from worksbyworrell.warlock.repository.base import SkillMetadataRepository
from worksbyworrell.warlock.repository.github import fetch_github_file
from worksbyworrell.warlock.repository.parser import parse_content, parse_file

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


class GithubSkillMetadataRepository(SkillMetadataRepository):
    """Strategy to read skill metadata from GitHub API."""

    def __init__(self):
        pass

    def get_skill(self, skill_id: str) -> Dict[str, Any]:
        """Read the skill metadata from the GitHub API."""
        raw = fetch_github_file("wbw-config-private", f"skills/{skill_id}/SKILL.md")
        data = parse_content(raw) if raw else {}

        if "system_prompt" not in data:
            data["system_prompt"] = f"Error: Skill '{skill_id}' not found in GitHub."

        return {"skill_id": skill_id, **data}
