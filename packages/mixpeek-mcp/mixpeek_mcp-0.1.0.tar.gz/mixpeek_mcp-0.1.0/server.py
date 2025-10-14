import os
import re
import json
import time
import asyncio
from typing import Any, Dict, List, Optional

try:
    import httpx  # type: ignore[import]
except ImportError:  # pragma: no cover - dev env lint workaround
    httpx = None  # type: ignore[assignment]

try:
    from pydantic import BaseModel  # type: ignore[import]
except ImportError:  # pragma: no cover - dev env lint workaround
    class BaseModel:  # type: ignore[no-redef]
        pass

try:
    from dotenv import load_dotenv  # type: ignore[import]
    load_dotenv()
except ImportError:
    pass

try:
    from mcp.server import Server  # type: ignore[import]
    from mcp.server.stdio import stdio_server  # type: ignore[import]
except ImportError:  # pragma: no cover - dev env lint workaround
    # Minimal fallback so the module remains importable in test/dev
    class _DummyServer:
        def __init__(self, name: str) -> None:
            self.name = name
            self._tools = {}

        def tool(self, name: str, desc: str = ""):
            def decorator(fn):
                self._tools[name] = {"fn": fn, "desc": desc}
                return fn
            return decorator

    class _DummyStdIO:
        def __init__(self, _server: Any) -> None:
            self._server = _server

        async def __aenter__(self):
            return self._server

        async def __aexit__(self, exc_type, exc, tb):
            return False

    def stdio_server(s: Any) -> Any:  # type: ignore[override]
        return _DummyStdIO(s)

    Server = _DummyServer  # type: ignore[assignment]


# ----------------------------
# Config
# ----------------------------
MCP_NAME = "mixpeek"

API_BASE = os.getenv("MIXPEEK_API_BASE", "https://api.mixpeek.com").rstrip("/")
OPENAPI_URL = os.getenv("MIXPEEK_OPENAPI_URL") or f"{API_BASE}/openapi.json"

# Allowlist regex against "METHOD /path"
ALLOWLIST = [
    r"(GET|POST) /v1/.*",
]

# Simple per-process token bucket rate limit
MAX_CALLS = int(os.getenv("MCP_RATE_MAX_CALLS", "20"))
PER_SECONDS = float(os.getenv("MCP_RATE_PER_SECONDS", "10"))

# Timeouts
CONNECT_TIMEOUT = float(os.getenv("MCP_CONNECT_TIMEOUT", "5"))
READ_TIMEOUT = float(os.getenv("MCP_READ_TIMEOUT", "30"))

# Headers
API_KEY = os.getenv("MIXPEEK_API_KEY")
NAMESPACE = os.getenv("MIXPEEK_NAMESPACE")


def auth_headers() -> Dict[str, str]:
    headers: Dict[str, str] = {}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    if NAMESPACE:
        headers["X-Namespace"] = NAMESPACE
    return headers


# ----------------------------
# Utilities
# ----------------------------
def allowed(method: str, path: str) -> bool:
    target = f"{method.upper()} {path}"
    return any(re.fullmatch(p, target) for p in ALLOWLIST)


def redact(obj: Any) -> Any:
    try:
        data = json.loads(json.dumps(obj))
    except (TypeError, ValueError):
        return "<unserializable>"
    if isinstance(data, dict):
        if "headers" in data:
            data["headers"] = {
                k: ("<redacted>" if k.lower() == "authorization" else v)
                for k, v in data["headers"].items()
            }
        body = data.get("json")
        if isinstance(body, (str, bytes)) and len(str(body)) > 2048:
            data["json"] = "<truncated>"
    return data


class TokenBucket:
    def __init__(self, max_calls: int, per_seconds: float) -> None:
        self.max_calls = max_calls
        self.per = per_seconds
        self.tokens = float(max_calls)
        self.last = time.monotonic()

    def allow(self) -> bool:
        now = time.monotonic()
        elapsed = now - self.last
        self.last = now
        self.tokens = min(self.max_calls, self.tokens + elapsed * (self.max_calls / self.per))
        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True
        return False


bucket = TokenBucket(MAX_CALLS, PER_SECONDS)


# ----------------------------
# OpenAPI parsing
# ----------------------------
class ToolArg(BaseModel):
    name: str
    required: bool = False
    location: str  # "query" | "path" | "body"


class Endpoint(BaseModel):
    operation_id: str
    method: str
    path: str
    query_args: List[ToolArg] = []
    path_args: List[ToolArg] = []
    wants_body: bool = False


