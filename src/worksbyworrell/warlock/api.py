import logging
import httpx
from starlette.requests import Request
from starlette.responses import JSONResponse

from worksbyworrell.warlock.repository import get_agent_repository

logger = logging.getLogger(__name__)

async def get_daemon_agent(request: Request):
    """
    Lightweight REST fallback endpoint to retrieve the Daemon agent definition.
    Bypasses MCP layers and uses the extraction repository directly.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        logger.warning("Missing or invalid Authorization header in /api/daemon fallback")
        return JSONResponse({"error": "Missing or invalid Authorization header"}, status_code=401)
        
    token = auth_header.split(" ", 1)[1]
    
    # Manually validate GCP Identity token via tokeninfo endpoint
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={token}")
        if response.status_code != 200:
            logger.error(f"GCP token validation failed: {response.text}")
            return JSONResponse({"error": "Invalid GCP Identity token"}, status_code=401)
            
    # Default to fetching 'daemon' if no specific agent was provided in the query string
    agent_name = request.query_params.get("agent_name", "daemon")
    
    try:
        agent_data = get_agent_repository().get_agent(agent_name)
        if not agent_data:
            return JSONResponse({"error": f"Agent '{agent_name}' not found"}, status_code=404)
        
        return JSONResponse(agent_data)
    except Exception as e:
        logger.error(f"Failed to fetch agent '{agent_name}' in fallback API: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)
