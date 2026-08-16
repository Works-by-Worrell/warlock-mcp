from worksbyworrell.warlock.core import mcp, profile_uri
from worksbyworrell.core.repository import get_profile_repository


@mcp.resource(profile_uri("public"))
def get_public_profile(username: str) -> str:
    """Returns the public technical profile"""
    data = get_profile_repository().get_profile(username)
    return data.get("public_prompt") or ""


@mcp.resource(profile_uri("private"))
def get_private_profile(username: str) -> str:
    """
    Safely returns local personal alignment constraints and distilled identity
    lore from the gitignored boundary.
    """
    data = get_profile_repository().get_profile(username)
    return data.get("private_prompt") or ""


@mcp.resource(profile_uri("combined"))
def get_combined_profile(username: str) -> str:
    data = get_profile_repository().get_profile(username)
    public = data.get("public_prompt") or ""
    private = data.get("private_prompt") or ""
    return f"--- PUBLIC PROFILE ---\n{public}\n\n--- PRIVATE PROFILE ---\n{private}\n"
