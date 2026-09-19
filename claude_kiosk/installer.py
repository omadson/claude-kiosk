"""Installs a desktop launcher for the kiosk."""

import shutil
import subprocess
import sys
from importlib import resources
from pathlib import Path


def install():
    """Render the packaged .desktop template and install it."""
    exe = shutil.which("claude-kiosk") or sys.argv[0]
    pkg = resources.files("claude_kiosk") / "packaging"

    icon_dir = Path.home() / ".local/share/icons/hicolor/256x256/apps"
    icon_dir.mkdir(parents=True, exist_ok=True)
    (icon_dir / "claude-kiosk.png").write_bytes(
        (pkg / "icon.png").read_bytes()
    )

    apps_dir = Path.home() / ".local/share/applications"
    apps_dir.mkdir(parents=True, exist_ok=True)
    desktop = (
        (pkg / "claude-kiosk.desktop").read_text().replace("__EXE__", exe)
    )
    (apps_dir / "claude-kiosk.desktop").write_text(desktop)

    subprocess.run(["update-desktop-database", str(apps_dir)], check=False)
    subprocess.run(
        ["gtk-update-icon-cache", "-f", str(icon_dir.parents[1])], check=False
    )
    print("Installed.")


def uninstall():
    """Remove the desktop launcher and icon."""
    icon = (
        Path.home()
        / ".local/share/icons/hicolor/256x256/apps/claude-kiosk.png"
    )
    apps_dir = Path.home() / ".local/share/applications"
    desktop = apps_dir / "claude-kiosk.desktop"

    for path in (icon, desktop):
        path.unlink(missing_ok=True)

    subprocess.run(["update-desktop-database", str(apps_dir)], check=False)
    subprocess.run(
        ["gtk-update-icon-cache", "-f", str(icon.parents[2])], check=False
    )
    print("Uninstalled.")
