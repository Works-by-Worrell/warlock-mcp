import os
from typing import Any, Dict

from google.cloud import firestore

from worksbyworrell.warlock.repository.base import UserProfileRepository
from worksbyworrell.warlock.repository.parser import parse_file

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


class FirestoreUserProfileRepository(UserProfileRepository):
    """Strategy to read user profile configurations from Firestore collections."""

    def __init__(self, client: firestore.Client | None = None):
        self.client = client or firestore.Client()

    def get_profile(self, username: str) -> Dict[str, Any]:
        """Get merged user profile data from Firestore."""
        public_ref = self.client.collection(USER_PROFILES).document(f"{username}.md")
        public_data = public_ref.get().to_dict() or {}

        private_ref = self.client.collection(USER_PROFILE_OVERLAYS).document(f"{username}.md")
        private_data = private_ref.get().to_dict() or {}

        return _merge(username, public_data, private_data)
