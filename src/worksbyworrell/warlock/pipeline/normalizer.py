import re
from typing import Any


def normalize_key_str(key: str) -> str:
    """
    Normalizes a single string key to snake_case.

    Transforms camelCase, PascalCase, kebab-case, and mixed cases to standard snake_case.
    For example:
    - agent-name -> agent_name
    - agentName -> agent_name
    - UserProfile -> user_profile
    - API_KEY -> api_key
    - camelCase_mixed-kebab -> camel_case_mixed_kebab
    """
    s = key.replace("-", "_")
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", s)
    s = re.sub(r"_+", "_", s)
    return s.lower().strip("_")


def normalize_keys(data: Any) -> Any:
    """
    Recursively normalizes dictionary keys to snake_case.

    Handles nested dictionaries and lists of dictionaries.
    """
    if isinstance(data, dict):
        return {normalize_key_str(k): normalize_keys(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [normalize_keys(item) for item in data]
    return data
