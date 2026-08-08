import os
from typing import Any, Dict

from worksbyworrell.warlock.repository.base import UserProfileRepository
from worksbyworrell.warlock.repository.github import fetch_github_file
from worksbyworrell.warlock.repository.parser import parse_content, parse_file

USER_PROFILES = "user_profiles"
USER_PROFILE_OVERLAYS = "user_profile_overlays"


def _merge(username: str, public_data: dict, private_data: dict) -> Dict[str, Any]:
    public_prompt = public_data.pop("system_prompt", "")
    private_prompt = private_data.pop("system_prompt", "")

    return {
        "username": username,
        **public_data,
        **private_data,
        "public_prompt": public_prompt,
        "private_prompt": private_prompt,
    }


# noinspection DuplicatedCode
class LocalUserProfileRepository(UserProfileRepository):
    """Strategy to read user profile configurations from the local filesystem."""

    def __init__(self, public_dir: str | None = None, private_dir: str | None = None):
        self.public_dir = public_dir or os.environ.get("WARLOCK_CONFIG_DIR", "./.public/profiles")
        self.private_dir = private_dir or os.environ.get(
            "WARLOCK_PRIVATE_CONFIG_DIR", "./.private/profiles"
        )

    def get_profile(self, username: str) -> Dict[str, Any]:
        """Get merged user profile data from local filesystem."""
        public_path = os.path.join(self.public_dir, f"{username}.md")
        private_path = os.path.join(self.private_dir, f"{username}.md")

        public_data = parse_file(public_path)
        private_data = parse_file(private_path)

        return _merge(username, public_data, private_data)


class GithubUserProfileRepository(UserProfileRepository):
    """Strategy to read user profile configurations from GitHub API."""

    def __init__(self):
        pass

    def get_profile(self, username: str) -> Dict[str, Any]:
        """Get merged user profile data from GitHub API."""
        public_raw = fetch_github_file("wbw-config", f"profiles/{username}.md")
        public_data = parse_content(public_raw) if public_raw else {}

        private_raw = fetch_github_file("wbw-config-private", f"profiles/{username}.md")
        private_data = parse_content(private_raw) if private_raw else {}

        return _merge(username, public_data, private_data)
