import importlib


class _Resp:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload or {"ok": True}
        self.text = text

    def json(self):
        return self._payload

    def raise_for_status(self):
        return None


class _Client:
    last = None

    def __init__(self, timeout):
        self.timeout = timeout

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def request(self, method, url, params=None, json=None, headers=None):
        _Client.last = {
            "method": method,
            "url": url,
            "params": params,
            "json": json,
            "headers": headers,
        }
        return _Resp(payload={"ok": True, "echo": _Client.last})


import pytest


@pytest.mark.asyncio
async def test_use_cases_ingest_define_retrieve(monkeypatch):
    # Arrange
    monkeypatch.setenv("MIXPEEK_API_KEY", "sk_test")
    monkeypatch.setenv("MIXPEEK_NAMESPACE", "ns-test")
    monkeypatch.setenv("MIXPEEK_API_BASE", "https://api.mixpeek.com")

    import server
    importlib.reload(server)

    # mock httpx AsyncClient
    monkeypatch.setattr(server.httpx, "AsyncClient", _Client)

    # Build a synthetic spec covering common Mixpeek flows
    # - Ingest: POST /v1/objects
    # - Define Collection: POST /v1/collections
    # - Execute Retriever: POST /v1/retrievers/{retriever_id}/execute
    # - Health: GET /v1/health
    spec = {
        "paths": {
            "/v1/objects": {
                "post": {
                    "operationId": "objects_create",
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"type": "object"}}},
                    },
                }
            },
            "/v1/collections": {
                "post": {
                    "operationId": "collections_create",
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"type": "object"}}},
                    },
                }
            },
            "/v1/retrievers/{retriever_id}/execute": {
                "post": {
                    "operationId": "retrievers_execute",
                    "parameters": [
                        {"name": "retriever_id", "in": "path", "required": True},
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"type": "object"}}},
                    },
                }
            },
            "/v1/health": {
                "get": {
                    "operationId": "healthcheck_v1_health_get",
                    "parameters": [
                        {"name": "deep", "in": "query", "required": False},
                    ],
                }
            },
        }
    }

    endpoints = server.extract_endpoints(spec)
    ops = {e.operation_id: e for e in endpoints}

    # Ingest object
    ingest_tool = server.create_tool(ops["objects_create"])
    out = await ingest_tool(body={"url": "https://example.com/file.pdf", "bucket_id": "bkt1"})
    assert out["ok"] is True
    assert _Client.last["method"] == "POST"
    assert _Client.last["url"].endswith("/v1/objects")

    # Create collection
    coll_tool = server.create_tool(ops["collections_create"])
    out = await coll_tool(body={"name": "docs", "description": "Test", "feature_extractors": []})
    assert out["ok"] is True
    assert _Client.last["method"] == "POST"
    assert _Client.last["url"].endswith("/v1/collections")

    # Execute retriever
    ret_tool = server.create_tool(ops["retrievers_execute"])
    out = await ret_tool(retriever_id="ret1", body={"query": "warehouse safety", "return_urls": True})
    assert out["ok"] is True
    assert _Client.last["method"] == "POST"
    assert _Client.last["url"].endswith("/v1/retrievers/ret1/execute")

    # Healthcheck
    health_tool = server.create_tool(ops["healthcheck_v1_health_get"])
    out = await health_tool(deep=True)
    assert out["ok"] is True
    assert _Client.last["method"] == "GET"
    assert _Client.last["params"] == {"deep": True}
    assert _Client.last["headers"]["Authorization"].startswith("Bearer ")
    assert _Client.last["headers"]["X-Namespace"] == "ns-test"


