import json
import threading
import time
import urllib.error
import urllib.request

import pytest

from claude_kiosk import server


@pytest.fixture
def running_server(monkeypatch, tmp_path):
    monkeypatch.setattr(server, "CONFIG_DIR", tmp_path / "config")
    monkeypatch.setattr(
        server, "CONFIG_PATH", tmp_path / "config" / "config.json"
    )
    monkeypatch.setattr(server, "CACHE_DIR", tmp_path / "cache")
    monkeypatch.setattr(
        server, "CACHE_PATH", tmp_path / "cache" / "usage_cache.json"
    )
    monkeypatch.setattr(server, "_config", dict(server.DEFAULT_CONFIG))
    monkeypatch.setattr(server, "CREDS_PATH", tmp_path / "no-creds.json")
    monkeypatch.setattr(server, "_cache", {"data": None, "fetched_at": 0.0})
    monkeypatch.setattr(server, "_account_caches", {})

    httpd = server.HTTPServer(("127.0.0.1", 0), server.Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{httpd.server_port}"
    finally:
        httpd.shutdown()
        thread.join()


def test_fetch_disk_shape():
    data = server.fetch_disk()
    assert data["total"] > 0
    assert 0 <= data["pct"] <= 100


def test_fetch_memory_shape():
    data = server.fetch_memory()
    assert data["total"] > 0
    assert "swap" in data


def test_fetch_cpu_shape():
    server.fetch_cpu()  # first call has no prior sample
    data = server.fetch_cpu()
    assert "cores" in data
    assert data["cores"] >= 1


def test_config_roundtrip(monkeypatch, tmp_path):
    monkeypatch.setattr(server, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(server, "CONFIG_PATH", tmp_path / "config.json")
    monkeypatch.setattr(
        server, "_config", {"weather_lat": 1.0, "weather_lon": 2.0}
    )
    server._save_config()
    monkeypatch.setattr(server, "_config", dict(server.DEFAULT_CONFIG))
    server._load_config()
    assert server._config == {
        **server.DEFAULT_CONFIG,
        "weather_lat": 1.0,
        "weather_lon": 2.0,
    }


def test_static_routes(running_server):
    for path in ("/", "/style.css", "/script.js", "/favicon.png"):
        with urllib.request.urlopen(f"{running_server}{path}") as resp:
            assert resp.status == 200


def test_unknown_route_404(running_server):
    with pytest.raises(urllib.error.HTTPError) as exc:
        urllib.request.urlopen(f"{running_server}/nope")
    assert exc.value.code == 404


def test_config_route_removed(running_server):
    with pytest.raises(urllib.error.HTTPError) as exc:
        urllib.request.urlopen(f"{running_server}/config")
    assert exc.value.code == 404


def test_api_config_route_removed(running_server):
    with pytest.raises(urllib.error.HTTPError) as exc:
        urllib.request.urlopen(f"{running_server}/api/config")
    assert exc.value.code == 404


def test_api_usage(running_server):
    with urllib.request.urlopen(f"{running_server}/api/usage") as resp:
        data = json.loads(resp.read())
    assert "disk" in data and "memory" in data and "cpu" in data
    assert data["city"] == server.DEFAULT_CONFIG["weather_city"]


def test_geocode_city_parses_response(monkeypatch):
    class FakeResp:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return b'{"city": "Testville", "countryName": "Testland"}'

    monkeypatch.setattr(
        server.urllib.request, "urlopen", lambda *a, **k: FakeResp()
    )
    assert server.geocode_city(1.0, 2.0) == "Testville"


def test_geocode_city_returns_none_on_failure(monkeypatch):
    def boom(*a, **k):
        raise OSError("network down")

    monkeypatch.setattr(server.urllib.request, "urlopen", boom)
    assert server.geocode_city(1.0, 2.0) is None


def _stale_cache(resets_at, fetched_at=0.0):
    return {
        "data": {
            "session": {"pct": 42.0, "resets_at": resets_at},
            "week": {"pct": 42.0, "resets_at": resets_at},
        },
        "fetched_at": fetched_at,
    }


def test_fetch_usage_zeroes_expired_window_on_stale_fallback(
    monkeypatch, tmp_path
):
    past = "2000-01-01T00:00:00+00:00"
    monkeypatch.setattr(server, "_cache", _stale_cache(past))
    monkeypatch.setattr(server, "CREDS_PATH", tmp_path / "no-creds.json")
    monkeypatch.setattr(
        server, "_config", {**server.DEFAULT_CONFIG, "min_fetch_interval": 0}
    )

    data = server.fetch_usage()

    assert data["session"] == {"pct": 0, "resets_at": None}
    assert data["week"] == {"pct": 0, "resets_at": None}


def test_fetch_usage_keeps_cache_hit_before_min_interval_but_zeroes_expired(
    monkeypatch,
):
    past = "2000-01-01T00:00:00+00:00"
    monkeypatch.setattr(
        server, "_cache", _stale_cache(past, fetched_at=time.time())
    )
    monkeypatch.setattr(
        server,
        "_config",
        {**server.DEFAULT_CONFIG, "min_fetch_interval": 999999},
    )

    data = server.fetch_usage()

    assert data["session"]["pct"] == 0
    assert data["week"]["pct"] == 0


def test_fetch_usage_extra_account_reads_its_own_creds_and_cache(
    monkeypatch, tmp_path
):
    (tmp_path / ".credentials.json").write_text(
        '{"claudeAiOauth": {"accessToken": "tok-b"}}'
    )
    seen = []

    class FakeResp:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return (
                b'{"five_hour": {"utilization": 7}, '
                b'"seven_day": {"utilization": 9}}'
            )

    def fake_urlopen(req, **k):
        seen.append(req.get_header("Authorization"))
        return FakeResp()

    monkeypatch.setattr(server.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(server, "_account_caches", {})
    monkeypatch.setattr(server, "_cache", {"data": None, "fetched_at": 0.0})

    data = server.fetch_usage(str(tmp_path))
    server.fetch_usage(str(tmp_path))  # served from cache

    assert seen == ["Bearer tok-b"]
    assert data["session"]["pct"] == 7
    assert data["week"]["pct"] == 9
    assert server._cache["data"] is None  # default account untouched


def test_api_usage_lists_extra_accounts_with_per_account_error(
    running_server, tmp_path
):
    server._config["accounts"] = [
        {"name": "work", "config_dir": str(tmp_path / "missing")}
    ]
    with urllib.request.urlopen(f"{running_server}/api/usage") as resp:
        data = json.loads(resp.read())
    assert data["accounts"][0]["name"] == "work"
    assert "error" in data["accounts"][0]


def test_fetch_usage_backs_off_after_failure(monkeypatch, tmp_path):
    calls = []

    def boom(*a, **k):
        calls.append(1)
        raise OSError("HTTP Error 429: Too Many Requests")

    creds = tmp_path / ".credentials.json"
    creds.write_text('{"claudeAiOauth": {"accessToken": "t"}}')
    monkeypatch.setattr(server.urllib.request, "urlopen", boom)
    monkeypatch.setattr(server, "_account_caches", {})
    monkeypatch.setattr(server, "_failures", {})

    for _ in range(3):
        with pytest.raises(Exception, match="429"):
            server.fetch_usage(str(tmp_path))

    assert len(calls) == 1
