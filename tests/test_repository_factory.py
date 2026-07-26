import os
import pytest
from worksbyworrell.warlock.repository import (
    get_agent_repository,
    get_profile_repository,
    get_resource_repository,
    get_skill_repository
)
from worksbyworrell.warlock.repository.agent import LocalAgentRepository, FirestoreAgentRepository
from worksbyworrell.warlock.repository.profile import LocalUserProfileRepository, FirestoreUserProfileRepository
from worksbyworrell.warlock.repository.resource import LocalResourceRepository, FirestoreResourceRepository
from worksbyworrell.warlock.repository.skill import LocalSkillMetadataRepository, FirestoreSkillMetadataRepository


def test_factory_resolves_local_when_gcp_project_absent(monkeypatch):
    """Verify resolvers default to local strategies when GCP_PROJECT_ID is not set."""
    monkeypatch.delenv("GCP_PROJECT_ID", raising=False)
    
    assert isinstance(get_agent_repository(), LocalAgentRepository)
    assert isinstance(get_profile_repository(), LocalUserProfileRepository)
    assert isinstance(get_resource_repository(), LocalResourceRepository)
    assert isinstance(get_skill_repository(), LocalSkillMetadataRepository)


def test_factory_resolves_firestore_when_gcp_project_present(monkeypatch, mocker):
    """Verify resolvers switch to Firestore strategies when GCP_PROJECT_ID is set."""
    monkeypatch.setenv("GCP_PROJECT_ID", "test-project-123")
    
    # Mock firestore.Client initialization so it doesn't try to touch real GCP
    mocker.patch("google.cloud.firestore.Client")
    
    assert isinstance(get_agent_repository(), FirestoreAgentRepository)
    assert isinstance(get_profile_repository(), FirestoreUserProfileRepository)
    assert isinstance(get_resource_repository(), FirestoreResourceRepository)
    assert isinstance(get_skill_repository(), FirestoreSkillMetadataRepository)
