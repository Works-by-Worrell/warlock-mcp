import os
import httpx
import logging
from ..core import mcp

logger = logging.getLogger(__name__)

@mcp.tool()
async def fetch_org_agent(agent_name: str) -> str:
    """
    Dynamically fetches the system prompt and governance rules for a specific organizational agent.
    Bypasses CI/CD lag by pulling the markdown file directly from the GitHub repository.
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return "Error: GITHUB_TOKEN environment variable is not set. Cannot fetch agent definition."
        
    repo = "Works-by-Worrell/wbw-config-private"
    path = f"agents/{agent_name}.md"
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3.raw",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    logger.info(f"Fetching agent definition for '{agent_name}' from {repo}")
    
    async with httpx.AsyncClient() as client:
        try:
            # We use the raw accept header to get the actual markdown content, not the base64 JSON wrapper
            resp = await client.get(url, headers=headers)
            if resp.status_code == 404:
                return f"Error: Agent '{agent_name}' not found in the organizational registry."
            resp.raise_for_status()
            
            return resp.text
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch agent {agent_name} from GitHub: {e}")
            return f"Error: Failed to fetch agent definition: {e}"
