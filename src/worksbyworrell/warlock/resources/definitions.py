from worksbyworrell.core.repository import get_resource_repository

from worksbyworrell.warlock.core import mcp, resource_uri


@mcp.resource(resource_uri("definitions/ready"))
def get_definition_of_ready() -> str:
    """Returns the Definition of Ready for YouTrack tickets."""
    data = get_resource_repository().get_resource("definitions/ready")
    return data.get("system_prompt") or ""
