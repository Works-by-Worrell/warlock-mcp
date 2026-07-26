from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseRepository(ABC):
    """Abstract repository contract."""

    pass


class AgentRepository(ABC):
    @abstractmethod
    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """Fetch the combined public agent configuration and private overlay"""
        pass


class UserProfileRepository(ABC):
    @abstractmethod
    def get_profile(self, username: str) -> Dict[str, Any]:
        """Fetch and merge public and private user alignment profiles."""
        pass


class ResourceRepository(ABC):
    @abstractmethod
    def get_resource(self, resource_id: str) -> Dict[str, Any]:
        """Fetch a specific system resource definition."""
        pass


class SkillMetadataRepository(ABC):
    @abstractmethod
    def get_skill(self, skill_id: str) -> Dict[str, Any]:
        """Fetch instructions and metadata for a specific skill."""
        pass
