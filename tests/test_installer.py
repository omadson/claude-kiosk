import sys

from claude_kiosk import installer


def test_install_writes_desktop_launcher(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr(
        installer.shutil, "which", lambda name: "/usr/bin/claude-kiosk"
    )
    calls = []
    monkeypatch.setattr(
        installer.subprocess, "run", lambda *a, **k: calls.append(a)
    )

    installer.install()

    desktop = tmp_path / ".local/share/applications/claude-kiosk.desktop"
    icon = (
        tmp_path / ".local/share/icons/hicolor/256x256/apps/claude-kiosk.png"
    )
    assert "/usr/bin/claude-kiosk open" in desktop.read_text()
    assert icon.exists()
    assert len(calls) == 2


def test_install_falls_back_to_argv0(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr(installer.shutil, "which", lambda name: None)
    monkeypatch.setattr(sys, "argv", ["/fallback/claude-kiosk"])
    monkeypatch.setattr(installer.subprocess, "run", lambda *a, **k: None)

    installer.install()

    desktop = tmp_path / ".local/share/applications/claude-kiosk.desktop"
    assert "/fallback/claude-kiosk open" in desktop.read_text()


def test_uninstall_removes_files(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr(
        installer.shutil, "which", lambda name: "/usr/bin/claude-kiosk"
    )
    monkeypatch.setattr(installer.subprocess, "run", lambda *a, **k: None)
    installer.install()

    desktop = tmp_path / ".local/share/applications/claude-kiosk.desktop"
    icon = (
        tmp_path / ".local/share/icons/hicolor/256x256/apps/claude-kiosk.png"
    )
    assert desktop.exists() and icon.exists()

    installer.uninstall()

    assert not desktop.exists()
    assert not icon.exists()


def test_uninstall_ignores_missing_files(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr(installer.subprocess, "run", lambda *a, **k: None)

    installer.uninstall()
