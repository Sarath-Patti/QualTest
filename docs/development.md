# QualTest Developer Guide & Engineering Standards

Welcome to the **QualTest** developer guide. This document outlines development environment setup, code style guidelines, static analysis tools, testing procedures, and Continuous Integration (CI) standards.

---

## 1. Environment Setup

### Prerequisites
- **Python 3.10+**
- **Git**

### Virtual Environment Setup
It is strongly recommended to use an isolated Python virtual environment:

```bash
# Create a virtual environment
python3 -m venv .venv

# Activate the virtual environment
# On macOS / Linux:
source .venv/bin/activate

# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
```

### Dependency Installation
Install runtime and development dependencies:

```bash
# Upgrade pip
pip install --upgrade pip

# Install runtime dependencies
pip install -r requirements.txt

# Install development & engineering quality dependencies
pip install -r requirements-dev.txt
```

---

## 2. Pre-Commit Hooks Setup

Configure automated pre-commit git hooks to enforce code quality before commits:

```bash
pre-commit install
```

To run pre-commit manually across all files:

```bash
pre-commit run --all-files
```

---

## 3. Code Quality Tooling & Standards

QualTest uses centralized configuration in `pyproject.toml` for code formatting, linting, and type checking.

### Code Formatting (Black)
Black enforces consistent Python code formatting with an 88-character line length limit.

```bash
# Check formatting without modifying files
black --check .

# Auto-format all Python source files
black .
```

### Code Linting & Style (Ruff)
Ruff enforces PEP 8 compliance, import sorting (`isort`), code complexity limits (`mccabe`), and bug checks.

```bash
# Inspect codebase for linting warnings/errors
ruff check .

# Automatically fix supported linting issues
ruff check --fix .
```

### Static Type Checking (MyPy)
MyPy enforces strict type annotations across framework modules.

```bash
mypy framework network run.py
```

---

## 4. Testing Infrastructure & Coverage

### Running Tests (Pytest)
Pytest discovers and executes unit and integration test suites in the `tests/` directory:

```bash
# Run all unit tests
pytest
```

### Test Coverage (Coverage.py)
Measure code coverage and generate HTML reports:

```bash
# Run pytest with code coverage analysis
pytest --cov=framework --cov=network --cov-report=html:htmlcov --cov-report=term-missing
```

The HTML coverage report will be saved to `htmlcov/index.html`.

---

## 5. Continuous Integration (CI) Overview

QualTest uses **GitHub Actions** (`.github/workflows/ci.yml`) to automatically validate every push and pull request against Python 3.10, 3.11, and 3.12 matrix targets:

1. **Linting Check**: Executes `ruff check .`
2. **Formatting Check**: Executes `black --check .`
3. **Type Checking**: Executes `mypy framework network run.py`
4. **Test Suite & Coverage**: Executes `pytest --cov=framework --cov=network`
