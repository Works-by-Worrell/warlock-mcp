import os
import httpx
import logging
from ..core import mcp

logger = logging.getLogger(__name__)

async def _fetch_github_config(path: str, resource_name: str) -> str:
    """Internal helper to fetch markdown configuration from the wbw-config-private GitHub repo."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return f"Error: GITHUB_TOKEN environment variable is not set. Cannot fetch {resource_name}."
        
    repo = "Works-by-Worrell/wbw-config-private"
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3.raw",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    logger.info(f"Fetching {resource_name} from {repo}/{path}")
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 404:
                return f"Error: {resource_name} not found in the organizational registry at {path}."
            resp.raise_for_status()
            return resp.text
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch {resource_name} from GitHub: {e}")
            return f"Error: Failed to fetch {resource_name}: {e}"

@mcp.tool()
async def fetch_org_agent(agent_name: str) -> str:
    """
    Dynamically fetches the system prompt and governance rules for a specific organizational agent.
    Bypasses CI/CD lag by pulling the markdown file directly from the GitHub repository.
    """
    return await _fetch_github_config(f"agents/{agent_name}.md", f"Agent '{agent_name}'")

@mcp.tool()
async def fetch_user_profile(profile_name: str) -> str:
    """
    Dynamically fetches a user profile (e.g. baseline resume or personal config).
    Bypasses CI/CD lag by pulling the markdown file directly from the GitHub repository.
    """
    return await _fetch_github_config(f"profiles/{profile_name}.md", f"Profile '{profile_name}'")
