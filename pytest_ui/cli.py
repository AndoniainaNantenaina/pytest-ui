import os
import subprocess
from importlib.resources import files
from pathlib import Path

import click

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
    help="Port to run the Pytest-UI server on.",
)
@click.option(
    "--path",
    default=".",
    help="Path to the folder containing tests files.",
)
def main(port, path):
    """Launch the Pytest-UI interface."""
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

    subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


if __name__ == "__main__":
    main()
