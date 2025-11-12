import subprocess
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

    click.echo(click.style(PYTEST_UI_WELCOME_TEXT, fg="cyan"))
    click.echo("🧪 Pytest UI is running on :")
    click.echo(f"   - 📂 {project_path}")
    click.echo(click.style(f"   - 🔗 http://localhost:{port}", fg="green"))

    cmd = [
        "streamlit",
        "run",
        str(app_path),
        "--server.port",
        str(port),
        "--",
        str(project_path),
    ]

    process = subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Wait for user interrupt
    try:
        process.wait()
    except KeyboardInterrupt:
        process.terminate()


if __name__ == "__main__":
    main()
