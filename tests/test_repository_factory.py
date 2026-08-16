from worksbyworrell.core.repository import (
    get_agent_repository,
    get_profile_repository,
    get_resource_repository,
    get_skill_repository,
)
from worksbyworrell.core.repository.agent import LocalAgentRepository
from worksbyworrell.core.repository.profile import LocalUserProfileRepository
from worksbyworrell.core.repository.resource import (
    LocalResourceRepository,
)
from worksbyworrell.core.repository.skill import (
    LocalSkillMetadataRepository,
)


def test_factory_resolves_local_when_github_token_absent(monkeypatch):
    """Verify resolvers default to local strategies when GITHUB_TOKEN is not set."""
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    assert isinstance(get_agent_repository(), LocalAgentRepository)
    assert isinstance(get_profile_repository(), LocalUserProfileRepository)
    assert isinstance(get_resource_repository(), LocalResourceRepository)
    assert isinstance(get_skill_repository(), LocalSkillMetadataRepository)
