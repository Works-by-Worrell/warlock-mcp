import os

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", "..", ".."))

dotenv_path = os.path.join(PROJECT_ROOT, ".private", ".env")
load_dotenv(dotenv_path=dotenv_path)
mcp = FastMCP("Warlock")

PROFILE_BASE_URI = "profile://"
RESOURCE_BASE_URI = "resource://"


def profile_uri(name: str) -> str:
    return f"{PROFILE_BASE_URI}{{username}}/{name}"


def resource_uri(name: str) -> str:
    return f"{RESOURCE_BASE_URI}{name}"
