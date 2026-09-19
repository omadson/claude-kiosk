import json

from typer.testing import CliRunner

from claude_kiosk import __version__, browser, installer, server
from claude_kiosk.cli import app

runner = CliRunner()


def test_version_flag_prints_version_and_exits():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert result.output.strip() == __version__


def test_version_short_flag_prints_version_and_exits():
    result = runner.invoke(app, ["-v"])
    assert result.exit_code == 0
    assert result.output.strip() == __version__


def test_help_lists_commands():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "serve" in result.output
    assert "open" in result.output
    assert "config" in result.output
    assert "setup" in result.output
    assert "uninstall" in result.output


def test_serve_command_invokes_run_server(monkeypatch):
    called = []
    monkeypatch.setattr(server, "run_server", lambda: called.append(True))
    result = runner.invoke(app, ["serve"])
    assert result.exit_code == 0
    assert called == [True]


def test_open_command_invokes_open_kiosk(monkeypatch):
    called = []
    monkeypatch.setattr(browser, "open_kiosk", lambda: called.append(True))
    result = runner.invoke(app, ["open"])
    assert result.exit_code == 0
    assert called == [True]


def test_config_command_shows_current_config(monkeypatch, tmp_path):
    monkeypatch.setattr(server, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(server, "CONFIG_PATH", tmp_path / "config.json")
    monkeypatch.setattr(server, "_config", dict(server.DEFAULT_CONFIG))

    result = runner.invoke(app, ["config"])

    assert result.exit_code == 0
    assert "port: 8420" in result.output
    assert not (tmp_path / "config.json").exists()


def test_config_command_updates_and_persists(monkeypatch, tmp_path):
    monkeypatch.setattr(server, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(server, "CONFIG_PATH", tmp_path / "config.json")
    monkeypatch.setattr(server, "_config", dict(server.DEFAULT_CONFIG))

    result = runner.invoke(
        app, ["config", "--lat", "10", "--lon", "20", "--port", "9000"]
    )

    assert result.exit_code == 0
    assert "port: 9000" in result.output
    saved = json.loads((tmp_path / "config.json").read_text())
    assert saved["weather_lat"] == 10.0
    assert saved["weather_lon"] == 20.0
    assert saved["port"] == 9000


def test_config_command_rejects_out_of_range_lat(monkeypatch, tmp_path):
    monkeypatch.setattr(server, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(server, "CONFIG_PATH", tmp_path / "config.json")
    monkeypatch.setattr(server, "_config", dict(server.DEFAULT_CONFIG))

    result = runner.invoke(app, ["config", "--lat", "999"])

    assert result.exit_code == 1
    assert not (tmp_path / "config.json").exists()


def test_setup_command_invokes_installer(monkeypatch):
    called = []
    monkeypatch.setattr(installer, "install", lambda: called.append(True))
    result = runner.invoke(app, ["setup"])
    assert result.exit_code == 0
    assert called == [True]


def test_uninstall_command_invokes_installer(monkeypatch):
    called = []
    monkeypatch.setattr(installer, "uninstall", lambda: called.append(True))
    result = runner.invoke(app, ["uninstall"])
    assert result.exit_code == 0
    assert called == [True]
