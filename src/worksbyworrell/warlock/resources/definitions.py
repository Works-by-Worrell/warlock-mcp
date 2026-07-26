import os

from ..core import PROJECT_ROOT, mcp, resource_uri


@mcp.resource(resource_uri("definitions/ready"))
def get_definition_of_ready() -> str:
    """Returns the Definition of Ready for YouTrack tickets."""
    path = os.path.join(PROJECT_ROOT, ".public", "resources", "DEFINITION_OF_READY.md")

    if not os.path.exists(path):
        return "Error: DEFINITION_OF_READY.md not found."

    with open(path) as f:
        return f.read()
