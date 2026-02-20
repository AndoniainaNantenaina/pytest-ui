# GitHub Copilot Instructions for pytest-ui

## Project Overview
pytest-ui is a lightweight user interface for running and inspecting pytest test suites. It provides a Streamlit-based web interface for test discovery, execution, and result visualization.

## Tech Stack
- **Language**: Python 3.10+
- **Web Framework**: Streamlit (≥1.40.0)
- **Testing**: pytest (≥9.0.0), pytest-json-report (≥1.5.0)
- **CLI**: Click (≥8.0.0)
- **Data Processing**: pandas (≥2.0.0), plotly (≥6.4.0)
- **Package Manager**: uv (recommended for development)

## Code Style & Conventions

### General Python Guidelines
- Follow PEP 8 style guidelines
- Use snake_case for functions, variables, and module names
- Use PascalCase for class names
- Prefix private functions and methods with underscore (`_function_name`)
- Maximum line length: 88 characters (Black formatter compatible)

### Type Hints
- **Always use type hints** for function parameters and return values
- Import from `typing` module when needed (List, Optional, etc.)
- Use modern type hint syntax where possible:
  ```python
  # Preferred
  def example(path: Path | str) -> list[TestResult]:
  
  # Legacy (use only if Python < 3.10)
  from typing import List, Union
  def example(path: Union[Path, str]) -> List[TestResult]:
  ```

### Data Structures
- Use `@dataclass` from the `dataclasses` module for data containers
- Example:
  ```python
  from dataclasses import dataclass
  
  @dataclass
  class TestResult:
      nodeid: str
      outcome: str
      duration: float
  ```

### Path Handling
- **Always use `pathlib.Path`** for file system operations
- Never use string concatenation for paths
- Use `.resolve()` to get absolute paths
- Example:
  ```python
  from pathlib import Path
  
  project_path = Path(path).resolve()
  report_file = project_path / "report.json"
  ```

### Subprocess and External Commands
- Use `subprocess.run()` for executing external commands
- Set `capture_output=True, text=True` for text output
- Always handle process return codes and errors
- Example from runner.py:
  ```python
  process = subprocess.run(
      cmd,
      capture_output=True,
      text=True,
      cwd=self.project_path.parent.parent,
  )
  ```

### Error Handling
- Use specific exception types (e.g., `FileNotFoundError`)
- Provide clear, actionable error messages
- Handle JSON parsing errors when reading pytest reports

## Project Structure

```
pytest_ui/
├── __init__.py           # Package initialization
├── cli.py                # CLI entry point using Click
├── app.py                # Main Streamlit application
├── runner.py             # Pytest test execution logic
├── parser.py             # Parse pytest JSON reports
├── assets/               # Images and visual assets
└── static/               # Static files (fonts, licenses)
```

## Key Components

### CLI (`cli.py`)
- Entry point: `main()` function decorated with `@click.command()`
- Options: `--port` (default: 8585), `--path` (default: ".")
- Launches Streamlit app via subprocess
- Uses ASCII art banner for branding

### Streamlit App (`app.py`)
- Main UI implementation
- Uses `@st.cache_data` for caching test results
- Session state management for persistence
- Receives project path from CLI via sys.argv

### Test Runner (`runner.py`)
- `PytestRunner` class handles test execution
- Generates JSON reports using pytest-json-report plugin
- Stores reports in temporary directory (`/tmp/pytest_ui/`)
- Returns dict with stdout, stderr, exit_code, and parsed report

### Report Parser (`parser.py`)
- Converts pytest JSON reports to `TestResult` dataclass instances
- Extracts: nodeid, name, outcome, duration, message, file

## Development Workflow

### Adding New Features
1. Add implementation in appropriate module (runner, parser, app)
2. Update type hints and docstrings
3. Consider adding tests in `tests/` directory
4. Update README.md if user-facing feature

### Streamlit-Specific Guidelines
- Use Streamlit caching decorators (`@st.cache_data`) for expensive operations
- Store state in `st.session_state` for persistence across reruns
- Use Streamlit components: `st.selectbox`, `st.button`, `st.dataframe`, etc.
- Organize UI with columns: `st.columns()` for layout

### Testing
- Write pytest tests in the `tests/` directory
- Test files should be named `test_*.py`
- Use meaningful test names that describe what is being tested

## Common Patterns

### Reading Project Configuration
```python
from importlib.resources import files

config_dir = files("pytest_ui").joinpath(".streamlit")
```

### Running External Commands
```python
import subprocess

process = subprocess.run(
    ["pytest", "-vv", "--json-report"],
    capture_output=True,
    text=True,
)
```

### Streamlit Caching
```python
@st.cache_data(show_spinner=False)
def _run_tests(tests_path: Path | str, keyword: Optional[str] = None):
    # Expensive operation
    pass
```

## Dependencies Management
- Use `pyproject.toml` for dependency declarations
- Add new dependencies under `[project.dependencies]`
- Include version constraints (e.g., `"streamlit>=1.40.0"`)
- Static resources must be declared in `[tool.setuptools.package-data]`

## Localization Notes
- Some error messages may be in French (legacy code in runner.py)
- When adding new user-facing text, prefer English for consistency
- Consider extracting strings for future i18n support

## Common Tasks

### Adding a New CLI Option
1. Add `@click.option` decorator in `cli.py`
2. Pass parameter to Streamlit via command line arguments
3. Update `app.py` to read the parameter from sys.argv

### Adding New Test Filters
1. Modify pytest command in `runner.py` to add flags
2. Update parser if new fields are needed in JSON report
3. Add UI controls in `app.py` for user interaction

### Adding Visualizations
1. Use plotly for charts (`import plotly.express as px`)
2. Use pandas DataFrames for tabular data
3. Display with `st.plotly_chart()` or `st.dataframe()`

## Best Practices
- Keep functions small and focused (single responsibility)
- Use descriptive variable names
- Add docstrings to functions and classes
- Validate user inputs and paths
- Use context managers for file operations
- Avoid hardcoded paths; make them configurable
- Cache expensive operations (test runs, data processing)

## Security Considerations
- Never execute arbitrary code from user input
- Validate and sanitize file paths
- Be cautious with subprocess execution
- Don't expose internal file system structure in UI

## Performance Tips
- Cache test results to avoid re-running tests unnecessarily
- Use `@st.cache_data` for data transformations
- Limit DataFrame sizes displayed in UI
- Consider pagination for large test suites

## Resources
- [Streamlit Documentation](https://docs.streamlit.io/)
- [pytest Documentation](https://docs.pytest.org/)
- [Click Documentation](https://click.palletsprojects.com/)
- [pytest-json-report Plugin](https://pypi.org/project/pytest-json-report/)
