import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class PytestRunner:
    """Runs pytest tests and generates JSON reports."""

    def __init__(self, project_path: Path, debug: bool = False) -> None:
        """Initialize the pytest runner.
        
        Args:
            project_path: Root path of the project containing tests.
            debug: Enable debug mode with verbose output.
        """
        self.project_path = Path(project_path).resolve()
        self.tmp_dir = Path(tempfile.gettempdir()) / "pytest_ui"
        self.tmp_dir.mkdir(exist_ok=True)
        self.report_file = self.tmp_dir / "report.json"
        self.debug = debug

    def run_tests(self, keyword: Optional[str] = None) -> dict:
        """Execute pytest and generate a JSON report.
        
        Args:
            keyword: Optional pytest keyword filter to run specific tests.
            
        Returns:
            Dictionary containing stdout, stderr, exit_code, and report.
            
        Raises:
            FileNotFoundError: If the project path does not exist.
        """
        if not self.project_path.exists():
            msg = f"Project path does not exist: {self.project_path}"
            logger.error(msg)
            raise FileNotFoundError(msg)

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
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON report: {e}")
                result["stderr"] += f"\n[WARN] Failed to parse JSON report: {e}"

        return result
