"""
Card 2: Repo Auth & Discovery Logic

Walks a GitHub or GitLab repository's file tree (recursively) using their
respective REST APIs, finds files matching the target spec patterns, and
returns their raw content — all via async httpx calls.
"""
import fnmatch
import re
from dataclasses import dataclass

import httpx

# Files we want to find and parse
TARGET_PATTERNS = [
    "swagger.json",
    "openapi.json",
    "openapi.yaml",
    "openapi.yml",
    "swagger.yaml",
    "swagger.yml",
    "*.postman_collection.json",
]

GITHUB_API = "https://api.github.com"
GITLAB_API = "https://gitlab.com/api/v4"


@dataclass
class DiscoveredFile:
    path: str
    content: str


def _detect_provider(repo_url: str) -> str:
    """Return 'github' or 'gitlab' based on the repo URL."""
    if "github.com" in repo_url:
        return "github"
    if "gitlab.com" in repo_url:
        return "gitlab"
    raise ValueError(f"Unsupported git host in URL: {repo_url}")


def _parse_github_url(repo_url: str) -> tuple[str, str]:
    """Extract (owner, repo) from a GitHub HTTPS URL."""
    match = re.search(r"github\.com/([^/]+)/([^/?.]+)", repo_url)
    if not match:
        raise ValueError(f"Cannot parse GitHub URL: {repo_url}")
    return match.group(1), match.group(2).removesuffix(".git")


def _parse_gitlab_url(repo_url: str) -> str:
    """Extract the URL-encoded project path from a GitLab HTTPS URL."""
    match = re.search(r"gitlab\.com/(.+?)(?:\.git)?$", repo_url)
    if not match:
        raise ValueError(f"Cannot parse GitLab URL: {repo_url}")
    return match.group(1).replace("/", "%2F")


def _matches_target(filename: str) -> bool:
    """Return True if the filename matches any of the TARGET_PATTERNS."""
    name = filename.split("/")[-1]
    return any(fnmatch.fnmatch(name, pat) for pat in TARGET_PATTERNS)


async def _github_discover(
    client: httpx.AsyncClient, owner: str, repo: str
) -> list[DiscoveredFile]:
    """Fetch the recursive file tree from GitHub and download matching files."""
    # Resolve default branch
    repo_resp = await client.get(f"{GITHUB_API}/repos/{owner}/{repo}")
    repo_resp.raise_for_status()
    default_branch = repo_resp.json()["default_branch"]

    # Get full recursive tree
    tree_resp = await client.get(
        f"{GITHUB_API}/repos/{owner}/{repo}/git/trees/{default_branch}",
        params={"recursive": "1"},
    )
    tree_resp.raise_for_status()
    tree = tree_resp.json().get("tree", [])

    # Filter to blob (file) nodes matching our patterns
    target_files = [
        node["path"]
        for node in tree
        if node["type"] == "blob" and _matches_target(node["path"])
    ]

    # Fetch raw content for each match concurrently
    results: list[DiscoveredFile] = []
    for path in target_files:
        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{default_branch}/{path}"
        raw_resp = await client.get(raw_url)
        raw_resp.raise_for_status()
        results.append(DiscoveredFile(path=path, content=raw_resp.text))

    return results


async def _gitlab_discover(
    client: httpx.AsyncClient, project_path: str
) -> list[DiscoveredFile]:
    """Fetch the recursive file tree from GitLab and download matching files."""
    # Resolve default branch
    project_resp = await client.get(f"{GITLAB_API}/projects/{project_path}")
    project_resp.raise_for_status()
    default_branch = project_resp.json()["default_branch"]

    # Walk tree recursively (GitLab paginates at 100 items)
    all_files: list[str] = []
    page = 1
    while True:
        tree_resp = await client.get(
            f"{GITLAB_API}/projects/{project_path}/repository/tree",
            params={"recursive": "true", "per_page": 100, "page": page},
        )
        tree_resp.raise_for_status()
        items = tree_resp.json()
        if not items:
            break
        all_files.extend(
            item["path"] for item in items
            if item["type"] == "blob" and _matches_target(item["path"])
        )
        if len(items) < 100:
            break
        page += 1

    # Fetch raw content
    results: list[DiscoveredFile] = []
    for path in all_files:
        encoded_path = path.replace("/", "%2F")
        raw_resp = await client.get(
            f"{GITLAB_API}/projects/{project_path}/repository/files/{encoded_path}/raw",
            params={"ref": default_branch},
        )
        raw_resp.raise_for_status()
        results.append(DiscoveredFile(path=path, content=raw_resp.text))

    return results


async def discover_api_files(repo_url: str, token: str) -> list[DiscoveredFile]:
    """
    Entry point: given a repo URL and auth token, return all discovered
    API spec files (path + raw content) from the repository.
    """
    provider = _detect_provider(repo_url)

    headers = {"Accept": "application/json"}
    if provider == "github":
        headers["Authorization"] = f"Bearer {token}"
    else:
        headers["PRIVATE-TOKEN"] = token

    async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
        if provider == "github":
            owner, repo = _parse_github_url(repo_url)
            return await _github_discover(client, owner, repo)
        else:
            project_path = _parse_gitlab_url(repo_url)
            return await _gitlab_discover(client, project_path)
