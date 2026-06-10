# Changelog

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
