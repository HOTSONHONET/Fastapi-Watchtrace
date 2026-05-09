from __future__ import annotations

from watchtower.middleware import WatchTowerMiddleware


def test_middleware_should_skip_excluded_prefixes_and_static_assets() -> None:
    middleware = WatchTowerMiddleware(
        app=lambda scope, receive, send: None,
        source_root="/tmp/src",
        output_dir="/tmp/out",
        exclude_paths=["/__watchtower", "/docs"],
    )

    assert middleware._should_skip("/__watchtower/api/requests") is True
    assert middleware._should_skip("/assets/app.js") is True
    assert middleware._should_skip("/api/items") is False
