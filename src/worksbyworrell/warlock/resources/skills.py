from worksbyworrell.core.repository import get_skill_repository

from worksbyworrell.warlock.core import mcp


@mcp.resource("skill://{skill_name}")
def get_skill_instructions(skill_name: str) -> str:
    """Returns instructions and metadata from a skill's SKILL.md file."""
    data = get_skill_repository().get_skill(skill_name)
    return data.get("system_prompt") or ""
