# Changelog

## [0.7.0] - 2026-07-01

### Added
- Added `rt explain` command (and corresponding web UI modal with Summary / Deep Analysis / Action Plan modes) powered by a new `ExplainTaskUseCase` and Ollama LLM integration
- Added `get_task` method to `TaskRepository` (and SQLite implementation) for fetching a single task by ID
- Added `all` extra in `pyproject.toml` to install web + completion dependencies together
- Added test coverage for `ExplainTaskUseCase` factory wiring, the new `Settings.resolve_db_path` / `data_dir` behavior, and the FastAPI app's index route, static mount, and router registration (including the new `explain` route)

### Changed
- Refactored `Settings`: replaced `db_path` property and private `_resolve_data_dir` with a public `resolve_data_dir()` helper, a `data_dir` property that now creates the directory on access, and a new `resolve_db_path()` method for resolving relative/absolute DB paths
- `AppContainer` and `sqlite_connection_factory` now work with a resolved `Path` instead of a raw db name string, with path resolution centralized in `Settings`
- Reorganized web static assets into `static/css/`, `static/js/`, and `static/img/` subfolders
- Replaced `ui.py`'s `render_index_html()` with direct `FileResponse` serving of `templates/index.html`, returning a 500 error if the template file is missing
- Reworked test suites for settings/connection (`TestDefaultDataDir` → `TestSettings`) and the web app (`test_app.py`) to match the new `Settings`-based path resolution and file-based index serving
- Bumped `fastapi` to 0.138.2 and `raztint` to 0.8.2

### Removed
- Removed `tests/presentation/web/test_ui.py` along with the deleted `ui.py` module
- Removed standalone `default_data_dir()` function and its tests (folded into `Settings`)
- 
---

## [0.6.1] - 2026-06-27

### Added

* Added additional test coverage for the web layer

### Changed

* Improved project documentation and expanded README clarity
* Refactored and cleaned up `pyproject.toml` structure and formatting
* Updated project description metadata in `pyproject.toml`

---

## [0.6.0] - 2026-06-25

### Added

* Added `--clear-priority`, `--clear-due`, `--clear-tags`, and `--clear-project` flags to the `rt update` command for explicitly removing optional fields from a task

### Changed

* Redesigned the web UI with a side panel layout for inline task editing, keeping the task list visible while editing
* Split `ui.py` into separate static files: `static/style.css`, `static/app.js`, and `templates/index.html`, served via FastAPI `StaticFiles`
* Migrated `ruff` and `ty` configuration out of `pyproject.toml` into dedicated `ruff.toml` and `ty.toml` files
* Added `infrastructure/version.py` as the single source of truth for the package version across CLI and web
* Updated README and `pyproject.toml` metadata

### Fixed

* Fixed `None` values sent from the web UI not clearing optional fields (`due_date`, `project`, `priority`, `tags`) on task update
* Fixed a bug where `typing_extensions` was not installed on fresh installs
* Fixed an infinite loop caused by `renderTasks` being called recursively instead of `renderTask` in the task list renderer
* Fixed `edit-panel` not closing after a successful save in the web UI

---

## [0.5.1] - 2026-06-10

### Fixed
- Corrected dependency classification by ensuring FastAPI is only included in the optional web extra and not in core runtime dependencies

---

## [0.5.0] - 2026-06-10

### Added
- Added an optional FastAPI-powered web UI, including its test suite and CLI router test coverage, contributed ([#26](https://github.com/razbuild/raztodo/pull/26) by [@Lee123-hub33](https://github.com/Lee123-hub33)), available through the new `rt-web` entry point and the `raztodo[web]` extra
- Added a lightweight single-page web interface for creating, listing, searching, completing, deleting, clearing, importing, and exporting tasks
- Added a dedicated `src/raztodo/presentation/web/ui.py` module to keep the web UI HTML, CSS, and JavaScript separate from the FastAPI app wiring

### Changed
- Refactored the web app so `src/raztodo/presentation/web/app.py` focuses on FastAPI setup while UI rendering lives in a dedicated helper module
- Improved CLI router command-class resolution to support command modules with different class naming patterns more reliably
- Updated package metadata and installation options in `pyproject.toml`, including the `rt-web` script and optional `web` dependencies
- Refreshed README and docs to document the optional web UI, revised installation flows, CLI usage examples, architecture notes, configuration guidance, and testing instructions
- Updated CI to install and test with the `web` extra, keep coverage reporting in the workflow, and align the matrix with the current toolchain setup
- Regenerated `uv.lock` to reflect the current dependency graph and optional extras

### Fixed
- Fixed and clarified several CLI help strings and examples, including due date guidance, update examples, and completion installation instructions
- Improved consistency in some error/help messaging across CLI, use-case, and repository code paths

### Tests
- Expanded web route tests to cover the HTML index page and current API behavior
- Updated existing application, domain, and infrastructure tests to align with the web UI and related refactors

### Removed
- Removed repository-local issue templates, pull request template, and top-level community policy files in favor of shared RazBuild documentation/resources

---

## [0.4.1] - 2026-05-08

### Fixed
- Fixed incorrect data in examples and usage guide (tags, priority examples)
- Fixed potential log formatting issue when logging exceptions in `__main__.py`

### Added
- Added helpful cross-reference links to the usage guide for faster navigation

### Changed
- Improved container lifecycle management to ensure cleanup even on errors
- Enhanced error messages and logging consistency

---

## [0.4.0] - 2026-05-07

### Added
- Migrate to uv for dependency management and tool installation

### Fixed
- Bugs in completion_cmd and entrypoint

### Changed
- Rewrite CI/CD workflows to use uv (removed pr_test.py)
- Update documentation with uv installation instructions

---

## [0.3.0] - 2026-05-02

### Added
- CLI auto-complete feature ([#2](https://github.com/razbuild/raztodo/pull/2) by [@MaswiliK](https://github.com/MaswiliK))

### Changed
- Minimum required Python version raised to 3.10
- Replaced `mypy` with `ty` for static type checking

### Docs
- Documentation improved and updated

---

## [0.2.1] - 2025-12-27

### Fixed
- Fixed Windows APPDATA path resolution bug
- Fixed absolute database path handling in connection factory
- Fixed file permission check using resolved path instead of original path

### Docs
- Improve documentation clarity and correctness
- Fix incorrect or unclear information in documentation

---

## [0.2.0] - 2025-12-13

### Added
- New `clear tasks` command

### Changed / Refactored
- SQLite search performance significantly improved
- CLI startup time and overall performance improved
- Internal container architecture refactored (no user-facing impact)

### Docs
- README updated to reflect new features
- Documentation updated and aligned with current behavior

---

## [0.1.1] - 2025-12-11

### Added
- Dependency `raztint` added for colored messages

### Changed / Refactored
- CLI entrypoint changed from `raztodo` to `rt`
- Logger naming improved
- Type hints simplified across command modules
- CLI output improved and performance optimized

### Removed
- Obsolete and unused files removed
- Compiled Python artifacts removed from the repository

### Docs
- README updated (badges, assets, formatting)
- Demo preview improved

### CI
- CI configuration fixed
- Python 3.14 added to test matrix
