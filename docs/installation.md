# Installation

## Requirements

- Python 3.9+.
- An active Claude Code login, stored in `~/.claude/.credentials.json`.

### Browser, for `open`/`setup`

`claude-kiosk open` (and the desktop launcher `setup` installs) needs
Google Chrome or Chromium on `PATH`: it tries `google-chrome`,
`google-chrome-stable`, `chromium` and `chromium-browser`, in that
order, and opens the first one it finds in `--app` mode (no tabs, no
address bar). `serve` needs none of this; any browser can open its URL.

## Install

=== "uv"

    ```bash
    uv tool install claude-kiosk
    ```

=== "pipx"

    ```bash
    pipx install claude-kiosk
    ```

=== "pip"

    ```bash
    pip install claude-kiosk
    ```

Gets you the `claude-kiosk` command.

## From source (development)

```bash
git clone https://github.com/omadson/claude-kiosk
cd claude-kiosk
uv sync                      # dev deps: typer, pytest, ruff, mkdocs, ...
uv run claude-kiosk serve
```

`pip install .` works the same way as the PyPI package above, just
pointed at the local checkout instead of the index.

See `CONTRIBUTING.md` for the contribution process.
