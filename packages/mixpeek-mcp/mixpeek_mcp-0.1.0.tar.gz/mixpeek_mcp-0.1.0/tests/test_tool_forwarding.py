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
async def test_tool_forwarding_builds_request(monkeypatch):
    monkeypatch.setenv("MIXPEEK_API_KEY", "sk_test")
    monkeypatch.setenv("MIXPEEK_NAMESPACE", "ns1")
    monkeypatch.setenv("MIXPEEK_API_BASE", "https://example.com")

    import server
    importlib.reload(server)

    # mock httpx AsyncClient
    monkeypatch.setattr(server.httpx, "AsyncClient", _Client)

    ep = server.Endpoint(
        operation_id="update_item",
        method="POST",
        path="/v1/items/{item_id}",
        query_args=[server.ToolArg(name="verbose", required=False, location="query")],
        path_args=[server.ToolArg(name="item_id", required=True, location="path")],
        wants_body=True,
    )

    tool = server.create_tool(ep)

    out = await tool(item_id=123, verbose=True, body={"name": "abc"})
    assert out["ok"] is True

    assert _Client.last["method"] == "POST"
    assert _Client.last["url"] == "https://example.com/v1/items/123"
    assert _Client.last["params"] == {"verbose": True}
    assert _Client.last["json"] == {"name": "abc"}
    assert _Client.last["headers"]["Authorization"] == "Bearer sk_test"
    assert _Client.last["headers"]["X-Namespace"] == "ns1"

