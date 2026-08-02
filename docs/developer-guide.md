# Developer Environment & Contribution Guide

This guide describes environment configuration, quality assurance standards, local testing, and developer workflows for **QualTest v1.0**.

---

## 1. Local Environment Setup

### Prerequisites
- Python 3.10, 3.11, or 3.12
- Git

### Virtual Environment Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
pre-commit install
```

---

## 2. Code Quality Assurance

QualTest enforces mandatory quality gates on all code:

### Formatting (`Black`)
```bash
black --check .
# Auto-format:
black .
```

### Linting & Import Sorting (`Ruff`)
```bash
ruff check .
# Auto-fix fixable issues:
ruff check . --fix
```

### Type Checking (`MyPy`)
```bash
mypy framework network run.py
```

### Unit Tests & Coverage (`Pytest`)
```bash
pytest
# Run with coverage report:
pytest --cov=framework --cov=network --cov-report=html
```

---

## 3. GitHub Actions CI Pipeline

The CI workflow `.github/workflows/ci.yml` runs on every push and pull request:
1. Installs dependencies (`requirements.txt` + `requirements-dev.txt`).
2. Checks code formatting via `black --check .`.
3. Runs linter via `ruff check .`.
4. Validates static typing via `mypy framework network run.py`.
5. Executes full unit test suite with coverage reporting via `pytest --cov=framework --cov=network`.
