"""
Card 3: File Parsing Engine

Parses discovered API spec files (OpenAPI/Swagger JSON+YAML, Postman Collections)
and normalizes every endpoint into the unified EndpointCreate schema.
"""
import json
import re

import yaml

from app.discovery import DiscoveredFile
from app.schemas import EndpointCreate, HttpMethod

# Valid HTTP methods we'll accept from any spec
_VALID_METHODS = {m.value for m in HttpMethod}

# OpenAPI/Swagger path-level keys that are NOT HTTP methods
_OPENAPI_NON_METHOD_KEYS = {
    "summary", "description", "servers", "parameters", "x-", "$ref"
}


# ---------------------------------------------------------------------------
# Format detection
# ---------------------------------------------------------------------------

def _is_postman(data: dict) -> bool:
    """Postman collections always have an 'info' block with a '_postman_id'."""
    return isinstance(data.get("info"), dict) and "_postman_id" in data["info"]


def _is_openapi(data: dict) -> bool:
    return "openapi" in data or "swagger" in data


# ---------------------------------------------------------------------------
# OpenAPI / Swagger parser
# ---------------------------------------------------------------------------

def _parse_openapi(data: dict, source_file: str) -> list[EndpointCreate]:
    endpoints: list[EndpointCreate] = []
    paths: dict = data.get("paths", {})

    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue

        # Path-level deprecated flag (applies to all methods if set)
        path_deprecated = bool(path_item.get("deprecated", False))

        for method, operation in path_item.items():
            upper = method.upper()
            if upper not in _VALID_METHODS:
                continue
            if not isinstance(operation, dict):
                continue

            # Operation-level deprecated overrides path-level
            is_deprecated = bool(operation.get("deprecated", path_deprecated))

            endpoints.append(
                EndpointCreate(
                    endpoint_path=path,
                    http_method=HttpMethod(upper),
                    source_file=source_file,
                    is_deprecated=is_deprecated,
                )
            )

    return endpoints


# ---------------------------------------------------------------------------
# Postman Collection parser
# ---------------------------------------------------------------------------

def _extract_postman_path(request: dict) -> str | None:
    """
    Postman stores URLs as either a raw string or a structured object.
    Returns a normalized path string like /users/{id}, or None if unparseable.
    """
    url = request.get("url")
    if not url:
        return None

    raw: str | None = None
    if isinstance(url, str):
        raw = url
    elif isinstance(url, dict):
        # Prefer the structured path segments list
        segments = url.get("path")
        if isinstance(segments, list):
            # Segments may be strings or dicts with a 'value' key
            parts = []
            for seg in segments:
                if isinstance(seg, str):
                    parts.append(seg)
                elif isinstance(seg, dict):
                    parts.append(seg.get("value", ""))
            return "/" + "/".join(parts)
        raw = url.get("raw")

    if not raw:
        return None

    # Strip protocol + host, keep only the path portion
    match = re.search(r"(?:https?://[^/]+)(/[^?#]*)", raw)
    if match:
        return match.group(1) or "/"
    # Bare path (no host)
    if raw.startswith("/"):
        return raw.split("?")[0]
    return None


def _walk_postman_items(
    items: list, source_file: str, endpoints: list[EndpointCreate]
) -> None:
    """Recursively walk Postman folders and leaf request items."""
    for item in items:
        if not isinstance(item, dict):
            continue

        # Folder — recurse
        if "item" in item:
            _walk_postman_items(item["item"], source_file, endpoints)
            continue

        # Leaf request
        request = item.get("request")
        if not isinstance(request, dict):
            continue

        method = (request.get("method") or "").upper()
        if method not in _VALID_METHODS:
            continue

        path = _extract_postman_path(request)
        if not path:
            continue

        endpoints.append(
            EndpointCreate(
                endpoint_path=path,
                http_method=HttpMethod(method),
                source_file=source_file,
                is_deprecated=False,  # Postman has no deprecation concept
            )
        )


def _parse_postman(data: dict, source_file: str) -> list[EndpointCreate]:
    endpoints: list[EndpointCreate] = []
    _walk_postman_items(data.get("item", []), source_file, endpoints)
    return endpoints


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def parse_file(discovered: DiscoveredFile) -> list[EndpointCreate]:
    """
    Parse a single DiscoveredFile into a list of normalized EndpointCreate objects.
    Returns an empty list if the file cannot be parsed or contains no endpoints.
    """
    content = discovered.content.strip()
    source = discovered.path

    # Deserialize
    data: dict | None = None
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError:
            return []

    if not isinstance(data, dict):
        return []

    if _is_postman(data):
        return _parse_postman(data, source)
    if _is_openapi(data):
        return _parse_openapi(data, source)

    return []


def parse_all(discovered_files: list[DiscoveredFile]) -> list[EndpointCreate]:
    """Parse every discovered file and return a flat, deduplicated endpoint list."""
    seen: set[tuple] = set()
    results: list[EndpointCreate] = []

    for f in discovered_files:
        for ep in parse_file(f):
            key = (ep.endpoint_path, ep.http_method, ep.source_file)
            if key not in seen:
                seen.add(key)
                results.append(ep)

    return results
