import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st

from pytest_ui.parser import TestResult, parse_pytest_report
from pytest_ui.runner import PytestRunner


def _get_project_path_from_cli() -> Path:
    """Récupère le chemin passé après le `--` de streamlit run."""
    if len(sys.argv) > 1:
        return Path(sys.argv[-1]).resolve()
    return Path(".").resolve()


@dataclass
class Config:
    tests_path: Path
    keyword: Optional[str] = None


def _configure() -> Config:
    st.header(":material/experiment: Pytest UI")

    default_path = _get_project_path_from_cli()

    project_path = st.text_input(
        "Tests folder",
        value=str(default_path),
        disabled=True,
    )

    return Config(tests_path=Path(project_path), keyword=None)


@st.cache_data(show_spinner="Running tests...")
def _run_tests(
    tests_path: Path | str,
    keyword: Optional[str] = None,
) -> list[TestResult] | None:
    runner = PytestRunner(Path(tests_path), debug=False)

    # List all test files in the tests_path
    test_files = list(Path(tests_path).rglob("test_*.py"))

    for f in test_files:
        st.write(f":material/check_circle: {f.relative_to(tests_path)}")

    output = runner.run_tests(keyword=keyword)

    report = output.get("report")
    out = output["stdout"] or output["stderr"] or "No output."

    if not report:
        return None, out

    return parse_pytest_report(report), out


if __name__ == "__main__":
    st.set_page_config(page_title="Pytest UI", layout="centered")

    config = _configure()

    if not config:
        st.stop()

    # --- Lancement des tests ---
    run = st.button(
        "Run Tests",
        width="stretch",
        icon=":material/play_arrow:",
        type="primary",
    )

    if not run and st.session_state.get("running", False) is not True:
        st.session_state["running"] = False
        st.stop()

    st.session_state["running"] = True

    results, output = _run_tests(config.tests_path, keyword=config.keyword)

    if not results:
        st.code(output, language="bash")
        st.warning(
            """
Unable to run tests.
Please check the output above for errors.
"""
        )
        st.stop()

    # --- Affichage des résultats ---
    df = pd.DataFrame([r.__dict__ for r in results])
    passed = len(df[df["outcome"] == "passed"])
    failed = len(df[df["outcome"] == "failed"])
    total = len(df)

    c1, c2, c3 = st.columns(3, width="stretch")
    with c1:
        st.metric("🟢 PASSED", passed, border=True)
    with c2:
        st.metric("🟡 FAILED", failed, border=True)
    with c3:
        st.metric(":material/experiment: TOTAL", total, border=True)
    st.divider()

    df["nodeid"] = df["nodeid"].astype(str).str.split("::").str[0]
    df["outcome"] = df["outcome"].astype(str).str.upper()
    df["outcome"] = df["outcome"].replace(
        {
            "PASSED": "🟢",
            "FAILED": "🟡",
            "SKIPPED": ">>",
        }
    )

    grouped = df.groupby("nodeid")
    for outcome, group in grouped:
        group_failed_len = len(group[group["outcome"] == "🟡"])
        group_passed_len = len(group[group["outcome"] == "🟢"])

        status = "🟢" if group_failed_len == 0 else "🟡"

        with st.expander(
            f"{status} *{outcome} ({group_passed_len}/{len(group)})*",
        ):
            group = group.set_index("outcome")
            st.dataframe(group, width="stretch")

    st.subheader("📃Logs")
    selected = st.selectbox("Afficher les logs d'un test :", df["name"])
    test = df[df["name"] == selected].iloc[0]
    st.code(
        test["message"] or "Aucun message.",
        language="bash",
        line_numbers=True,
        height="content",
    )
