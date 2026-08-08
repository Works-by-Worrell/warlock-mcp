import logging

from worksbyworrell.warlock.repository import get_agent_repository, get_profile_repository

from ..core import mcp

logger = logging.getLogger(__name__)


@mcp.tool()
async def fetch_org_agent(agent_name: str) -> str:
    """
    Dynamically fetches the system prompt and instructions for a specific organizational agent.
    Query the AgentRepository to retrieve the required agent instructions.
    """
    try:
        agent_data = get_agent_repository().get_agent(agent_name)
        prompt = agent_data.get("system_prompt")
        if not prompt:
            return f"Error: No configuration found for agent '{agent_name}'"
        return prompt
    except Exception as e:
        logger.error(f"Failed to fetch agent '{agent_name}': {e}")
        return f"Error: Failed to fetch agent '{agent_name}': {e}"


@mcp.tool()
async def fetch_user_profile(profile_name: str) -> str:
    """
    Dynamically fetches a user profile (e.g. baseline resume or personal config).
    Bypasses CI/CD lag by pulling the markdown file directly from the GitHub repository.
    """
    try:
        profile_data = get_profile_repository().get_profile(profile_name)
        public_prompt = profile_data.get("public_prompt", "")
        private_prompt = profile_data.get("private_prompt", "")
        
        if not public_prompt and not private_prompt:
            return f"Error: No configuration found for profile '{profile_name}'"
            
        return f"{public_prompt}\n\n{private_prompt}".strip()
    except Exception as e:
        logger.error(f"Failed to fetch profile '{profile_name}': {e}")
        return f"Error: Failed to fetch profile '{profile_name}': {e}"
