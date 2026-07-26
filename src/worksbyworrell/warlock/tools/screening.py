import logging

from ..core import mcp

logger = logging.getLogger(__name__)


@mcp.tool()
async def evaluate_project_fit(brief: str) -> str:
    """
    Evaluates a project or opportunity brief against the Operator's profile.
    Returns a structured JSON assessment. Implementation pending WBW-34.
    """
    return (
        '{"verdict": "NOT_IMPLEMENTED",'
        ' "message": "evaluate_project_fit is a stub pending WBW-34."}'
    )
