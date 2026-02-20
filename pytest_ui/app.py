import logging
import sys
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st

from pytest_ui.parser import TestResult, parse_pytest_report
from pytest_ui.runner import PytestRunner

logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# UTILITIES
# ---------------------------------------------------------


def _get_project_path_from_cli() -> Path:
    """Get project path passed after streamlit run.

    Returns:
        Path object pointing to the project directory or test file.
    """
    if len(sys.argv) > 1:
        return Path(sys.argv[1]).resolve()
    return Path(".").resolve()


def _is_test_file(path: Path) -> bool:
    """Check if the given path is a test file.

    Args:
        path: Path to check.

    Returns:
        True if path is a .py test file, False otherwise.
    """
    return (
        path.is_file()
        and path.suffix == ".py"
        and (path.name.startswith("test_") or path.name.endswith("_test.py"))
    )


@dataclass
class Config:
    """Configuration for pytest-ui application.
    
    Attributes:
        tests_path: Path to the project directory containing tests.
        keyword: Optional pytest keyword expression for filtering tests.
    """
    tests_path: Path
    keyword: Optional[str] = None


def _configure() -> Config:
    """Load configuration from CLI arguments.
    
    Returns:
        Config object with tests path and optional keyword filter.
    """
    default_path = _get_project_path_from_cli()
    return Config(tests_path=Path(default_path), keyword=None)


@st.cache_data(show_spinner=False)
def _run_tests(
    tests_path: str, keyword: Optional[str] = None
) -> tuple[list["TestResult"] | None, str]:
    """Run Pytest and return test results and output.
    
    Args:
        tests_path: String path to the project directory (must be string for caching).
        keyword: Optional pytest keyword filter.
        
    Returns:
        Tuple of (TestResult list or None if failed, output string).
    """
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
    """Render sidebar configuration and return user inputs.
    
    Args:
        config: Configuration object with project settings.
        
    Returns:
        Tuple of (run_clicked, project_path, keyword, use_cache).
    """
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Check if we're running a single test file
        is_file = _is_test_file(config.tests_path)

        if is_file:
            st.text_input(
                "Test File",
                value=config.tests_path.name,
                disabled=True,
                key="project_path",
            )
            st.caption(f"📍 {config.tests_path.parent}")
        else:
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


def metrics_panel(df: pd.DataFrame) -> None:
    """Display test result metrics in a formatted panel.
    
    Args:
        df: DataFrame containing test results.
    """
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


def results_table(df: pd.DataFrame) -> None:
    """Display tests grouped by file with filtering and expandable sections.
    
    Args:
        df: DataFrame containing test results.
    """
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


def logs_panel(df: pd.DataFrame, full_output: str) -> None:
    """Display test logs with test-specific and full output tabs.
    
    Args:
        df: DataFrame containing test results.
        full_output: Raw pytest output string.
    """
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
        layout="wide",
        page_icon=files("pytest_ui").joinpath("assets/pytest_faviconV2.png"),
    )

    # Persistent flag
    if "has_run" not in st.session_state:
        st.session_state.has_run = False

    st.logo(files("pytest_ui").joinpath("assets/pytest_faviconV2.png"))
    st.title(":material/experiment: Pytest UI")

    config = _configure()

    # Display file mode indicator
    if _is_test_file(config.tests_path):
        st.info(f"🧪 Running single test file: **{config.tests_path.name}**")

    run_clicked, project_path, keyword, use_cache = sidebar_config(config)

    if run_clicked:
        st.session_state.has_run = True

    # Stop unless tests already ran
    if not st.session_state.has_run:
        st.info("Click **Run Tests** to start.")
        st.stop()

    # Run tests
    with st.status("Running tests...", expanded=True) as status:
        if not use_cache:
            st.cache_data.clear()

        results, output = _run_tests(project_path, keyword)
        status.success("Tests completed!")

    if not results:
        st.error("Unable to run tests.")
        st.code(output, language="bash")
        st.stop()

    # Main UI
    df = pd.DataFrame([r.__dict__ for r in results])

    metrics_panel(df)
    results_table(df)
    logs_panel(df, output)
