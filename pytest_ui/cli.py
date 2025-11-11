import subprocess
from pathlib import Path

import click


@click.command()
@click.option("--port", default=8585, help="Port Streamlit à utiliser.")
@click.option("--path", default=".", help="Chemin du projet à tester.")
def main(port, path):
    """Lancer l'interface Pytest-UI."""
    app_path = Path(__file__).resolve().parent / "app.py"
    project_path = Path(path).resolve()

    click.echo(f"📂 Tests folder: {project_path}")
    click.echo(f"🧪 Pytest UI is running on http://localhost:{port}")

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

    click.echo(f"✅ Pytest-UI est lancé sur http://localhost:{port}")
    click.echo("🧠 Appuyez sur CTRL+C pour quitter.")

    # Wait for user interrupt
    try:
        process.wait()
    except KeyboardInterrupt:
        click.echo("\n🛑 Arrêt de Pytest-UI...")
        process.terminate()


if __name__ == "__main__":
    main()
