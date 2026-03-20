"""
Pass 3: AI-Powered Endpoint Inference via Gemini

When no API spec files are found in a repository, this module sends source
code files to Gemini (gemini-2.0-flash) and asks it to infer API endpoints
from framework-specific route definitions (FastAPI, Flask, Express, Django,
Spring, Gin, Rails, etc.).
"""
import json
import logging
import os
from dataclasses import dataclass

import google.generativeai as genai

from app.schemas import EndpointCreate, HttpMethod

logger = logging.getLogger(__name__)

# Source file extensions worth analysing
SOURCE_EXTENSIONS = {
    ".py", ".js", ".mjs", ".cjs",
    ".ts", ".tsx",
    ".java", ".kt",
    ".go",
    ".rb",
    ".php",
    ".cs",
}

# Filename fragments that strongly suggest route/handler code — ranked first
_ROUTE_KEYWORDS = (
    "route", "router", "routes",
    "url", "urls",
    "endpoint", "endpoints",
    "controller", "controllers",
    "handler", "handlers",
    "api", "view", "views",
    "app", "main", "server", "index",
)

MAX_FILES = 15
MAX_BYTES_PER_FILE = 24_000
MAX_TOTAL_BYTES = 150_000


@dataclass
class SourceFile:
    path: str
    content: str


def _route_priority(path: str) -> int:
    # Check both the full path and the filename so that files inside a
    # `routes/` or `controllers/` directory rank highly even if their
    # individual filename (e.g. `admin.ts`) contains no keyword.
    full = path.lower()
    name = full.split("/")[-1].replace(".", "_")
    for rank, kw in enumerate(_ROUTE_KEYWORDS):
        if kw in name or kw in full:
            return rank
    return len(_ROUTE_KEYWORDS)


def _is_source_file(path: str, size: int) -> bool:
    ext = "." + path.rsplit(".", 1)[-1].lower() if "." in path else ""
    skip_fragments = ("test", "spec", "migration", "generated", "vendor", "node_modules", "__pycache__")
    low = path.lower()
    if any(frag in low for frag in skip_fragments):
        return False
    return ext in SOURCE_EXTENSIONS and size <= MAX_BYTES_PER_FILE


def select_source_files(tree_nodes: list[dict]) -> list[str]:
    """Return a ranked list of source file paths for inference."""
    candidates = [
        node["path"]
        for node in tree_nodes
        if node.get("type") == "blob"
        and _is_source_file(node["path"], node.get("size", MAX_BYTES_PER_FILE))
    ]
    candidates.sort(key=_route_priority)
    return candidates[:MAX_FILES]


def _build_prompt(files: list[SourceFile]) -> str:
    sections = []
    total = 0
    for f in files:
        chunk = f.content[:MAX_BYTES_PER_FILE]
        total += len(chunk)
        sections.append(f"### {f.path}\n```\n{chunk}\n```")
        if total >= MAX_TOTAL_BYTES:
            break

    code_block = "\n\n".join(sections)

    return f"""You are an expert at reading web framework source code.

Analyse the source files below and extract every API endpoint definition you can find.
Look for Flask/FastAPI/Django/Express/Spring/Gin/Rails/Laravel route decorators and router registrations.

Return a JSON array — and ONLY the JSON array, no explanation — where each object has:
  "endpoint_path"  : URL path string, e.g. "/users/{{id}}"
  "http_method"    : one of GET POST PUT PATCH DELETE HEAD OPTIONS
  "source_file"    : the file path listed in the header above
  "is_deprecated"  : boolean — true only if the code explicitly marks it deprecated

If no endpoints are found, return an empty array: []

---
{code_block}"""


def _parse_response(text: str) -> list[EndpointCreate]:
    text = text.strip()
    # Strip markdown fences if Gemini wraps the output
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    try:
        raw: list[dict] = json.loads(text)
    except json.JSONDecodeError as exc:
        logger.warning("Gemini returned non-JSON inference output: %s", exc)
        return []

    endpoints: list[EndpointCreate] = []
    valid_methods = {m.value for m in HttpMethod}

    for item in raw:
        try:
            method = str(item.get("http_method", "")).upper()
            if method not in valid_methods:
                continue
            endpoints.append(
                EndpointCreate(
                    endpoint_path=str(item["endpoint_path"]),
                    http_method=HttpMethod(method),
                    source_file=str(item.get("source_file", "inferred")),
                    is_deprecated=bool(item.get("is_deprecated", False)),
                )
            )
        except (KeyError, ValueError):
            continue

    return endpoints


async def infer_endpoints(source_files: list[SourceFile]) -> list[EndpointCreate]:
    """
    Call Gemini to infer endpoints from source code.
    Returns empty list if GEMINI_API_KEY is not set or nothing is found.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY not set — skipping AI inference pass")
        return []

    if not source_files:
        return []

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=(
            "You are an API security analyst. Extract API endpoint definitions "
            "from source code with 100% accuracy. Always respond with valid JSON only — "
            "no markdown, no explanation, just the JSON array."
        ),
    )

    prompt = _build_prompt(source_files)
    logger.info("Running Gemini inference on %d source files", len(source_files))

    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            temperature=0,
            response_mime_type="application/json",
        ),
    )

    text = response.text or ""
    endpoints = _parse_response(text)
    logger.info("Gemini inference found %d endpoints", len(endpoints))
    return endpoints
