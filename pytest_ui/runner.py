import json
import subprocess
import tempfile
from pathlib import Path
from typing import Optional


class PytestRunner:
    def __init__(self, project_path: Path):
        self.project_path = Path(project_path).resolve()
        self.tmp_dir = Path(tempfile.gettempdir()) / "pytest_ui"
        self.tmp_dir.mkdir(exist_ok=True)
        self.report_file = self.tmp_dir / "report.json"

    def run_tests(self, keyword: Optional[str] = None) -> dict:
        """Exécute pytest et génère un rapport JSON."""
        cmd = [
            "pytest",
            str(self.project_path),
            "--json-report",
            f"--json-report-file={self.report_file}",
            "-q",  # mode quiet
        ]
        if keyword:
            cmd += ["-k", keyword]

        process = subprocess.run(
            cmd, capture_output=True, text=True, cwd=self.project_path
        )

        output = {
            "stdout": process.stdout,
            "stderr": process.stderr,
            "exit_code": process.returncode,
        }

        print(output)

        # Charger le rapport JSON si disponible
        if self.report_file.exists():
            with open(self.report_file, "r", encoding="utf-8") as f:
                report_data = json.load(f)
            output["report"] = report_data
        else:
            output["report"] = None

        return output
