import importlib.util
import inspect
import logging
import os

from ..core import PROJECT_ROOT, mcp

logger = logging.getLogger(__name__)


def get_skill_path(skill_name: str) -> str:
    return os.path.join(PROJECT_ROOT, ".skills", skill_name, "SKILL.md")


@mcp.resource("skill://{skill_name}")
def get_skill_instructions(skill_name: str) -> str:
    """Returns instructions and metadata from a skill's SKILL.md file."""
    path = get_skill_path(skill_name)
    if not os.path.exists(path):
        return f"Error: Skill '{skill_name}' not found."

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_dynamic_skills_tools():
    """Scans the skills/ directory and dynamically registers functions in tools.py as MCP tools."""
    skills_dir = os.path.join(PROJECT_ROOT, ".skills")
    if not os.path.exists(skills_dir):
        os.makedirs(skills_dir, exist_ok=True)
        return

    for skill_name in os.listdir(skills_dir):
        skill_path = os.path.join(skills_dir, skill_name)
        if not os.path.isdir(skill_path):
            continue

        tools_file = os.path.join(skill_path, "tools.py")
        if os.path.exists(tools_file):
            try:
                # Dynamic import namespace setup
                module_name = f"warlock.skills.{skill_name}.tools"
                spec = importlib.util.spec_from_file_location(module_name, tools_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Inspect and register functions
                registered_count = 0
                for name, func in inspect.getmembers(module, inspect.isfunction):
                    # Only register functions defined in the tools.py file itself
                    # (not imported helper libraries)
                    if func.__module__ == module_name and not name.startswith("_"):
                        mcp.add_tool(func)
                        registered_count += 1

                logger.info(
                    f"Dynamically registered {registered_count} tools for skill: {skill_name}"
                )
            except Exception as e:
                logger.error(f"Failed to load tools for skill '{skill_name}': {e}")
