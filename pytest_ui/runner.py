import json
import subprocess
import tempfile
from pathlib import Path
from typing import Optional


class PytestRunner:

    def __init__(self, project_path: Path, debug: bool = False):
        self.project_path = Path(project_path).resolve()
        self.tmp_dir = Path(tempfile.gettempdir()) / "pytest_ui"
        self.tmp_dir.mkdir(exist_ok=True)
        self.report_file = self.tmp_dir / "report.json"
        self.debug = debug

    def run_tests(self, keyword: Optional[str] = None) -> dict:
        """Exécute pytest et génère un rapport JSON."""
        if not self.project_path.exists():
            raise FileNotFoundError(
                f"""
Le dossier {self.project_path} n'existe pas. Veuillez vérifier le chemin."""
            )

        cmd = [
            "pytest",
            str(self.project_path),
            "-vv",
            "--json-report",
            f"--json-report-file={self.report_file}",
            "-q",
        ]
        if keyword:
            cmd += ["-k", keyword]

        if self.debug:
            cmd += ["-v", "-s", "--maxfail=1", "--disable-warnings"]

        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=self.project_path.parent.parent,
            env=None,
        )

        result = {
            "stdout": process.stdout,
            "stderr": process.stderr,
            "exit_code": process.returncode,
            "report": None,
        }

        if self.report_file.exists():
            try:
                with open(self.report_file, "r", encoding="utf-8") as f:
                    result["report"] = json.load(f)
            except json.JSONDecodeError:
                result[
                    "stderr"
                ] += """
\n[WARN] Erreur de parsing du rapport JSON.
"""

        return result
