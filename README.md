# pytest-ui

## Screenshots
<img alt="image" src="https://github.com/user-attachments/assets/6480ab87-3b8c-43c0-879f-6c03b220c692" />
<img alt="image" src="https://github.com/user-attachments/assets/fb2f9dd8-aa9d-417d-b628-8188d4473c49" />


A lightweight user interface for running and inspecting pytest test suites. Designed to simplify test discovery, execution, and result visualization for developers and teams.

## Features
- [x] Discover pytest tests in a project.
- [x] Run all tests inside a tests folder.
- [ ] Run a single test file.

## Installation
Install directly from GitHub repository using pip :
```bash
pip install git+https://github.com/AndoniainaNantenaina/pytest-ui.git
```

## Quickstart
Run the UI for the current project:
```
pytest-ui --path /your/test/folder
```
Then open http://localhost:8585 to see the UI.

## Usage Notes
- The UI leverages the local pytest installation; project virtualenv is recommended.
- Use markers and naming conventions to improve filtering and navigation.

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
Built on top of [pytest](https://pypi.org/project/pytest/) and [pytest-json-report](https://pypi.org/project/pytest-json-report/) and inspired by developer, UX improvements for local test iteration and debugging.
