import subprocess
from pathlib import Path

import click


@click.command()
@click.option("--port", default=8585, help="Port Streamlit à utiliser.")
@click.option("--path", default=".", help="Chemin du projet à tester.")
def main(port, path):
    """Lancer l'interface Pytest-UI."""
    app_path = Path(__file__).parent / "app.py"
    cmd = [
        "streamlit",
        "run",
        str(app_path),
        "--server.port",
        str(port),
        "--",
        path,
    ]
    subprocess.run(cmd)


if __name__ == "__main__":
    main()
