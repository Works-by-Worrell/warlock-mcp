import os
from typing import Any, Dict

import yaml

from worksbyworrell.warlock.repository.base import AgentRepository
from worksbyworrell.warlock.repository.github import fetch_github_file
from worksbyworrell.warlock.repository.parser import parse_content, parse_file

AGENT_CONFIGURATIONS = "agent_configurations"
AGENT_OVERLAYS = "agent_overlays"


def _merge(
    agent_id: str, public_data: Dict[str, Any], private_data: Dict[str, Any]
) -> Dict[str, Any]:
    public_prompt = public_data.pop("system_prompt", "")
    private_prompt = private_data.pop("system_prompt", "")

    merged = {
        "agent_id": agent_id,
        **public_data,
        **private_data,
    }

    prompt_parts = []
    if public_prompt:
        prompt_parts.append(public_prompt)
    if private_prompt:
        prompt_parts.append(private_prompt)

    if not prompt_parts:
        merged["system_prompt"] = f"Error: No configuration found for agent '{agent_id}'"
    else:
        body_str = "\n\n---\n\n".join(prompt_parts)
        fm_dict = {k: v for k, v in merged.items() if k != "system_prompt"}
        if fm_dict:
            fm_str = yaml.dump(fm_dict, sort_keys=False).strip()
            merged["system_prompt"] = f"---\n{fm_str}\n---\n\n{body_str}"
        else:
            merged["system_prompt"] = body_str

    return merged


# noinspection DuplicatedCode
class LocalAgentRepository(AgentRepository):
    """Strategy to read agent configurations from the local filesystem."""

    def __init__(self, public_dir: str | None = None, private_dir: str | None = None):
        self.public_dir = public_dir or os.environ.get("WARLOCK_CONFIG_DIR", "./.public/agents")
        self.private_dir = private_dir or os.environ.get(
            "WARLOCK_PRIVATE_CONFIG_DIR", "./.private/agents"
        )

    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """Get merged agent configuration from local filesystem."""
        public_path = os.path.join(self.public_dir, f"{agent_id}.md")
        private_path = os.path.join(self.private_dir, f"{agent_id}.md")

        public_data = parse_file(public_path)
        private_data = parse_file(private_path)

        return _merge(agent_id, public_data, private_data)


class GithubAgentRepository(AgentRepository):
    """Strategy to read agent configurations from GitHub API."""

    def __init__(self):
        pass

    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """Get merged agent configuration from GitHub API."""
        public_raw = fetch_github_file("wbw-config", f"agents/{agent_id}.md")
        public_data = parse_content(public_raw) if public_raw else {}

        private_raw = fetch_github_file("wbw-config-private", f"agents/{agent_id}.md")
        private_data = parse_content(private_raw) if private_raw else {}

        return _merge(agent_id, public_data, private_data)
