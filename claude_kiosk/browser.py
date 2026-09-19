"""Opens the dashboard in a Chrome/Chromium app window, starting the
HTTP server first if it isn't already running."""

import shutil
import socket
import subprocess
import sys
import time

from claude_kiosk import server

BROWSERS = (
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
)


def _port_open(port):
    with socket.socket() as sock:
        sock.settimeout(0.3)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def _start_server():
    subprocess.Popen(
        [
            sys.executable,
            "-c",
            "from claude_kiosk.server import run_server; run_server()",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
    )


def open_kiosk():
    """Ensure the server is running, then open it in a browser app window."""
    server._load_config()
    port = server._config["port"]

    if not _port_open(port):
        _start_server()
        for _ in range(50):  # ~5s
            if _port_open(port):
                break
            time.sleep(0.1)

    browser_path = next(
        (p for p in (shutil.which(b) for b in BROWSERS) if p), None
    )
    if browser_path is None:
        print("No Chrome/Chromium found. Open manually:")
        print(f"  http://localhost:{port}")
        raise SystemExit(1)

    subprocess.Popen(
        [browser_path, f"--app=http://localhost:{port}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
    )
