# Usage

Every `claude-kiosk` command, in the order `--help` lists them.

## Show the version

`claude-kiosk --version` (or `-v`) prints the installed version and exits.

<div data-copy="claude-kiosk --version">

```console
$ claude-kiosk --version

0.1.0
```

</div>

## Open kiosk in browser

`claude-kiosk serve` runs the HTTP server. Open `http://localhost:8420`
in any browser.

<div data-copy="claude-kiosk serve">

```console
$ claude-kiosk serve

http://localhost:8420
```

</div>

## Open kiosk in a window

`claude-kiosk open` starts the server if it isn't already running, then
opens it in a Chrome/Chromium `--app` window (no tabs, no address bar).
Reuses the server if one is already listening on the configured port.

<div data-copy="claude-kiosk open">

```console
$ claude-kiosk open
```

</div>

!!! note
    Needs Chrome or Chromium on `PATH`; see
    [Installation](installation.md#requirements). None
    found: prints the dashboard URL instead of opening a window.

## Show or update configuration

`claude-kiosk config` shows or updates persisted settings: weather
location, HTTP port, and API polling intervals. Run with no flags to
see current values; see [Configuration](#configuration) below for what
each one does.

<div data-copy="claude-kiosk config --lat -3.8131 --lon -38.5321">

```console
$ claude-kiosk config --lat -3.8131 --lon -38.5321

weather_lat: -3.8131
weather_lon: -38.5321
port: 8420
min_fetch_interval: 300
weather_min_interval: 900
```

</div>

## Configuration

Everything below is set with
[`claude-kiosk config`](#show-or-update-configuration) and persisted to
`$XDG_CONFIG_HOME/claude-kiosk/config.json`; no source edits, no rebuild.

### Weather location

```bash
claude-kiosk config --lat -3.8131 --lon -38.5321
```

`--lat`/`--lon` must be set together, validated to `[-90, 90]`/`[-180,
180]`. Defaults to Passaré, Fortaleza-CE (`-3.8131, -38.5321`).

### Port and caching intervals

```bash
claude-kiosk config --port 9000 --min-fetch-interval 300 --weather-min-interval 900
```

| Flag | Default | What it controls |
|---|---|---|
| `--port` | `8420` | HTTP server port. |
| `--min-fetch-interval` | 300s | Minimum gap between `usage` API calls, to avoid tripping rate limits. |
| `--weather-min-interval` | 900s | Minimum gap between weather API calls. |

!!! note
    Restart `serve` after changing `--port` for it to take effect; a
    running server keeps listening on its original port.

### File locations (XDG)

The package is installed read-only into site-packages, so config/cache
live under XDG dirs instead of next to the code:

| Path | Contents |
|---|---|
| `$XDG_CONFIG_HOME/claude-kiosk/config.json` (`~/.config/...` by default) | Weather lat/lon, port, polling intervals. |
| `$XDG_CACHE_HOME/claude-kiosk/usage_cache.json` (`~/.cache/...` by default) | Last known Claude usage payload, so a restart can serve it while the API is unreachable. |

!!! note
    Neither file is created until first written (`claude-kiosk config`
    with at least one flag, or the first successful `/api/usage` fetch).

## Install a desktop launcher

`claude-kiosk setup` installs a `.desktop` launcher
(`~/.local/share/applications`) and icon that run `claude-kiosk open`
from your app menu.

<div data-copy="claude-kiosk setup">

```console
$ claude-kiosk setup

Installed.
```

</div>

## Remove the desktop launcher

`claude-kiosk uninstall` reverses `setup`: removes the launcher and
icon it created.

<div data-copy="claude-kiosk uninstall">

```console
$ claude-kiosk uninstall

Uninstalled.
```

</div>

## HTTP API

`serve`/`open` expose one JSON endpoint the dashboard polls; anything
else can hit it too.

```bash
curl http://localhost:8420/api/usage
```

```json
{
  "session": {"pct": 42.0, "resets_at": "2026-09-19T18:00:00Z"},
  "week": {"pct": 17.5, "resets_at": "2026-09-25T00:00:00Z"},
  "weather": {"temp": 29.4, "humidity": 68, "code": 1},
  "disk": {"total": 512110190592, "used": 210110190592, "free": 302000000000, "pct": 41.0},
  "memory": {"total": 16656896000, "used": 9800000000, "free": 6856896000, "pct": 58.8,
             "swap": {"total": 8589934592, "used": 0, "free": 8589934592, "pct": 0}},
  "cpu": {"pct": 12.3, "cores": 8}
}
```

`session`/`week` come from the Claude OAuth `usage` endpoint and are
cached for `--min-fetch-interval` seconds; `weather` is cached for
`--weather-min-interval` seconds and is `null` if the last fetch
failed. `disk`/`memory`/`cpu` describe the host machine and are always
read fresh.
