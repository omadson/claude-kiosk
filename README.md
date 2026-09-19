<p align="center">
  <img src="https://raw.githubusercontent.com/omadson/claude-kiosk/main/docs/assets/logo.png" alt="claude-kiosk logo" width="120">
</p>

<h1 align="center">claude-kiosk</h1>

<p align="center">
  <a href="https://pypi.org/project/claude-kiosk/"><img src="https://img.shields.io/pypi/v/claude-kiosk" alt="PyPI version"></a>
  <a href="https://omadson.github.io/claude-kiosk/"><img src="https://img.shields.io/badge/docs-online-blue" alt="Docs"></a>
  <a href="https://pepy.tech/project/claude-kiosk"><img src="https://pepy.tech/badge/claude-kiosk" alt="Downloads"></a>
  <a href="https://github.com/omadson/claude-kiosk/blob/main/LICENSE"><img src="https://img.shields.io/github/license/omadson/claude-kiosk" alt="License"></a>
</p>

`claude-kiosk` is a local kiosk display for Claude usage and system resource stats. Shows two screens you tap/click to switch between:

- **Usage**: 5-hour and 7-day Claude usage bars (from the OAuth `usage` endpoint), plus a weather strip (day, time, temperature, humidity) up top.
- **Overview**: memory, CPU and disk usage bars for the host machine.

<p align="center">
  <img src="https://raw.githubusercontent.com/omadson/claude-kiosk/main/docs/assets/screenshots/usage.png" alt="Usage screen" width="49%">
  <img src="https://raw.githubusercontent.com/omadson/claude-kiosk/main/docs/assets/screenshots/overview.png" alt="Overview screen" width="49%">
</p>

It reads your existing Claude Code login from `~/.claude/.credentials.json` (no separate API key needed), and runs entirely locally: no telemetry, no external accounts.

## Installation

```bash
pip install claude-kiosk
```

or

```bash
uv tool install claude-kiosk
```

## Usage

```bash
claude-kiosk serve
```

Open `http://localhost:8420` in your browser, or open it directly in
a dedicated window:

```bash
claude-kiosk open
```

Full documentation, including configuration and the desktop launcher,
at **[omadson.github.io/claude-kiosk](https://omadson.github.io/claude-kiosk/)**.

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full contribution guide.
