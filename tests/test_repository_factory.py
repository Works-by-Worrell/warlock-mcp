from worksbyworrell.core.repository import (
    get_agent_repository,
    get_profile_repository,
    get_resource_repository,
    get_skill_repository,
)
from worksbyworrell.core.repository.agent import LocalAgentRepository
from worksbyworrell.core.repository.profile import (
    CombinedProfileRepository,
)
from worksbyworrell.core.repository.resource import (
    LocalDefinitionRepository,
)
from worksbyworrell.core.repository.skill import (
    LocalSkillMetadataRepository,
)


def test_factory_resolves_local_when_gcp_project_absent(monkeypatch):
    """Verify resolvers default to local strategies when GCP_PROJECT_ID is not set."""
    monkeypatch.delenv("GCP_PROJECT_ID", raising=False)

    assert isinstance(get_agent_repository(), LocalAgentRepository)
    assert isinstance(get_profile_repository(), LocalUserProfileRepository)
    assert isinstance(get_resource_repository(), LocalResourceRepository)
    assert isinstance(get_skill_repository(), LocalSkillMetadataRepository)
