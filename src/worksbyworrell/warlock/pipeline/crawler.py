import os
from typing import Any, Dict

from worksbyworrell.warlock.repository.parser import parse_file


def crawl_standard_directory(directory_path: str) -> Dict[str, Any]:
    """
    Crawls a standard domain directory (e.g., agents/, profiles/, resources/).

    Parses each Markdown (.md) file using parse_file and maps the results by
    the lowercase filename (without extension) as the document ID.

    If the directory does not exist, returns an empty dictionary gracefully.
    """
    if os.path.exists(directory_path) and os.path.isdir(directory_path):
        directory_data = {}
        for filename in os.listdir(directory_path):
            if filename.endswith(".md"):
                file_path = os.path.join(directory_path, filename)
                doc_id = os.path.splitext(filename)[0].lower()
                directory_data[doc_id] = parse_file(file_path)
        return directory_data
    else:
        return {}


def crawl_skills_directory(directory_path: str) -> Dict[str, Any]:
    """
    Crawls the skills directory.

    Finds subdirectories containing a 'SKILL.md' file. Parses each using parse_file
    and maps the results by the lowercase subdirectory name as the skill ID.

    If the directory does not exist, returns an empty dictionary gracefully.
    """
    if os.path.exists(directory_path) and os.path.isdir(directory_path):
        skills_data = {}
        for skill_dir in os.listdir(directory_path):
            skill_path = os.path.join(directory_path, skill_dir)
            if os.path.isdir(skill_path):
                skill_name = skill_dir.lower()
                file_path = os.path.join(directory_path, skill_dir, "SKILL.md")
                if os.path.exists(file_path):
                    skills_data[skill_name] = parse_file(file_path)
        return skills_data
    return {}
