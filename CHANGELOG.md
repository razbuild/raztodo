# Changelog

## 0.4.0 - 2026-05-07

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
