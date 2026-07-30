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


def _get_firestore_client(project_id: str) -> firestore.Client:
    database_id = os.environ.get("GCP_DATABASE_ID", "(default)")
    # noinspection PyTypeChecker
    return firestore.Client(project=project_id, database=database_id)


def get_agent_repository() -> AgentRepository:
    project_id = os.environ.get("GCP_PROJECT_ID")
    if project_id:
        return FirestoreAgentRepository(_get_firestore_client(project_id))
    return LocalAgentRepository()


def get_profile_repository() -> UserProfileRepository:
    project_id = os.environ.get("GCP_PROJECT_ID")
    if project_id:
        return FirestoreUserProfileRepository(_get_firestore_client(project_id))
    return LocalUserProfileRepository()


def get_resource_repository() -> ResourceRepository:
    project_id = os.environ.get("GCP_PROJECT_ID")
    if project_id:
        return FirestoreResourceRepository(_get_firestore_client(project_id))
    return LocalResourceRepository()


def get_skill_repository() -> SkillMetadataRepository:
    project_id = os.environ.get("GCP_PROJECT_ID")
    if project_id:
        return FirestoreSkillMetadataRepository(_get_firestore_client(project_id))
    return LocalSkillMetadataRepository()
