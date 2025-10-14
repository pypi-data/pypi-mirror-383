# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [2.1.0] - 2025-10-13

### Changed
- `scripts.build` now calls `sync_metadata_module()` before invoking `python -m build`, ensuring wheels and sdists ship freshly generated metadata.
- Added an explicit CLI test covering the `--version` flag so console-script aliases stay aligned with generated constants.
- Updated README, INSTALL instructions, and the Quickstart notebook to document `lib-cli-exit-tools` as the canonical console entry point alongside its aliases.

## [2.0.0] - 2025-10-12

### Changed
- Modernised runtime and automation tooling to rely on native Python 3.13 APIs, including updated signal adapters and simplified exception rendering.
- Raised development dependency floors (codecov-cli, import-linter, bandit, pip-audit, pyright, pytest, pytest-asyncio, ruff, textual) to the latest stable releases.
- Refined documentation to reflect the current behaviour-focused test suite and active automation scripts.
- Brought script modules and metadata fallbacks back into coverage reporting and removed ad-hoc sys.path manipulation from the automation launcher.
- Adopted PEP 604 union typing throughout the CLI runner and facade helpers to underline the Python 3.13-only baseline and to keep function signatures declarative.
- Updated packaging metadata to require `build>=1.3.0`, `pytest-cov>=7.0.0`, `twine>=6.2.0`, and `hatchling>=1.27.0`, matching the latest stable releases verified via `pip index`.
- Restored real signal integration coverage and Hypothesis-backed exit-code property tests to guard regression-prone paths.

### Removed
- Retired Conda/Homebrew/Nix packaging automation and updated documentation to reflect the PyPI-only distribution path.
- Dropped legacy ImportError-based script fallbacks now that automation entry points run as a proper package.

### Documentation
- Highlighted the Python 3.13 baseline, dependency refresh, and updated CI action set in the README.
- Documented the revived signal integration suite and property-based tests in the system module reference.


## [1.6.0] - 2025-10-08

### Added
- Property-based (Hypothesis) tests covering `SystemExit` payload handling and configurable broken-pipe exit codes.
- POSIX integration test that drives a subprocess through a SIGINT to assert real signal handling behaviour.

### Changed
- Local `make test` runs skip packaging-sync enforcement unless running in CI or with `ENFORCE_PACKAGING_SYNC=1`, reducing friction for contributors.
- CLI rich-click styling now preserves coloured tracebacks when stderr supports UTF/TTY output even if stdout is piped.
- Centralised public API exports so `lib_cli_exit_tools` and its facade share a single authoritative symbol list.

### Security
- Suppress pip-audit false positive for GHSA-4xh5-x5gv-qwph until an official fixed pip build is published.

## [1.5.0] - 2025-10-08

### Added
- Configuration helpers `config_overrides` and `reset_config` so embedders can
  safely tweak and restore global CLI settings without bespoke fixtures.
- Expanded OS-aware test coverage (sysexits mappings, signal restoration, CLI
  behaviours) and rewritten specs that no longer rely on private helpers.
- CI job that executes the Quickstart notebook on Python 3.13 and validations that ensure packaging metadata stays in sync at tag time.
- Automation that keeps Conda, Homebrew, and Nix specs aligned with `pyproject.toml`, including a dedicated `--sync-packaging` mode.
- Regression tests covering `SystemExit` variants, tolerant output rendering, English signal messages, and ValueError mappings on Windows.

### Changed
- Hardened `get_system_exit_code` handling for non-integer payloads and switched OS detection to `os.name`.
- Updated `_print_output` to decode both `bytes` and `str`, trimming assertions in favour of resilient diagnostics.
- Standardised signal messages (“Aborted (SIGINT).”, etc.) and cached metadata lookups in `__init__conf__`.
- Enforced an 85% coverage threshold (in line with `pyproject.toml` and Codecov settings) and removed spurious coverage pragmas to reflect the new test suite.
- Repartitioned the library into `core`, `adapters`, and `application` layers with `lib_cli_exit_tools` acting as the facade.
- `run_cli` now accepts injectable `exception_handler` and `signal_installer` hooks, and rich-click configuration is applied lazily from `main()`.

### Fixed
- Restored Pyright compatibility by typing metadata helpers against a minimal protocol.
- Removed a Ruff F401 false positive on the Quickstart notebook via per-file ignore.

### Documentation
- Expanded the README with packaging sync guidance and notebook usage notes.
- Clarified release steps in CONTRIBUTING and refreshed developer docs.

## [1.4.0] - 2025-09-26

### Changed
- Refactored packaging automation and broadened the pytest suite to cover new CLI flows.

## [1.3.1] - 2025-09-26

### Fixed
- Adjusted coloured traceback behaviour to address regressions introduced in 1.3.0.

## [1.3.0] - 2025-09-25

### Added
- Introduced Rich-powered traceback rendering for CLI failures.

## [1.2.0] - 2025-09-25

### Changed
- Switched the CLI stack to rich-click and delivered associated fixes.

## [1.1.1] - 2025-09-18

### Added
- Documentation and doctest updates for newly exposed helpers.

## [1.1.0] - 2025-09-16

### Added
- `lib_cli_exit_tools.run_cli` helper to reduce Click boilerplate (see `cli.py`).

## [1.0.3] - 2025-09-16

### Added
- `make menu` target for the Textual-powered maintenance UI.

## [1.0.2] - 2025-09-15

### Changed
- Miscellaneous internal improvements.

## [1.0.1] - 2025-09-15

### Changed
- Miscellaneous internal improvements.

## [1.0.0] - 2025-09-15

### Added
- Initial public release.

## [0.1.1] - 2025-09-15

### Added
- Placeholder for early internal work.

## [0.1.0] - 2025-09-14

### Added
- Unified package naming, tightened public API exports, and added tests for exit-code mapping and CLI behaviour.

## [0.0.1] - 2025-09-13

### Added
- Initial internal release.
