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
    project_id = os.environ.get("GCP_PROJECT_ID")
    if project_id:
        return GithubAgentRepository()
    return LocalAgentRepository()


def get_profile_repository() -> UserProfileRepository:
    project_id = os.environ.get("GCP_PROJECT_ID")
    if project_id:
        return GithubUserProfileRepository()
    return LocalUserProfileRepository()


def get_resource_repository() -> ResourceRepository:
    project_id = os.environ.get("GCP_PROJECT_ID")
    if project_id:
        return GithubResourceRepository()
    return LocalResourceRepository()


def get_skill_repository() -> SkillMetadataRepository:
    project_id = os.environ.get("GCP_PROJECT_ID")
    if project_id:
        return GithubSkillMetadataRepository()
    return LocalSkillMetadataRepository()
