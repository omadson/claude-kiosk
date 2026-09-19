import pytest

from claude_kiosk import browser, server


@pytest.fixture(autouse=True)
def _config(monkeypatch):
    monkeypatch.setattr(server, "_config", dict(server.DEFAULT_CONFIG))
    monkeypatch.setattr(server, "_load_config", lambda: None)
    monkeypatch.setattr(browser, "time", browser.time)
    monkeypatch.setattr(browser.time, "sleep", lambda s: None)


def test_open_kiosk_reuses_running_server(monkeypatch):
    monkeypatch.setattr(browser, "_port_open", lambda port: True)
    started = []
    monkeypatch.setattr(browser, "_start_server", lambda: started.append(True))
    monkeypatch.setattr(
        browser.shutil, "which", lambda name: f"/usr/bin/{name}"
    )
    popens = []
    monkeypatch.setattr(
        browser.subprocess, "Popen", lambda *a, **k: popens.append(a)
    )

    browser.open_kiosk()

    assert started == []
    assert popens == [
        (["/usr/bin/google-chrome", "--app=http://localhost:8420"],)
    ]


def test_open_kiosk_starts_server_when_not_running(monkeypatch):
    calls = {"port_open": iter([False, False, True])}
    monkeypatch.setattr(
        browser, "_port_open", lambda port: next(calls["port_open"])
    )
    started = []
    monkeypatch.setattr(browser, "_start_server", lambda: started.append(True))
    monkeypatch.setattr(
        browser.shutil, "which", lambda name: "/usr/bin/chromium"
    )
    monkeypatch.setattr(browser.subprocess, "Popen", lambda *a, **k: None)

    browser.open_kiosk()

    assert started == [True]


def test_open_kiosk_exits_when_no_browser_found(monkeypatch):
    monkeypatch.setattr(browser, "_port_open", lambda port: True)
    monkeypatch.setattr(browser.shutil, "which", lambda name: None)

    with pytest.raises(SystemExit):
        browser.open_kiosk()


def test_port_open_true_for_listening_socket():
    import socket

    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen(1)
        port = listener.getsockname()[1]
        assert browser._port_open(port) is True


def test_port_open_false_for_closed_port():
    assert browser._port_open(1) is False
