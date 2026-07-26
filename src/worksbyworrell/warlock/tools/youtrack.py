import logging
import os

import httpx

from ..core import mcp

logger = logging.getLogger(__name__)


async def _request(method: str, path: str, **kwargs) -> httpx.Response:
    """
    Centralized HTTP executor for YouTrack REST calls.
    Handles dynamic env sourcing, headers injection, URL parsing, and HTTP requests.
    """
    base_url = os.getenv("YOUTRACK_URL")
    token = os.getenv("YOUTRACK_TOKEN")
    headers = {
        "Authorization": f"Bearer {token}",
        **kwargs.pop("headers", {}),
    }

    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"

    async with httpx.AsyncClient() as client:
        resp = await client.request(method, url, headers=headers, **kwargs)
        # Raise HTTPError for bad statuses (4xx, 5xx) so tools can catch them cleanly
        resp.raise_for_status()
        return resp


def _handle_error(e: httpx.HTTPError) -> str:
    """
    DRY helper to handle type-guarded exceptions from HTTPX.
    Ensures PyCharm/IntelliJ's type checker narrows Any | None correctly.
    """
    resp = getattr(e, "response", None)
    if isinstance(resp, httpx.Response):
        logger.error(f"YouTrack API returned error: {resp.status_code} - {resp.text}")
        return f"Failed to fetch details: {resp.status_code} - {resp.text}"

    logger.error(f"YouTrack connection failed: {e}")
    return f"Failed to fetch details: {e}"


@mcp.tool()
async def create_youtrack_issue(
    summary: str,
    description: str,
    tags: list[str] = None,
    priority: str = "Normal",
) -> str:
    """
    Creates a new issue in YouTrack with optional tags and priority.
    Resolves tag names to IDs automatically.
    """
    resolved_tags = []
    if tags:
        try:
            # Fetch all tags to map names to IDs
            logger.info("Resolving tags")
            tags_resp = await _request(
                "GET", "/api/tags?fields=id,name", params={"fields": "id,name"}
            )
            all_tags = tags_resp.json()
            for tag_name in tags:
                # Try to match name exactly or with a leading #
                match = next(
                    (
                        t
                        for t in all_tags
                        if t["name"].lower() == tag_name.lower()
                        or t["name"].lower() == f"#{tag_name.lower()}"
                    ),
                    None,
                )
                if match:
                    resolved_tags.append({"id": match["id"]})
        except httpx.HTTPError as e:
            logger.warning(f"Failed to resolve tags: {e}")

    payload = {
        "project": {"shortName": os.getenv("YOUTRACK_PROJECT_KEY")},
        "summary": summary,
        "description": description,
        "customFields": [
            {"name": "Priority", "$type": "SingleEnumIssueCustomField", "value": {"name": priority}}
        ],
    }

    if resolved_tags:
        payload["tags"] = resolved_tags

    logger.info("Writing new YouTrack issue")

    try:
        resp = await _request("POST", "/api/issues", params={"fields": "idReadable"}, json=payload)

        data = resp.json()
        issue_id = data["idReadable"]
        base_url = os.getenv("YOUTRACK_URL")
        if base_url is None:
            base_url = "http://localhost"
        issue_url = f"{base_url.rstrip('/')}/issues/{issue_id}"
        return f"Created new issue: [{issue_id}] - {issue_url}"
    except httpx.HTTPError as e:
        return _handle_error(e)


@mcp.tool()
async def search_youtrack_issues(query: str, max_results: int = 10) -> str:
    """
    Search YouTrack for issues matching the query.

    Supports standard YouTrack search query syntax, including:
    - Unresolved tickets: "#Unresolved"
    - Board and Sprint specific lists: "Board {Board Name}: {Sprint Name}"
        (e.g., "Board Warlock MCP: Sprint.001")
    - Specific tags: "tag: #Warlock"
    """
    logger.info(f"Searching YouTrack issues: {query}")
    params = {
        "query": query,
        "$top": max_results,
        "fields": "idReadable,summary,customFields(name,value(name))",
    }

    try:
        resp = await _request("GET", "/api/issues", params=params)

        issues = resp.json()

        if not issues:
            return f"No issues found for query: {query}"

        content = [f"## Search Results - {query}\n"]
        for issue in issues[:max_results]:
            stage_field = next(
                (f for f in issue.get("customFields", []) if f["name"] == "Stage"),
                None,
            )
            status = (
                stage_field["value"]["name"]
                if stage_field and stage_field.get("value")
                else "Unknown"
            )
            content.append(f"- **{issue['idReadable']}**: {issue['summary']} [{status}]")
        return "\n".join(content)
    except httpx.HTTPError as e:
        return _handle_error(e)


@mcp.tool()
async def get_youtrack_issue_details(issue_id: str) -> str:
    """
    Fetch details about a given YouTrack issue.
    """
    logger.info(f"Fetching details for YouTrack issue: {issue_id}")
    try:
        resp = await _request(
            "GET",
            f"/api/issues/{issue_id}",
            params={
                "fields": "idReadable,summary,description,tags(name),customFields(name,value(name))"
            },
        )
        issue = resp.json()

        if not issue:
            return f"Failed to find issue: {issue_id}"

        stage_field = next(
            (f for f in issue.get("customFields", []) if f["name"] == "Stage"),
            None,
        )
        status = (
            stage_field["value"]["name"] if stage_field and stage_field.get("value") else "Unknown"
        )
        tags_list = issue.get("tags") or []
        tags_str = ", ".join(f"#{tag['name']}" for tag in tags_list) or "None"

        content = [
            f"# {issue['idReadable']} - {issue['summary']}\n",
            f"- **Status**: {status}\n",
            f"- **Tags**: {tags_str}\n",
            f"- **Description**:\n{issue.get('description', 'No description provided.')}",
        ]

        return "\n".join(content)
    except httpx.HTTPError as e:
        return _handle_error(e)


@mcp.tool()
async def update_youtrack_issue(
    issue_id: str,
    summary: str = None,
    description: str = None,
    priority: str = None,
    stage: str = None,
) -> str:
    """
    Updates an existing YouTrack issue.
    Allows updating the summary, description, priority, and stage/status.
    """
    payload = {}
    if summary is not None:
        payload["summary"] = summary
    if description is not None:
        payload["description"] = description

    custom_fields = []
    if priority is not None:
        custom_fields.append(
            {"name": "Priority", "$type": "SingleEnumIssueCustomField", "value": {"name": priority}}
        )
    if stage is not None:
        custom_fields.append(
            {"name": "Stage", "$type": "StateIssueCustomField", "value": {"name": stage}}
        )

    if custom_fields:
        payload["customFields"] = custom_fields

    if not payload:
        return "No updates specified"

    logger.info(f"Updating YouTrack issue {issue_id} with fields {list(payload.keys())}")

    try:
        await _request(
            "POST",
            f"/api/issues/{issue_id}",
            params={"fields": "idReadable"},
            json=payload,
        )
        logger.info(f"Successfully updated YouTrack issue {issue_id}")
        return f"Successfully updated YouTrack issue {issue_id}"
    except httpx.HTTPError as e:
        return _handle_error(e)
