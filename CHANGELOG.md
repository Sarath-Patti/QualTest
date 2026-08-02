# Changelog

All notable changes to the **QualTest** (Wireless Modem Validation & Test Automation Framework) project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-08-02

### Added
- **v1.0 Production Release & Repository Polish**: Complete engineering documentation, architecture diagrams, protocol stack specifications, community guidelines, GitHub issue/PR templates, and release notes.
- Subsystem documentation in `docs/architecture.md`, `docs/protocol-stack.md`, `docs/developer-guide.md`, and `docs/community.md`.
- GitHub issue templates (`bug_report.md`, `feature_request.md`) and pull request template (`PULL_REQUEST_TEMPLATE.md`).
- Expanded sample testcase configurations in `testcases/examples/` (LTE Attach, Detach, Handover, Failure Injection).
- Sample execution report templates in `reports/examples/`.
- Official v1.0.0 release notes in `docs/releases/v1.0.md`.

---

## [0.9.0] - 2026-08-02

### Added
- **v0.9 Protocol Log Replay & Analysis Engine**: Offline protocol log parser supporting JSON, CSV, and Plain Text log formats.
- **LTE/5G Protocol Messages**: Enumerations for RRC (`RRC_CONNECTION_REQUEST`, `RRC_CONNECTION_SETUP`, `RRC_CONNECTION_SETUP_COMPLETE`), NAS (`NAS_ATTACH_REQUEST`, `NAS_ATTACH_ACCEPT`, `NAS_AUTH_REQUEST`, `NAS_AUTH_ACCEPT`), Mobility (`SERVICE_REQUEST`, `SERVICE_ACCEPT`, `HANDOVER_REQUEST`, `HANDOVER_COMPLETE`), and Detach signaling.
- **Modem Finite State Machine (`ModemFSM`)**: State reconstruction across `IDLE`, `RRC_CONNECTING`, `CONNECTED`, `REGISTERED`, `IN_SERVICE`, `HANDOVER`, `DETACHED`, and `ERROR` states.
- **Protocol Signaling Analyzer**: Anomaly detection engine (`MISSING_MESSAGE`, `DUPLICATE_MESSAGE`, `INVALID_TRANSITION`, `UNEXPECTED_DETACH`, `AUTHENTICATION_FAILURE`, `OUT_OF_ORDER_SIGNALING`, `UNKNOWN_MESSAGE`).
- **Ordered Timeline Generator**: Timeline generation tracking timestamp, message, previous state, current state, and validation status.
- **Replay Metrics Engine**: Calculation of attach, registration, and handover procedure durations, message counts, and completion percentage.
- **CLI Integration**: Offline log replay execution via `python run.py --replay <log_file_path>`.
- **Sample Signaling Logs**: Realistic LTE/5G log files in `logs/samples/`.

---

## [0.8.1] - 2026-08-02

### Fixed
- **Engineering Quality Improvements**: Fixed static analysis violations, type annotations, and import sorting across all modules.
- Refactored `Settings` singleton to eliminate global state statements (`PLW0603`).
- Decoupled network package initialization to prevent eager server imports and resolve circular dependency import errors in Pytest collection.
- Optimized `run.py` CLI option handling to reduce cyclomatic complexity.

---

## [0.8.0] - 2026-08-02

### Added
- **Engineering Quality Infrastructure**: Centralized tool configuration in `pyproject.toml` for Black, Ruff, MyPy, Pytest, and Coverage.
- Added `requirements-dev.txt` for developer environment tooling.
- Configured `.pre-commit-config.yaml` for pre-commit git hooks.
- Configured GitHub Actions CI workflow in `.github/workflows/ci.yml`.
- Developer setup guide in `docs/development.md`.

---

## [0.7.0] - 2026-08-02

### Added
- **Reporting & Metrics Engine**: Modular report generator in `framework/reporter/`.
- Automated generation of HTML (`reports/report.html`) and CSV (`reports/report.csv`) reports.
- Execution metrics calculation: pass rates, total duration, minimum/maximum/average command latencies.
- CLI integration via `--report` flag.

---

## [0.6.0] - 2026-08-02

### Added
- **Concurrent Test Scheduler**: Parallel testcase execution engine in `framework/scheduler/`.
- ThreadPoolExecutor worker thread management for batch testcase execution.
- Thread-safe result aggregation (`SchedulerSummary`, `ExecutionResult`).
- CLI integration via `--run-all <directory>`.

---

## [0.5.0] - 2026-08-02

### Added
- **Failure Injection Engine**: Configurable failure injector in `framework/simulator/failure_injector.py`.
- Support for packet loss, response timeout, socket disconnect, malformed response payload, and response delay injection.
- CLI integration via `--failure-config <config_file>`.

---

## [0.4.0] - 2026-08-02

### Added
- **Validation Engine**: Step validation engine in `framework/validator/engine.py`.
- Latency measurement using high-resolution performance counters (`time.perf_counter`).
- Structured validation status (`PASS`, `FAIL`, `TIMEOUT`, `ERROR`, `UNKNOWN`).
- CLI integration via `python run.py --run <testcase_file>`.

---

## [0.3.0] - 2026-08-02

### Added
- **Modem Network Simulator**: Multi-protocol TCP and UDP server implementations in `network/tcp/` and `network/udp/`.
- Protocol-agnostic unified simulator manager in `framework/simulator/network_simulator.py`.
- Command processing and automated modem response matching.
- CLI integration via `python run.py --simulator tcp|udp`.

---

## [0.2.0] - 2026-08-02

### Added
- **JSON Testcase Runner**: JSON testcase parser and schema validator in `framework/parser/`.
- Schema error handling and exception hierarchy (`TestCaseError`).
- Immutable data models (`TestCase`, `TestStep`).
- CLI integration via `python run.py --test <testcase_file>`.

---

## [0.1.0] - 2026-08-02

### Added
- **Project Foundation**: Initial repository structure, immutable configuration system (`Settings`), centralized logger subsystem (`setup_logger`), and CLI entry point (`run.py`).
