from dataclasses import dataclass
from typing import List, Optional


@dataclass
class TestResult:
    nodeid: str
    name: str
    outcome: str
    duration: float
    message: Optional[str]
    file: str


def parse_pytest_report(report: dict) -> List[TestResult]:
    """Transforme le rapport JSON pytest en objets Python."""
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
