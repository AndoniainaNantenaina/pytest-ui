import sys
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st

from pytest_ui.parser import TestResult, parse_pytest_report
from pytest_ui.runner import PytestRunner

# ---------------------------------------------------------
# UTILITIES
# ---------------------------------------------------------


def _get_project_path_from_cli() -> Path:
    """Get project path passed after streamlit run."""
    if len(sys.argv) > 1:
        return Path(sys.argv[1]).resolve()
    return Path(".").resolve()


@dataclass
class Config:
    tests_path: Path
    keyword: Optional[str] = None


def _configure() -> Config:
    default_path = _get_project_path_from_cli()
    return Config(tests_path=Path(default_path), keyword=None)


@st.cache_data(show_spinner=False)
def _run_tests(
    tests_path: Path | str,
    keyword: Optional[str] = None,
) -> tuple[list["TestResult"] | None, str]:
    """Run Pytest and return (results, output)."""
    runner = PytestRunner(Path(tests_path), debug=False)

    output = runner.run_tests(keyword=keyword)
    report = output.get("report")
    out = output["stdout"] or output["stderr"] or "No output."

    if not report:
        return None, out

    return parse_pytest_report(report), out


# ---------------------------------------------------------
# UI SECTIONS
# ---------------------------------------------------------


def sidebar_config(config: Config) -> tuple[bool, str | None, str, bool]:
    """Render sidebar configuration and return click state."""
    with st.sidebar:
        st.header("⚙️ Configuration")

        st.text_input(
            "Project Path",
            value=str(config.tests_path),
            disabled=True,
            key="project_path",
        )

        keyword = st.text_input(
            "Keyword (optional)",
            placeholder="e.g. login or test_home or math*",
        )

        run = st.button(
            "Run Tests",
            type="primary",
            icon=":material/play_arrow:",
        )

        use_cache = st.toggle(
            "Use Cache",
            value=True,
        )

    return run, st.session_state.get("project_path"), keyword, use_cache


def metrics_panel(df: pd.DataFrame):
    """Pretty top metrics."""
    passed = len(df[df["outcome"] == "passed"])
    failed = len(df[df["outcome"] == "failed"])
    total = len(df)

    c1, c2, c3 = st.columns(3)

    def box(text, bg):
        st.markdown(
            f"""
            <div style="
                background:{bg};
                padding:14px;
                border-radius:12px;
                text-align:center;
                font-size:20px;
                font-weight:600;
                ">
                {text}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c1:
        box(f"🟢 Passed: {passed}", "#d4f6d4")

    with c2:
        box(f"🟡 Failed: {failed}", "#fff3c4")

    with c3:
        box(f"📦 Total: {total}", "#e8e8e8")

    st.divider()


def results_table(df: pd.DataFrame):
    """Group tests by file and show expandable sections with filtering."""
    st.subheader("📂 Test Groups")

    # Search input
    search = st.text_input("🔍 Search test name / file")
    if search:
        df = df[
            df["name"].str.contains(search, case=False)
            | df["nodeid"].str.contains(search, case=False)
        ].copy()

    # Replace status for UI
    df["nodeid"] = df["nodeid"].astype(str).str.split("::").str[0]
    df["status_emoji"] = df["outcome"].map(
        {
            "passed": "🟢",
            "failed": "🟡",
            "skipped": "⏭️",
        }
    )

    grouped = df.groupby("nodeid")

    for group_name, group in grouped:
        total = len(group)
        failed = len(group[group["outcome"] == "failed"])
        passed = len(group[group["outcome"] == "passed"])

        badge = "🟢" if failed == 0 else "🟡"

        with st.expander(
            f"{badge} {group_name}  ({passed}/{total})",
            expanded=False,
        ):
            # Style dataframe
            st.dataframe(
                group[["name", "status_emoji", "duration", "message"]].rename(
                    columns={
                        "status_emoji": "Status",
                        "duration": "Duration (s)",
                    }
                )
            )


def logs_panel(df: pd.DataFrame, full_output: str):
    """Bottom logs tab system."""
    st.subheader("📝 Logs")

    tab1, tab2 = st.tabs(["🔹 Test-specific Log", "📣 Full Pytest Output"])

    with tab1:
        if df.empty:
            st.info("No test results to display logs for.")
        else:
            selected = st.selectbox("Select a test:", df["name"])
            test = df[df["name"] == selected].iloc[0]
            st.code(test["message"] or "No log available.", language="bash")

    with tab2:
        st.code(
            full_output or "No output.",
            language="bash",
            line_numbers=True,
        )


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

if __name__ == "__main__":
    st.set_page_config(
        page_title="Pytest UI",
        layout="centered",
        page_icon=files("pytest_ui").joinpath("assets/pytest_faviconV2.png"),
    )

    # Persistent flag
    if "has_run" not in st.session_state:
        st.session_state.has_run = False

    st.logo(files("pytest_ui").joinpath("assets/pytest_faviconV2.png"))
    st.title(":material/experiment: Pytest UI")

    config = _configure()

    if config.tests_path.is_dir():
        test_files_inside = [
            f
            for f in config.tests_path.rglob("*")
            if f.is_file() and f.name.startswith("test_") and f.suffix == ".py"
        ]

        selected_tests = {k.name: False for k in test_files_inside}
        st.subheader("🧪 Select Test Files to Run")

        c1, c2 = st.columns(2)
        for i, f in enumerate(test_files_inside):
            with c1 if i % 2 == 0 else c2:
                selected_tests[f.name] = st.checkbox(
                    f.relative_to(config.tests_path).as_posix(),
                    value=False,
                )

    _can_run = any(v for v in selected_tests.values())

    if st.button(
        "LET'S TEST! 🚀",
        type="primary",
        icon=":material/play_arrow:",
        width="stretch",
        disabled=not _can_run,
        help="Select at least one test file to run." if not _can_run else None,
    ):
        st.session_state.has_run = True

    # Stop unless tests already ran
    if not st.session_state.has_run:
        st.stop()

    if all(not v for v in selected_tests.values()):
        st.warning("Please select at least one test file to run.")
        st.stop()

    to_run = [
        str(config.tests_path.joinpath(name))
        for name, selected in selected_tests.items()
        if selected
    ]

    progress_bar = st.progress(0.0, text="Running tests...")

    results = []
    output = ""

    for i, test_file in enumerate(to_run):
        res, out = _run_tests(test_file, None)

        if res:
            results.extend(res)

        progress_bar.progress(
            (i + 1) / len(to_run),
            text=f":material/experiment: {test_file}...",
        )

        output += out + "\n\n"

    progress_bar.empty()

    if len(results) == 0:
        st.error("Unable to run tests.")
        st.code(output, language="bash")
        st.stop()

    # Main UI
    df = pd.DataFrame([r.__dict__ for r in results])

    metrics_panel(df)
    results_table(df)
    logs_panel(df, output)
