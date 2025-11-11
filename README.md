# pytest-ui

A lightweight user interface for running and inspecting pytest test suites. Designed to simplify test discovery, execution, and result visualization for developers and teams.

## Features
- Discover pytest tests in a project tree.
- Run single tests, files, or test suites.
- Live test output and failure tracebacks.
- Filtering and grouping by markers, names, or paths.
- Exportable test run reports (HTML/JSON).
- Integrates with CI by producing machine-readable artifacts.

## Installation
Install from PyPI:
```
pip install pytest-ui
```
Or install from source:
```
git clone https://github.com/your-org/pytest-ui.git
cd pytest-ui
pip install -e .
```

## Quickstart
Run the UI for the current project:
```
pytest-ui
```
Run tests non-interactively and output a report:
```
pytest-ui --run --output report.json
```
Run a single test:
```
pytest-ui --run tests/test_example.py::test_function
```

## Configuration
Create a `pytest-ui.yml` at the project root to customize behavior:
```yaml
ui:
    port: 8080
    host: 127.0.0.1
runner:
    timeout: 300
    parallel: 4
report:
    format: html
    path: reports/latest.html
```
CLI flags override config file settings.

## Usage Notes
- The UI leverages the local pytest installation; project virtualenv is recommended.
- For large suites, enable parallel execution in config to reduce runtime.
- Use markers and naming conventions to improve filtering and navigation.

## Development
Run the test suite:
```
pytest
```
Run linters and type checks:
```
flake8
mypy
```
Build a source distribution:
```
python -m build
```

## Contributing
Contributions are welcome. Suggested workflow:
- Fork the repository.
- Create a feature branch.
- Open a pull request with a clear description and tests.
Follow the repository's coding style and include tests for new behavior.

Please read CONTRIBUTING.md and CODE_OF_CONDUCT.md for more details (create them if they do not exist).

## License
MIT License — see LICENSE file.

## Acknowledgements
Built on top of pytest and inspired by developer UX improvements for local test iteration and debugging.