async def fetch_openapi() -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=httpx.Timeout(READ_TIMEOUT, connect=CONNECT_TIMEOUT)) as cx:
        try:
            r = await cx.get(OPENAPI_URL, headers=auth_headers())
            r.raise_for_status()
            return r.json()
        except httpx.HTTPError:
            # Fallback to FastAPI docs path if needed
            alt = f"{API_BASE}/docs/openapi.json"
            r = await cx.get(alt, headers=auth_headers())
            r.raise_for_status()
            return r.json()


def extract_endpoints(spec: Dict[str, Any]) -> List[Endpoint]:
    eps: List[Endpoint] = []
    paths = spec.get("paths", {}) or {}
    for path, ops in paths.items():
        for method, op in (ops or {}).items():
            method_upper = method.upper()
            if method_upper not in {"GET", "POST"}:
                continue
            # respect x-mcp-hidden flag
            if op.get("x-mcp-hidden") is True:
                continue
            op_id = op.get("operationId")
            if not op_id:
                continue
            if not allowed(method_upper, path):
                continue

            query_args: List[ToolArg] = []
            path_args: List[ToolArg] = []

            for p in op.get("parameters", []) or []:
                loc = p.get("in")
                if loc == "query":
                    query_args.append(ToolArg(name=p["name"], required=p.get("required", False), location="query"))
                elif loc == "path":
                    path_args.append(ToolArg(name=p["name"], required=True, location="path"))

            wants_body = False
            req_body = op.get("requestBody") or {}
            content = req_body.get("content") or {}
            if any(ct.startswith("application/json") for ct in content.keys()):
                wants_body = True

            eps.append(
                Endpoint(
                    operation_id=op_id,
                    method=method_upper,
                    path=path,
                    query_args=query_args,
                    path_args=path_args,
                    wants_body=wants_body,
                )
            )
    return eps


# ----------------------------
# MCP Server
# ----------------------------
server = Server(MCP_NAME)


def create_tool(endpoint: Endpoint) -> Any:
    name = endpoint.operation_id
    method = endpoint.method
    path_template = endpoint.path
    query_names = [a.name for a in endpoint.query_args]
    path_names = [a.name for a in endpoint.path_args]

    @server.tool(name, desc=f"{method} {path_template} (from OpenAPI)")
    async def tool(**kwargs: Any) -> Any:
        if not bucket.allow():
            return {"error": "rate_limited", "hint": f"Max {MAX_CALLS} calls per {int(PER_SECONDS)}s"}

        # Build query/body
        query: Dict[str, Any] = {}
        body: Optional[Any] = None
        path_values: Dict[str, Any] = {}

        # envelope usage
        if isinstance(kwargs.get("query"), dict):
            query.update(kwargs["query"])  # type: ignore[index]
        if "body" in kwargs:
            body = kwargs["body"]

        # top-level convenience args
        for qn in query_names:
            if qn in kwargs:
                query[qn] = kwargs[qn]
        for pn in path_names:
            if pn in kwargs:
                path_values[pn] = kwargs[pn]

        # required checks
        for a in endpoint.query_args:
            if a.required and a.name not in query:
                return {"error": "missing_param", "param": a.name}
        for pn in path_names:
            if pn not in path_values:
                return {"error": "missing_path_param", "param": pn}
        if endpoint.wants_body and body is None and method == "POST":
            req_body = {"note": "no JSON body provided"}
        else:
            req_body = body if endpoint.wants_body else None

        # materialize path
        url_path = path_template
        for pn, pv in path_values.items():
            url_path = url_path.replace("{" + pn + "}", str(pv))

        url = API_BASE + url_path

        req = {
            "method": method,
            "url": url,
            "params": query or None,
            "json": req_body,
            "headers": auth_headers(),
        }
        print("[mixpeek:mcp] request:", json.dumps(redact(req)))

        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(READ_TIMEOUT, connect=CONNECT_TIMEOUT)) as cx:
                resp = await cx.request(method, url, params=query or None, json=req_body, headers=auth_headers())
                resp.raise_for_status()
            try:
                return resp.json()
            except ValueError:
                return {"status_code": resp.status_code, "text": resp.text[:4096]}
        except httpx.HTTPStatusError as e:  # type: ignore[misc]
            return {"error": "http_status", "status": e.response.status_code, "detail": e.response.text[:1024]}
        except httpx.RequestError as e:
            return {"error": "request_failed", "detail": str(e)[:1024]}

    return tool


async def main() -> None:
    spec = await fetch_openapi()
    endpoints = extract_endpoints(spec)

    for ep in endpoints:
        create_tool(ep)

    @server.tool("mixpeek.health", desc="Basic health check for the MCP server")
    async def health() -> Any:  # noqa: F841
        return {"ok": True, "tools": len(endpoints)}

    async with stdio_server(server):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())

def run_cli() -> None:
    asyncio.run(main())



