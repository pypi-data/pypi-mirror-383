import os
import importlib
import pytest


@pytest.mark.asyncio
async def test_live_healthcheck_if_env_present(monkeypatch):
    api_key = os.getenv("LIVE_MIXPEEK_API_KEY")
    spec_url = os.getenv("LIVE_MIXPEEK_OPENAPI_URL")
    api_base = os.getenv("LIVE_MIXPEEK_API_BASE")

    if not api_key or not spec_url or not api_base:
        pytest.skip("live env not provided")

    monkeypatch.setenv("MIXPEEK_API_KEY", api_key)
    monkeypatch.setenv("MIXPEEK_API_BASE", api_base)
    monkeypatch.setenv("MIXPEEK_OPENAPI_URL", spec_url)

    import server
    importlib.reload(server)

    spec = await server.fetch_openapi()
    endpoints = server.extract_endpoints(spec)
    ops = {e.operation_id: e for e in endpoints}

    # health tool exists
    # If operationId is e.g. "healthcheck_v1_health_get"
    # Exercise tool and expect 200/ok output
    for oid, ep in ops.items():
        if "health" in oid:
            tool = server.create_tool(ep)
            out = await tool()
            assert isinstance(out, dict)
            break
    else:
        pytest.skip("no health operation found in spec")


