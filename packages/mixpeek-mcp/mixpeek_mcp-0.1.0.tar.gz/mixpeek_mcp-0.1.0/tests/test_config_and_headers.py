import os
import importlib


def test_auth_headers_with_key_and_namespace(monkeypatch):
    monkeypatch.setenv("MIXPEEK_API_KEY", "sk_test")
    monkeypatch.setenv("MIXPEEK_NAMESPACE", "ns-test")
    monkeypatch.setenv("MIXPEEK_API_BASE", "https://api.mixpeek.com")

    import server  # import module under test
    importlib.reload(server)

    headers = server.auth_headers()
    assert headers.get("Authorization") == "Bearer sk_test"
    assert headers.get("X-Namespace") == "ns-test"


def test_openapi_url_default(monkeypatch):
    monkeypatch.delenv("MIXPEEK_OPENAPI_URL", raising=False)
    monkeypatch.setenv("MIXPEEK_API_BASE", "https://api.mixpeek.com")

    import server
    importlib.reload(server)

    assert server.OPENAPI_URL == "https://api.mixpeek.com/openapi.json"

