import logging

from starlette.requests import Request
from starlette.responses import JSONResponse

from worksbyworrell.warlock.repository import get_agent_repository

logger = logging.getLogger(__name__)


async def get_daemon_agent(request: Request):
    """
    Lightweight REST fallback endpoint to retrieve the Daemon agent definition.
    Bypasses MCP layers and uses the extraction repository directly.

    Authentication is handled at the Cloud Run IAM layer. Any request reaching
    this handler has already been authenticated by Google infrastructure.
    """
    # Default to fetching 'daemon' if no specific agent was provided
    agent_name = request.query_params.get("agent_name", "daemon")

    try:
        agent_data = get_agent_repository().get_agent(agent_name)
        if not agent_data:
            return JSONResponse(
                {"error": f"Agent '{agent_name}' not found"}, status_code=404
            )
        return JSONResponse(agent_data)
    except Exception as e:
        logger.error(f"Failed to fetch agent '{agent_name}' in fallback API: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)
