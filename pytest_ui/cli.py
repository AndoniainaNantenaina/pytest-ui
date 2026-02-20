import logging
import os
import subprocess
from importlib.resources import files
from pathlib import Path

import click

logger = logging.getLogger(__name__)

PYTEST_UI_WELCOME_TEXT = """
██████╗ ██╗   ██╗████████╗███████╗███████╗████████╗    ██╗   ██╗██╗
██╔══██╗╚██╗ ██╔╝╚══██╔══╝██╔════╝██╔════╝╚══██╔══╝    ██║   ██║██║
██████╔╝ ╚████╔╝    ██║   █████╗  ███████╗   ██║       ██║   ██║██║
██╔═══╝   ╚██╔╝     ██║   ██╔══╝  ╚════██║   ██║       ██║   ██║██║
██║        ██║      ██║   ███████╗███████║   ██║       ╚██████╔╝██║
╚═╝        ╚═╝      ╚═╝   ╚══════╝╚══════╝   ╚═╝        ╚═════╝ ╚═╝
        """


@click.command()
@click.option(
    "--port",
    default=8585,
    type=click.IntRange(1, 65535),
    help="Port to run the Pytest-UI server on (1-65535).",
)
@click.option(
    "--path",
    default=".",
    type=click.Path(exists=True, path_type=Path),
    help="Path to a test file or folder containing tests files.",
)
def main(port: int, path: Path) -> None:
    """Launch the Pytest-UI interface.

    Args:
        port: Port number to run the server on (1-65535).
        path: Path to a test file (.py) or folder containing tests files.
    """
    app_path = Path(__file__).resolve().parent / "app.py"
    project_path = Path(path).resolve()

    # Capture the path where the cli is executed
    whereis = Path.cwd()

    click.echo(click.style(PYTEST_UI_WELCOME_TEXT, fg="cyan"))
    click.echo("🧪 Pytest UI is running on :")
    click.echo(f"   - 📍 {whereis}")
    click.echo(f"   - 📂 {project_path}")
    click.echo(click.style(f"   - 🔗 http://localhost:{port}", fg="green"))

    config_dir = files("pytest_ui").joinpath(".streamlit")
    os.environ["STREAMLIT_CONFIG_DIR"] = str(config_dir)

    cmd = [
        "streamlit",
        "run",
        str(app_path),
        "--server.port",
        str(port),
        "--",
        str(project_path),
        "--whereis",
        str(whereis),
    ]

    try:
        subprocess.run(cmd, check=False)
    except FileNotFoundError as e:
        logger.error(f"Failed to launch Streamlit: {e}")
        click.echo(click.style("Error: Streamlit is not installed.", fg="red"))
        raise click.ClickException("Please install Streamlit to use pytest-ui.")


if __name__ == "__main__":
    main()
