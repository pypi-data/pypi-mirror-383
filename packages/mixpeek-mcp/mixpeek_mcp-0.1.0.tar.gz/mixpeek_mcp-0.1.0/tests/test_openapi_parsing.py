def test_extract_endpoints_parses_query_path_and_body():
    # local import to ensure test isolation
    import server

    spec = {
        "paths": {
            "/v1/items/{item_id}": {
                "get": {
                    "operationId": "get_item",
                    "parameters": [
                        {"name": "item_id", "in": "path", "required": True},
                        {"name": "verbose", "in": "query", "required": False},
                    ],
                },
                "post": {
                    "operationId": "update_item",
                    "parameters": [
                        {"name": "item_id", "in": "path", "required": True},
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"type": "object"}}},
                    },
                },
            }
        }
    }

    endpoints = server.extract_endpoints(spec)
    ops = {e.operation_id: e for e in endpoints}

    assert "get_item" in ops
    assert "update_item" in ops

    get_ep = ops["get_item"]
    assert get_ep.method == "GET"
    assert any(a.name == "verbose" for a in get_ep.query_args)
    assert any(a.name == "item_id" for a in get_ep.path_args)
    assert get_ep.wants_body is False

    post_ep = ops["update_item"]
    assert post_ep.method == "POST"
    assert any(a.name == "item_id" for a in post_ep.path_args)
    assert post_ep.wants_body is True

