"""Command-line entry point for claude-kiosk."""

from typing import Optional

import typer

from claude_kiosk import __version__

app = typer.Typer(
    help="Local kiosk display for Claude usage and system resource stats."
)


def _version_callback(value: bool):
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=_version_callback,
        is_eager=True,
        help="Show the version and exit.",
    ),
):
    pass


@app.command()
def serve():
    """Run the HTTP server and serve the dashboard over a browser."""
    from claude_kiosk.server import run_server

    run_server()


@app.command()
def open():
    """Open the dashboard in a browser app window (starts serve if needed)."""
    from claude_kiosk.browser import open_kiosk

    open_kiosk()


@app.command()
def config(
    lat: Optional[float] = typer.Option(
        None, "--lat", help="Weather latitude (-90 to 90)."
    ),
    lon: Optional[float] = typer.Option(
        None, "--lon", help="Weather longitude (-180 to 180)."
    ),
    port: Optional[int] = typer.Option(
        None, "--port", help="HTTP server port."
    ),
    min_fetch_interval: Optional[int] = typer.Option(
        None,
        "--min-fetch-interval",
        help="Seconds between Claude usage API calls.",
    ),
    weather_min_interval: Optional[int] = typer.Option(
        None,
        "--weather-min-interval",
        help="Seconds between weather API calls.",
    ),
):
    """Show or update persisted config (weather location, port, ...)."""
    from claude_kiosk import server

    server._load_config()

    if lat is not None or lon is not None:
        new_lat = lat if lat is not None else server._config["weather_lat"]
        new_lon = lon if lon is not None else server._config["weather_lon"]
        if not (-90 <= new_lat <= 90 and -180 <= new_lon <= 180):
            typer.echo(
                "Error: --lat must be -90..90, --lon must be -180..180.",
                err=True,
            )
            raise typer.Exit(1)
        server._config["weather_lat"] = new_lat
        server._config["weather_lon"] = new_lon
    if port is not None:
        server._config["port"] = port
    if min_fetch_interval is not None:
        server._config["min_fetch_interval"] = min_fetch_interval
    if weather_min_interval is not None:
        server._config["weather_min_interval"] = weather_min_interval

    if any(
        v is not None
        for v in (lat, lon, port, min_fetch_interval, weather_min_interval)
    ):
        server._save_config()

    for key, value in server._config.items():
        typer.echo(f"{key}: {value}")


@app.command()
def setup():
    """Install a desktop launcher for the kiosk."""
    from claude_kiosk.installer import install as _install

    _install()


@app.command()
def uninstall():
    """Remove the desktop launcher."""
    from claude_kiosk.installer import uninstall as _uninstall

    _uninstall()


if __name__ == "__main__":
    app()
