import os

from worksbyworrell.warlock.repository.agent import GithubAgentRepository, LocalAgentRepository
from worksbyworrell.warlock.repository.base import (
    AgentRepository,
    ResourceRepository,
    SkillMetadataRepository,
    UserProfileRepository,
)
from worksbyworrell.warlock.repository.profile import (
    GithubUserProfileRepository,
    LocalUserProfileRepository,
)
from worksbyworrell.warlock.repository.resource import (
    GithubResourceRepository,
    LocalResourceRepository,
)
from worksbyworrell.warlock.repository.skill import (
    GithubSkillMetadataRepository,
    LocalSkillMetadataRepository,
)


def get_agent_repository() -> AgentRepository:
    if os.environ.get("GITHUB_TOKEN"):
        return GithubAgentRepository()
    return LocalAgentRepository()


def get_profile_repository() -> UserProfileRepository:
    if os.environ.get("GITHUB_TOKEN"):
        return GithubUserProfileRepository()
    return LocalUserProfileRepository()


def get_resource_repository() -> ResourceRepository:
    if os.environ.get("GITHUB_TOKEN"):
        return GithubResourceRepository()
    return LocalResourceRepository()


def get_skill_repository() -> SkillMetadataRepository:
    if os.environ.get("GITHUB_TOKEN"):
        return GithubSkillMetadataRepository()
    return LocalSkillMetadataRepository()
