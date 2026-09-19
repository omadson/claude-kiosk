"""HTTP server: aggregates Claude usage, weather and host stats as JSON."""

import json
import os
import shutil
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

PKG_DIR = Path(__file__).resolve().parent
STATIC_DIR = PKG_DIR / "static"

CONFIG_DIR = (
    Path(os.environ.get("XDG_CONFIG_HOME") or "~/.config").expanduser()
    / "claude-kiosk"
)
CACHE_DIR = (
    Path(os.environ.get("XDG_CACHE_HOME") or "~/.cache").expanduser()
    / "claude-kiosk"
)
CONFIG_PATH = CONFIG_DIR / "config.json"
CACHE_PATH = CACHE_DIR / "usage_cache.json"

CREDS_PATH = Path("~/.claude/.credentials.json").expanduser()
USAGE_URL = "https://api.anthropic.com/api/oauth/usage"

# Passaré, Fortaleza-CE; overridable via `claude-kiosk config`
DEFAULT_CONFIG = {
    "weather_lat": -3.8131,
    "weather_lon": -38.5321,
    "port": 8420,
    "min_fetch_interval": 300,  # seconds; avoid tripping the usage API's 429s
    "weather_min_interval": 900,  # seconds; weather doesn't need to be fresher
}
_config = dict(DEFAULT_CONFIG)

_cache = {"data": None, "fetched_at": 0.0}


def _load_cache():
    """Restore the last known usage payload, if any, from disk."""
    try:
        _cache.update(json.loads(CACHE_PATH.read_text()))
    except Exception:
        pass


def _save_cache():
    """Persist the usage payload so a restart can serve it while stale."""
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        CACHE_PATH.write_text(json.dumps(_cache))
    except Exception:
        pass


def _load_config():
    """Load user overrides (e.g. weather location) on top of the defaults."""
    try:
        _config.update(json.loads(CONFIG_PATH.read_text()))
    except Exception:
        pass


def _save_config():
    """Persist the current config so it survives a restart."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(_config))


def fetch_usage():
    """Fetch 5h/7d Claude usage, using OAuth creds and a short-lived cache."""
    now = time.time()
    if (
        _cache["data"]
        and now - _cache["fetched_at"] < _config["min_fetch_interval"]
    ):
        return _cache["data"]

    try:
        with open(CREDS_PATH) as f:
            creds = json.load(f)
        token = creds["claudeAiOauth"]["accessToken"]
        req = urllib.request.Request(
            USAGE_URL,
            headers={
                "Authorization": f"Bearer {token}",
                "anthropic-beta": "oauth-2025-04-20",
                "User-Agent": "claude-kiosk",
            },
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            payload = json.load(resp)
        five = payload.get("five_hour") or {}
        seven = payload.get("seven_day") or {}
        data = {
            "session": {
                "pct": five.get("utilization", 0),
                "resets_at": five.get("resets_at"),
            },
            "week": {
                "pct": seven.get("utilization", 0),
                "resets_at": seven.get("resets_at"),
            },
        }
        _cache["data"] = data
        _cache["fetched_at"] = now
        _save_cache()
        return data
    except Exception:
        if _cache["data"]:
            return _cache[
                "data"
            ]  # serve stale data instead of breaking the page (e.g. on 429)
        raise


_weather_cache = {"data": None, "fetched_at": 0.0}


def fetch_weather():
    """Fetch current conditions for the configured location, cached 15min."""
    now = time.time()
    if (
        _weather_cache["data"]
        and now - _weather_cache["fetched_at"]
        < _config["weather_min_interval"]
    ):
        return _weather_cache["data"]
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={_config['weather_lat']}"
            f"&longitude={_config['weather_lon']}"
            "&current=temperature_2m,relative_humidity_2m,weather_code&timezone=auto"
        )
        req = urllib.request.Request(
            url, headers={"User-Agent": "claude-kiosk"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            payload = json.load(resp)
        current = payload.get("current") or {}
        data = {
            "temp": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "code": current.get("weather_code"),
        }
        _weather_cache["data"] = data
        _weather_cache["fetched_at"] = now
        return data
    except Exception:
        return _weather_cache["data"]  # None is fine; frontend hides the block


def fetch_disk():
    """Report root filesystem usage."""
    total, used, free = shutil.disk_usage("/")
    return {
        "total": total,
        "used": used,
        "free": free,
        "pct": used / total * 100,
    }


def fetch_memory():
    """Report RAM/swap usage by parsing /proc/meminfo (Linux-only)."""
    # ponytail: Linux-only; swap to psutil if cross-platform needed
    info = {}
    with open("/proc/meminfo") as f:
        for line in f:
            key, val = line.split(":", 1)
            info[key] = int(val.split()[0]) * 1024  # kB -> bytes
    total = info["MemTotal"]
    free = info.get("MemAvailable", info["MemFree"])
    used = total - free
    swap_total = info.get("SwapTotal", 0)
    swap_free = info.get("SwapFree", 0)
    swap_used = swap_total - swap_free
    return {
        "total": total,
        "used": used,
        "free": free,
        "pct": used / total * 100,
        "swap": {
            "total": swap_total,
            "used": swap_used,
            "free": swap_free,
            "pct": (swap_used / swap_total * 100) if swap_total else 0,
        },
    }


_cpu_prev = {"total": None, "idle": None}


def fetch_cpu():
    """Report instantaneous CPU%, diffed against the previous call."""
    # ponytail: Linux-only; swap to psutil if cross-platform needed
    with open("/proc/stat") as f:
        vals = [
            int(x) for x in f.readline().split()[1:8]
        ]  # user nice system idle iowait irq softirq
    idle = vals[3] + vals[4]
    total = sum(vals)
    prev_total, prev_idle = _cpu_prev["total"], _cpu_prev["idle"]
    _cpu_prev["total"], _cpu_prev["idle"] = total, idle
    if prev_total is None:
        return {"pct": 0, "cores": os.cpu_count()}
    dtotal = total - prev_total
    didle = idle - prev_idle
    pct = (1 - didle / dtotal) * 100 if dtotal else 0
    return {"pct": pct, "cores": os.cpu_count()}


class Handler(BaseHTTPRequestHandler):
    """Serves the static dashboard plus /api/usage."""

    def log_message(self, *args):
        pass

    STATIC = {
        "/": ("index.html", "text/html; charset=utf-8"),
        "/style.css": ("style.css", "text/css"),
        "/script.js": ("script.js", "application/javascript"),
        "/favicon.png": ("favicon.png", "image/png"),
    }

    def _send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in self.STATIC:
            filename, content_type = self.STATIC[self.path]
            with open(STATIC_DIR / filename, "rb") as f:
                body = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/api/usage":
            try:
                data = fetch_usage()
            except Exception as e:
                data = {"error": str(e)}
            data["weather"] = fetch_weather()
            data["disk"] = fetch_disk()
            data["memory"] = fetch_memory()
            data["cpu"] = fetch_cpu()
            self._send_json(data)
        else:
            self.send_response(404)
            self.end_headers()


def run_server():
    """Load persisted state and serve the dashboard until interrupted."""
    _load_cache()
    _load_config()
    port = _config["port"]
    print(f"http://localhost:{port}")
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()
