"""
Card 2: Repo Auth & Discovery Logic

Two-pass strategy:
  Pass 1 — exact filename matching against TARGET_PATTERNS (fast, zero extra downloads)
  Pass 2 — content sniffing: any .yaml/.yml/.json file under SIZE_LIMIT bytes is
            downloaded and checked for OpenAPI/Swagger/Postman fingerprints,
            catching any non-standard filename a real repo might use.
"""
import fnmatch
import re
from dataclasses import dataclass

import httpx

# Pass 1 — well-known exact / glob filenames
TARGET_PATTERNS = [
    "swagger.json",
    "openapi.json",
    "openapi.yaml",
    "openapi.yml",
    "swagger.yaml",
    "swagger.yml",
    "*.postman_collection.json",
    "*.postman_collection.yaml",
]

# Pass 2 — content-sniff any of these extensions if under SIZE_LIMIT
SNIFF_EXTENSIONS = {".yaml", ".yml", ".json"}
SIZE_LIMIT = 200_000  # 200 KB — skip giant files (generated clients, lock-files, etc.)

# Fingerprints that unambiguously identify a supported spec format
_OPENAPI_FINGERPRINTS = (
    b'"openapi"',   b"'openapi'",   b"openapi:",
    b'"swagger"',   b"'swagger'",   b"swagger:",
)
_POSTMAN_FINGERPRINT = b"_postman_id"

GITHUB_API = "https://api.github.com"
GITLAB_API = "https://gitlab.com/api/v4"

# Expose SourceFile for use by the inference module
from app.inference import SourceFile, select_source_files  # noqa: E402 (circular-safe: inference doesn't import discovery)


@dataclass
class DiscoveredFile:
    path: str
    content: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _detect_provider(repo_url: str) -> str:
    if "github.com" in repo_url:
        return "github"
    if "gitlab.com" in repo_url:
        return "gitlab"
    raise ValueError(f"Unsupported git host in URL: {repo_url}")


def _parse_github_url(repo_url: str) -> tuple[str, str]:
    match = re.search(r"github\.com/([^/]+)/([^/?.]+)", repo_url)
    if not match:
        raise ValueError(f"Cannot parse GitHub URL: {repo_url}")
    return match.group(1), match.group(2).removesuffix(".git")


def _parse_gitlab_url(repo_url: str) -> str:
    match = re.search(r"gitlab\.com/(.+?)(?:\.git)?$", repo_url)
    if not match:
        raise ValueError(f"Cannot parse GitLab URL: {repo_url}")
    return match.group(1).replace("/", "%2F")


def _matches_target(path: str) -> bool:
    """Pass 1: exact / glob filename match."""
    name = path.split("/")[-1]
    return any(fnmatch.fnmatch(name, pat) for pat in TARGET_PATTERNS)


def _is_sniff_candidate(path: str, size: int) -> bool:
    """Pass 2: is this a small YAML/JSON file worth content-sniffing?"""
    ext = "." + path.rsplit(".", 1)[-1].lower() if "." in path else ""
    return ext in SNIFF_EXTENSIONS and size <= SIZE_LIMIT


def _is_api_spec(content: bytes) -> bool:
    """Return True if the first 512 bytes contain a known spec fingerprint."""
    head = content[:512].lower()
    return (
        any(fp in head for fp in _OPENAPI_FINGERPRINTS)
        or _POSTMAN_FINGERPRINT in head
    )


# ---------------------------------------------------------------------------
# GitHub
# ---------------------------------------------------------------------------

async def _github_discover(
    client: httpx.AsyncClient, owner: str, repo: str
) -> list[DiscoveredFile]:
    # Resolve default branch
    repo_resp = await client.get(f"{GITHUB_API}/repos/{owner}/{repo}")
    repo_resp.raise_for_status()
    default_branch = repo_resp.json()["default_branch"]

    # Full recursive tree (includes file sizes)
    tree_resp = await client.get(
        f"{GITHUB_API}/repos/{owner}/{repo}/git/trees/{default_branch}",
        params={"recursive": "1"},
    )
    tree_resp.raise_for_status()
    tree = tree_resp.json().get("tree", [])

    matched_paths: set[str] = set()
    results: list[DiscoveredFile] = []

    def raw_url(path: str) -> str:
        return f"https://raw.githubusercontent.com/{owner}/{repo}/{default_branch}/{path}"

    # Pass 1 — exact name match
    for node in tree:
        if node["type"] == "blob" and _matches_target(node["path"]):
            matched_paths.add(node["path"])
            resp = await client.get(raw_url(node["path"]))
            resp.raise_for_status()
            results.append(DiscoveredFile(path=node["path"], content=resp.text))

    # Pass 2 — content sniff remaining YAML/JSON files
    for node in tree:
        path = node["path"]
        if node["type"] != "blob" or path in matched_paths:
            continue
        size = node.get("size", SIZE_LIMIT + 1)
        if not _is_sniff_candidate(path, size):
            continue

        resp = await client.get(raw_url(path))
        if resp.status_code != 200:
            continue
        raw = resp.content
        if _is_api_spec(raw):
            matched_paths.add(path)
            results.append(DiscoveredFile(path=path, content=raw.decode("utf-8", errors="replace")))

    return results


