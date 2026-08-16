import yaml

from worksbyworrell.warlock.core import mcp
from worksbyworrell.core.repository import (
    get_agent_repository,
    get_profile_repository,
    get_skill_repository,
)
from worksbyworrell.warlock.service.session_service import AgentSessionService

session_service = AgentSessionService(
    get_agent_repository(), get_profile_repository(), get_skill_repository()
)


@mcp.resource("agent://{agent_name}")
def get_agent_persona(agent_name: str) -> str:
    """
    Returns the layered agent persona. Combines the public base definition
    with the gitignored private overlay if it exists locally.
    """
    agent_data = get_agent_repository().get_agent(agent_name)
    metadata = {k: v for k, v in agent_data.items() if k not in ("agent_id", "system_prompt")}

    frontmatter = ""
    if metadata:
        yaml_str = yaml.safe_dump(metadata, sort_keys=False).strip()
        frontmatter = f"---\n{yaml_str}\n---\n"

    body = agent_data.get("system_prompt") or ""
    return f"{frontmatter}{body}"


@mcp.prompt()
def agent_session(agent_name: str, username: str, skills: str = "") -> str:
    """
    Assembles a complete agent system prompt containing:
    1. Agent Persona (Personality)
    2. User Profile (Constraints/Lore)
    3. Custom Skills (Abilities)
    """
    return session_service.build_session_prompt(
        agent_name=agent_name, username=username, skills=skills
    )
