"""Tests for the file parsing engine (Card 3) — no DB, no network needed."""
import json
from pathlib import Path

import pytest

from app.discovery import DiscoveredFile
from app.parser import parse_all, parse_file

FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(filename: str) -> DiscoveredFile:
    content = (FIXTURES / filename).read_text()
    return DiscoveredFile(path=filename, content=content)


# ---------------------------------------------------------------------------
# OpenAPI JSON
# ---------------------------------------------------------------------------

class TestOpenAPIJson:
    def test_endpoint_count(self):
        result = parse_file(load_fixture("openapi.json"))
        assert len(result) == 5  # GET+POST /users, GET+DELETE /users/{id}, GET /legacy/report

    def test_methods_present(self):
        result = parse_file(load_fixture("openapi.json"))
        methods = {ep.http_method.value for ep in result}
        assert methods == {"GET", "POST", "DELETE"}

    def test_deprecated_flagged(self):
        result = parse_file(load_fixture("openapi.json"))
        deprecated = [ep for ep in result if ep.is_deprecated]
        paths = {ep.endpoint_path for ep in deprecated}
        assert "/users/{id}" in paths          # DELETE /users/{id}
        assert "/legacy/report" in paths

    def test_non_deprecated_not_flagged(self):
        result = parse_file(load_fixture("openapi.json"))
        active = [ep for ep in result if not ep.is_deprecated]
        paths = {ep.endpoint_path for ep in active}
        assert "/users" in paths

    def test_source_file_preserved(self):
        result = parse_file(load_fixture("openapi.json"))
        assert all(ep.source_file == "openapi.json" for ep in result)


# ---------------------------------------------------------------------------
# OpenAPI YAML
# ---------------------------------------------------------------------------

class TestOpenAPIYaml:
    def test_endpoint_count(self):
        result = parse_file(load_fixture("openapi.yaml"))
        assert len(result) == 4  # GET+POST /products, GET+PUT /products/{sku}

    def test_deprecated_post_products(self):
        result = parse_file(load_fixture("openapi.yaml"))
        target = next(
            ep for ep in result
            if ep.endpoint_path == "/products" and ep.http_method.value == "POST"
        )
        assert target.is_deprecated is True

    def test_non_deprecated_get_products(self):
        result = parse_file(load_fixture("openapi.yaml"))
        target = next(
            ep for ep in result
            if ep.endpoint_path == "/products" and ep.http_method.value == "GET"
        )
        assert target.is_deprecated is False


# ---------------------------------------------------------------------------
# Postman Collection
# ---------------------------------------------------------------------------

class TestPostman:
    def test_endpoint_count(self):
        result = parse_file(load_fixture("myservice.postman_collection.json"))
        assert len(result) == 3  # POST /auth/login, DELETE /auth/session, GET /orders

    def test_nested_folder_items_parsed(self):
        result = parse_file(load_fixture("myservice.postman_collection.json"))
        paths = {ep.endpoint_path for ep in result}
        assert "/auth/login" in paths
        assert "/auth/session" in paths

    def test_top_level_item_parsed(self):
        result = parse_file(load_fixture("myservice.postman_collection.json"))
        paths = {ep.endpoint_path for ep in result}
        assert "/orders" in paths

    def test_no_deprecated_in_postman(self):
        result = parse_file(load_fixture("myservice.postman_collection.json"))
        assert all(ep.is_deprecated is False for ep in result)


# ---------------------------------------------------------------------------
# parse_all deduplication
# ---------------------------------------------------------------------------

class TestParseAll:
    def test_deduplication(self):
        """Feeding the same file twice should not produce duplicates."""
        f = load_fixture("openapi.json")
        result = parse_all([f, f])
        assert len(result) == 5

    def test_combines_multiple_files(self):
        files = [
            load_fixture("openapi.json"),
            load_fixture("openapi.yaml"),
            load_fixture("myservice.postman_collection.json"),
        ]
        result = parse_all(files)
        assert len(result) == 12  # 5 + 4 + 3


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_empty_paths(self):
        f = DiscoveredFile(
            path="empty.json",
            content=json.dumps({"openapi": "3.0.0", "info": {}, "paths": {}}),
        )
        assert parse_file(f) == []

    def test_invalid_content_returns_empty(self):
        f = DiscoveredFile(path="bad.json", content="not json or yaml <<<")
        assert parse_file(f) == []

    def test_unknown_format_returns_empty(self):
        f = DiscoveredFile(path="random.json", content=json.dumps({"foo": "bar"}))
        assert parse_file(f) == []
