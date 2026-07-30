import pytest
from unittest.mock import patch

# We import the functions to test (these will initially fail to import during Red-TDD)
try:
    from worksbyworrell.warlock.pipeline.normalizer import normalize_keys
    from worksbyworrell.warlock.pipeline.crawler import crawl_standard_directory, crawl_skills_directory
except ImportError:
    normalize_keys = None
    crawl_standard_directory = None
    crawl_skills_directory = None


# Ensure mock functions/modules exist for RED TDD execution
def test_modules_are_defined():
    assert normalize_keys is not None, "normalizer module/function is not yet defined."
    assert crawl_standard_directory is not None, "crawler module/function standard-crawl is not yet defined."
    assert crawl_skills_directory is not None, "crawler module/function skills-crawl is not yet defined."


# ============================================================================
# 1. KEY NORMALIZATION TESTS
# ============================================================================

@pytest.mark.skipif(normalize_keys is None, reason="Normalizer module not yet implemented.")
@pytest.mark.parametrize(
    "input_dict,expected_dict",
    [
        # Test kebab-case normalization
        (
            {"agent-name": "Torque", "model-name": "gemini-2.0"},
            {"agent_name": "Torque", "model_name": "gemini-2.0"}
        ),
        # Test camelCase normalization
        (
            {"agentName": "Clutch", "systemPrompt": "System directive"},
            {"agent_name": "Clutch", "system_prompt": "System directive"}
        ),
        # Test PascalCase normalization
        (
            {"UserProfile": "raworre", "MetadataDetails": {"key": "val"}},
            {"user_profile": "raworre", "metadata_details": {"key": "val"}}
        ),
        # Test uppercase and mixed cases
        (
            {"API_KEY": "12345", "camelCase_mixed-kebab": True},
            {"api_key": "12345", "camel_case_mixed_kebab": True}
        ),
        # Test nested dictionary key normalization
        (
            {"agent-details": {"nested-key-one": 1, "nestedTwo": 2}},
            {"agent_details": {"nested_key_one": 1, "nested_two": 2}}
        )
    ]
)
def test_normalize_keys_converts_to_snake_case(input_dict, expected_dict):
    """Verify that input keys in various naming formats are normalized recursively to snake_case."""
    assert normalize_keys(input_dict) == expected_dict


# ============================================================================
# 2. CRAWLER TESTS (STANDARD DOMAINS: AGENTS, PROFILES, RESOURCES)
# ============================================================================

@pytest.mark.skipif(crawl_standard_directory is None, reason="Crawler module not yet implemented.")
def test_crawl_standard_directory_extracts_yaml_and_body(tmp_path):
    """
    Verify that crawl_standard_directory traverses the directory,
    parses yaml frontmatter + markdown body, and returns standard document schemas mapped by ID.
    """
    # Set up mock folder structure
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    
    # 1. Write file with frontmatter
    (agents_dir / "torque.md").write_text(
        "---\n"
        "agent-name: Torque\n"
        "modelName: gemini-2.0\n"
        "---\n"
        "You are Torque."
    )
    
    # 2. Write file without frontmatter (plain instructions)
    (agents_dir / "clutch.md").write_text(
        "You are Clutch."
    )
    
    # 3. Write non-markdown file (should be ignored)
    (agents_dir / "notes.txt").write_text("Ignore this file.")

    # Act
    results = crawl_standard_directory(str(agents_dir))

    # Assert
    assert len(results) == 2
    assert "torque" in results
    assert "clutch" in results

    # Check parsed details for torque (including raw YAML frontmatter attributes)
    torque_data = results["torque"]
    assert torque_data["agent-name"] == "Torque"
    assert torque_data["modelName"] == "gemini-2.0"
    assert torque_data["system_prompt"] == "You are Torque."

    # Check parsed details for clutch (should have empty frontmatter fields but system_prompt populated)
    clutch_data = results["clutch"]
    assert clutch_data["system_prompt"] == "You are Clutch."


@pytest.mark.skipif(crawl_standard_directory is None, reason="Crawler module not yet implemented.")
def test_crawl_standard_directory_missing_path_returns_empty():
    """Verify that crawling a non-existent directory returns an empty dictionary gracefully."""
    results = crawl_standard_directory("/non/existent/path/for/sure")
    assert results == {}


# ============================================================================
# 3. CRAWLER TESTS (SKILL DOMAIN: NESTED SKILL.MD DIRECTORY STRUCT)
# ============================================================================

@pytest.mark.skipif(crawl_skills_directory is None, reason="Crawler module not yet implemented.")
def test_crawl_skills_directory_extracts_nested_skills(tmp_path):
    """
    Verify that crawl_skills_directory crawls folders,
    finding SKILL.md under subdirectories, and registers each using the subfolder name as the skill_id.
    """
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()

    # Set up mock skill folders
    guide_dir = skills_dir / "antigravity-guide"
    guide_dir.mkdir()
    (guide_dir / "SKILL.md").write_text(
        "---\n"
        "skillName: Antigravity Guide\n"
        "---\n"
        "Read this guide."
    )

    helper_dir = skills_dir / "git-helper"
    helper_dir.mkdir()
    (helper_dir / "SKILL.md").write_text(
        "Help with git operations."
    )

    # Folder without SKILL.md (should be ignored)
    empty_dir = skills_dir / "empty-skill"
    empty_dir.mkdir()
    (empty_dir / "README.md").write_text("Not a skill file.")

    # Act
    results = crawl_skills_directory(str(skills_dir))

    # Assert
    assert len(results) == 2
    assert "antigravity-guide" in results
    assert "git-helper" in results
    assert "empty-skill" not in results

    # Verify guide details
    guide_data = results["antigravity-guide"]
    assert guide_data["skillName"] == "Antigravity Guide"
    assert guide_data["system_prompt"] == "Read this guide."

    # Verify helper details
    helper_data = results["git-helper"]
    assert helper_data["system_prompt"] == "Help with git operations."


@pytest.mark.skipif(crawl_skills_directory is None, reason="Crawler module not yet implemented.")
def test_crawl_skills_directory_missing_path_returns_empty():
    """Verify that crawling a non-existent skills directory returns an empty dictionary gracefully."""
    results = crawl_skills_directory("/non/existent/skills/path")
    assert results == {}
