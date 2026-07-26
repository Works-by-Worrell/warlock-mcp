import os

from google.cloud import firestore

from worksbyworrell.warlock.repository.agent import FirestoreAgentRepository, LocalAgentRepository
from worksbyworrell.warlock.repository.base import (
    AgentRepository,
    ResourceRepository,
    SkillMetadataRepository,
    UserProfileRepository,
)
from worksbyworrell.warlock.repository.profile import (
    FirestoreUserProfileRepository,
    LocalUserProfileRepository,
)
from worksbyworrell.warlock.repository.resource import (
    FirestoreResourceRepository,
    LocalResourceRepository,
)
from worksbyworrell.warlock.repository.skill import (
    FirestoreSkillMetadataRepository,
    LocalSkillMetadataRepository,
)


def get_agent_repository() -> AgentRepository:
    project_id = os.environ.get("GCP_PROJECT_ID")
    if project_id:
        # noinspection PyTypeChecker
        client = firestore.Client(project=project_id)
        return FirestoreAgentRepository(client)
    return LocalAgentRepository()


def get_profile_repository() -> UserProfileRepository:
    project_id = os.environ.get("GCP_PROJECT_ID")
    if project_id:
        # noinspection PyTypeChecker
        client = firestore.Client(project=project_id)
        return FirestoreUserProfileRepository(client)
    return LocalUserProfileRepository()


def get_resource_repository() -> ResourceRepository:
    project_id = os.environ.get("GCP_PROJECT_ID")
    if project_id:
        # noinspection PyTypeChecker
        client = firestore.Client(project=project_id)
        return FirestoreResourceRepository(client)
    return LocalResourceRepository()


def get_skill_repository() -> SkillMetadataRepository:
    project_id = os.environ.get("GCP_PROJECT_ID")
    if project_id:
        # noinspection PyTypeChecker
        client = firestore.Client(project=project_id)
        return FirestoreSkillMetadataRepository(client)
    return LocalSkillMetadataRepository()
