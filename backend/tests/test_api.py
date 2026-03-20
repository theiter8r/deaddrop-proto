"""
Tests for the scanner API endpoints (Card 4) — mocks the discovery layer
so no real GitHub/GitLab calls are made.
"""
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.discovery import DiscoveredFile

FIXTURES = Path(__file__).parent / "fixtures"


def _fixture_files() -> list[DiscoveredFile]:
    return [
        DiscoveredFile(path=name, content=(FIXTURES / name).read_text())
        for name in [
            "openapi.json",
            "openapi.yaml",
            "myservice.postman_collection.json",
        ]
    ]


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# POST /scan
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_scan_returns_endpoints(client: AsyncClient):
    with patch(
        "app.routers.scan.discover_api_files",
        new=AsyncMock(return_value=_fixture_files()),
    ):
        resp = await client.post(
            "/scan",
            json={"repo_url": "https://github.com/example/repo", "token": "fake-token"},
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["endpoints_discovered"] == 12
    assert len(data["endpoints"]) == 12


@pytest.mark.asyncio
async def test_scan_persists_to_db(client: AsyncClient):
    with patch(
        "app.routers.scan.discover_api_files",
        new=AsyncMock(return_value=_fixture_files()),
    ):
        await client.post(
            "/scan",
            json={"repo_url": "https://github.com/example/repo", "token": "fake-token"},
        )

    resp = await client.get("/endpoints")
    assert resp.status_code == 200
    assert len(resp.json()) == 12


@pytest.mark.asyncio
async def test_scan_endpoint_schema(client: AsyncClient):
    with patch(
        "app.routers.scan.discover_api_files",
        new=AsyncMock(return_value=_fixture_files()),
    ):
        resp = await client.post(
            "/scan",
            json={"repo_url": "https://github.com/example/repo", "token": "fake-token"},
        )

    endpoint = resp.json()["endpoints"][0]
    assert "id" in endpoint
    assert "endpoint_path" in endpoint
    assert "http_method" in endpoint
    assert "source_file" in endpoint
    assert "is_deprecated" in endpoint


@pytest.mark.asyncio
async def test_scan_deprecated_flag_persisted(client: AsyncClient):
    with patch(
        "app.routers.scan.discover_api_files",
        new=AsyncMock(return_value=_fixture_files()),
    ):
        resp = await client.post(
            "/scan",
            json={"repo_url": "https://github.com/example/repo", "token": "fake-token"},
        )

    endpoints = resp.json()["endpoints"]
    deprecated = [e for e in endpoints if e["is_deprecated"]]
    assert len(deprecated) > 0


@pytest.mark.asyncio
async def test_scan_invalid_url_returns_422(client: AsyncClient):
    with patch(
        "app.routers.scan.discover_api_files",
        new=AsyncMock(side_effect=ValueError("Unsupported git host")),
    ):
        resp = await client.post(
            "/scan",
            json={"repo_url": "https://bitbucket.org/foo/bar", "token": "tok"},
        )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_scan_network_error_returns_502(client: AsyncClient):
    with patch(
        "app.routers.scan.discover_api_files",
        new=AsyncMock(side_effect=Exception("Connection timeout")),
    ):
        resp = await client.post(
            "/scan",
            json={"repo_url": "https://github.com/example/repo", "token": "tok"},
        )
    assert resp.status_code == 502


@pytest.mark.asyncio
async def test_scan_empty_repo_returns_zero(client: AsyncClient):
    with patch(
        "app.routers.scan.discover_api_files",
        new=AsyncMock(return_value=[]),
    ):
        resp = await client.post(
            "/scan",
            json={"repo_url": "https://github.com/example/empty", "token": "tok"},
        )
    assert resp.status_code == 200
    assert resp.json()["endpoints_discovered"] == 0


# ---------------------------------------------------------------------------
# GET /endpoints
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_endpoints_empty_initially(client: AsyncClient):
    resp = await client.get("/endpoints")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_list_endpoints_after_two_scans(client: AsyncClient):
    """Second scan of same files should not duplicate rows."""
    with patch(
        "app.routers.scan.discover_api_files",
        new=AsyncMock(return_value=_fixture_files()),
    ):
        await client.post(
            "/scan",
            json={"repo_url": "https://github.com/example/repo", "token": "tok"},
        )
        await client.post(
            "/scan",
            json={"repo_url": "https://github.com/example/repo", "token": "tok"},
        )

    resp = await client.get("/endpoints")
    assert len(resp.json()) == 12