# ---------------------------------------------------------------------------
# GitLab
# ---------------------------------------------------------------------------

async def _gitlab_discover(
    client: httpx.AsyncClient, project_path: str
) -> list[DiscoveredFile]:
    # Resolve default branch
    project_resp = await client.get(f"{GITLAB_API}/projects/{project_path}")
    project_resp.raise_for_status()
    default_branch = project_resp.json()["default_branch"]

    # Walk tree (paginated)
    all_nodes: list[dict] = []
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
        all_nodes.extend(items)
        if len(items) < 100:
            break
        page += 1

    matched_paths: set[str] = set()
    results: list[DiscoveredFile] = []

    def fetch_raw(path: str):
        encoded = path.replace("/", "%2F")
        return client.get(
            f"{GITLAB_API}/projects/{project_path}/repository/files/{encoded}/raw",
            params={"ref": default_branch},
        )

    # Pass 1 — exact name match
    for item in all_nodes:
        if item["type"] == "blob" and _matches_target(item["path"]):
            matched_paths.add(item["path"])
            resp = await fetch_raw(item["path"])
            resp.raise_for_status()
            results.append(DiscoveredFile(path=item["path"], content=resp.text))

    # Pass 2 — content sniff (GitLab tree doesn't return size, so sniff all small-ext files)
    for item in all_nodes:
        path = item["path"]
        if item["type"] != "blob" or path in matched_paths:
            continue
        if not _is_sniff_candidate(path, SIZE_LIMIT):  # size unknown, allow all
            continue

        resp = await fetch_raw(path)
        if resp.status_code != 200:
            continue
        raw = resp.content
        if len(raw) > SIZE_LIMIT:
            continue
        if _is_api_spec(raw):
            matched_paths.add(path)
            results.append(DiscoveredFile(path=path, content=raw.decode("utf-8", errors="replace")))

    return results


# ---------------------------------------------------------------------------
# Source-file collection (Pass 3 support)
# ---------------------------------------------------------------------------

async def _github_collect_sources(
    client: httpx.AsyncClient, owner: str, repo: str, default_branch: str, tree: list[dict]
) -> list[SourceFile]:
    paths = select_source_files(tree)
    sources: list[SourceFile] = []
    for path in paths:
        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{default_branch}/{path}"
        resp = await client.get(raw_url)
        if resp.status_code == 200:
            sources.append(SourceFile(path=path, content=resp.text))
    return sources


async def _gitlab_collect_sources(
    client: httpx.AsyncClient, project_path: str, default_branch: str, all_nodes: list[dict]
) -> list[SourceFile]:
    paths = select_source_files(all_nodes)
    sources: list[SourceFile] = []
    for path in paths:
        encoded = path.replace("/", "%2F")
        resp = await client.get(
            f"{GITLAB_API}/projects/{project_path}/repository/files/{encoded}/raw",
            params={"ref": default_branch},
        )
        if resp.status_code == 200:
            sources.append(SourceFile(path=path, content=resp.text))
    return sources


# ---------------------------------------------------------------------------
# Public entry points
# ---------------------------------------------------------------------------

async def discover_api_files(repo_url: str, token: str) -> list[DiscoveredFile]:
    provider = _detect_provider(repo_url)

    headers = {"Accept": "application/json"}
    if provider == "github":
        headers["Authorization"] = f"Bearer {token}"
    else:
        headers["PRIVATE-TOKEN"] = token

    async with httpx.AsyncClient(headers=headers, timeout=60.0) as client:
        if provider == "github":
            owner, repo = _parse_github_url(repo_url)
            return await _github_discover(client, owner, repo)
        else:
            project_path = _parse_gitlab_url(repo_url)
            return await _gitlab_discover(client, project_path)


async def collect_source_files(repo_url: str, token: str) -> list[SourceFile]:
    """
    Pass 3: collect ranked source code files for AI inference.
    Called by the scan router when Pass 1+2 yield no spec files.
    """
    provider = _detect_provider(repo_url)

    headers = {"Accept": "application/json"}
    if provider == "github":
        headers["Authorization"] = f"Bearer {token}"
    else:
        headers["PRIVATE-TOKEN"] = token

    async with httpx.AsyncClient(headers=headers, timeout=60.0) as client:
        if provider == "github":
            owner, repo = _parse_github_url(repo_url)
            repo_resp = await client.get(f"{GITHUB_API}/repos/{owner}/{repo}")
            repo_resp.raise_for_status()
            default_branch = repo_resp.json()["default_branch"]
            tree_resp = await client.get(
                f"{GITHUB_API}/repos/{owner}/{repo}/git/trees/{default_branch}",
                params={"recursive": "1"},
            )
            tree_resp.raise_for_status()
            tree = tree_resp.json().get("tree", [])
            return await _github_collect_sources(client, owner, repo, default_branch, tree)
        else:
            project_path = _parse_gitlab_url(repo_url)
            project_resp = await client.get(f"{GITLAB_API}/projects/{project_path}")
            project_resp.raise_for_status()
            default_branch = project_resp.json()["default_branch"]
            all_nodes: list[dict] = []
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
                all_nodes.extend(items)
                if len(items) < 100:
                    break
                page += 1
            return await _gitlab_collect_sources(client, project_path, default_branch, all_nodes)
