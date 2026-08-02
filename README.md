# QualTest

**Wireless Modem Validation & Test Automation Framework**

QualTest is a modular, high-performance test automation framework designed for validating wireless modem hardware, firmware, and protocol stack implementations.

---

## Current Milestone: v0.8 – Engineering Quality

The goal of milestone **v0.8** is to establish production-grade engineering quality standards by integrating code quality tooling, static type checking, automated test infrastructure, pre-commit hooks, GitHub Actions CI, and developer documentation.

### Features Implemented in v0.8:
- **Centralized Tool Configuration**: `pyproject.toml` configuration for Black, Ruff, MyPy, Pytest, and Coverage.
- **Development Dependencies**: `requirements-dev.txt` specifying tooling dependencies (`black`, `ruff`, `mypy`, `pytest`, `pytest-cov`, `pre-commit`).
- **Code Formatting & Linting**: Configuration for Black (88 char line-length) and Ruff (PEP 8, import sorting, complexity checks).
- **Static Type Checking**: MyPy type-checking configuration (`mypy framework network run.py`).
- **Testing & Coverage Infrastructure**: `pytest.ini` and coverage configuration with HTML output (`htmlcov/`).
- **Pre-Commit Integration**: `.pre-commit-config.yaml` specifying Black, Ruff, MyPy, YAML, and file hygiene hooks.
- **Continuous Integration (CI)**: GitHub Actions workflow (`.github/workflows/ci.yml`) triggering on pushes and pull requests across Python 3.10-3.12 targets.
- **Developer Documentation**: Dedicated guide in `docs/development.md`.

---

## Code Quality & Development Environment

QualTest enforces high project standards through automated tooling:

| Tool | Purpose | Command | Configuration |
| :--- | :--- | :--- | :--- |
| **Black** | Code Formatter | `black --check .` | `pyproject.toml` |
| **Ruff** | Linter & Import Sorter | `ruff check .` | `pyproject.toml` |
| **MyPy** | Static Type Checker | `mypy framework network run.py` | `pyproject.toml` |
| **Pytest** | Test Runner | `pytest` | `pytest.ini` / `pyproject.toml` |
| **Coverage** | Code Coverage Engine | `pytest --cov=framework --cov-report=html` | `pyproject.toml` |
| **Pre-Commit** | Git Hook Manager | `pre-commit run --all-files` | `.pre-commit-config.yaml` |

---

## Development Setup & Developer Guide

Refer to [docs/development.md](file:///Users/sarathpatti/Documents/QualTest/docs/development.md) for full developer environment setup and contribution procedures.

### Quick Start for Developers
```bash
# Set up virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

# Configure pre-commit git hooks
pre-commit install

# Run static analysis & tests
ruff check .
black --check .
mypy framework network run.py
pytest
```

---

## Continuous Integration (CI)

GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every `push` and `pull_request` to `main`:
1. **Linting Check**: `ruff check .`
2. **Format Check**: `black --check .`
3. **Type Check**: `mypy framework network run.py`
4. **Unit Tests & Coverage**: `pytest --cov=framework --cov=network`

---

## CLI Usage

### Run All Testcases Concurrently & Generate Reports
```bash
python run.py --run-all testcases/ --report
```

### Run Single Testcase & Generate Reports
```bash
python run.py --run testcases/attach_success.json --report
```

### Start Modem Network Simulator with Failure Injection
```bash
python run.py --simulator tcp --failure-config config/failure.json
```

---

## Development Roadmap

- [x] **v0.1 – Project Foundation**: Directory structure, configuration system, logging subsystem, CLI entry point, public module interfaces.
- [x] **v0.2 – JSON Test Runner**: JSON loader, schema validation, exception hierarchy, data models, sample testcases, CLI integration.
- [x] **v0.3 – Network Simulator**: TCP/UDP simulator servers, modem event engine, latency simulation, sample client, CLI integration.
- [x] **v0.4 – Validation Engine**: Step validation engine, latency measurement, validation state Enums, execution summary, CLI execution support.
- [x] **v0.5 – Failure Injection Engine**: Configurable failure injector, simulated network anomalies, CLI failure config support.
- [x] **v0.6 – Concurrent Test Scheduler**: ThreadPoolExecutor scheduler, parallel batch testcase execution, scheduler lifecycle, thread-safe result aggregation.
- [x] **v0.7 – Reporting & Metrics**: HTML and CSV report generation (`reports/report.html`, `reports/report.csv`), metrics calculation engine, CLI `--report` integration.
- [x] **v0.8 – Engineering Quality**: `pyproject.toml` centralized tool config, `requirements-dev.txt`, Black, Ruff, MyPy, Pytest, Coverage, Pre-commit hooks, GitHub Actions CI workflow, developer guide (`docs/development.md`).
