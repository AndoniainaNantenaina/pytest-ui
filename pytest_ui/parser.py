import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Result data for a single pytest test.
    
    Attributes:
        nodeid: Unique pytest node identifier (file::class::test).
        name: Test function name.
        outcome: Test outcome (passed, failed, skipped).
        duration: Test execution time in seconds.
        message: Error message or log output from test failure.
        file: Path to the test file.
    """
    nodeid: str
    name: str
    outcome: str
    duration: float
    message: Optional[str]
    file: str


def parse_pytest_report(report: dict) -> list[TestResult]:
    """Convert a pytest JSON report to TestResult objects.
    
    Args:
        report: Parsed JSON report from pytest.
        
    Returns:
        List of TestResult objects extracted from the report.
    """
    if not report or "tests" not in report:
        return []

    results = []
    for test in report["tests"]:
        name = test.get("keywords", [test["nodeid"].split("::")[-1]])[0]
        results.append(
            TestResult(
                nodeid=test["nodeid"],
                name=name,
                outcome=test["outcome"],
                duration=test.get("duration", 0.0),
                message=test.get("call", {}).get("longrepr", ""),
                file=test.get("file", test["nodeid"].split("::")[0]),
            )
        )
    return results
