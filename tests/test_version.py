from claude_kiosk import __version__


def test_version():
    assert isinstance(__version__, str) and __version__
