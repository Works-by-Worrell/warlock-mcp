import os
from typing import Any, Dict, Tuple

import yaml


def extract_frontmatter_and_body(content: str) -> Tuple[str, str]:
    """Helper function to extract frontmatter and body."""
    lines = content.split("\n")
    if lines and lines[0].strip() == "---":
        end_idx = -1
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                end_idx = i
                break

        if end_idx != -1:
            frontmatter = "\n".join(lines[1:end_idx])
            body = "\n".join(lines[end_idx + 1 :])
            return frontmatter, body

    return "", content


def parse_file(file_path: str) -> Dict[str, Any]:
    """Helper function to parse Markdown files."""
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        raw_content = f.read()

    fm_str, body_str = extract_frontmatter_and_body(raw_content)

    data = yaml.safe_load(fm_str) if fm_str else {}
    if not isinstance(data, dict):
        data = {}

    data["system_prompt"] = body_str.strip()
    return data
