# Contributing to QualTest

Thank you for your interest in contributing to **QualTest** (Wireless Modem Validation & Test Automation Framework)! We welcome contributions from the community.

---

## 1. Development Setup

### Environment Requirements
- **Python**: Version 3.10, 3.11, or 3.12.
- **Git**: For version control.

### Setup Virtual Environment
```bash
# Clone the repository
git clone https://github.com/Sarath-Patti/QualTest.git
cd QualTest

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install development dependencies
pip install -r requirements.txt -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

---

## 2. Coding Standards & Tooling

All code must pass strict quality gates before merging:

| Gate | Command | Requirement |
| :--- | :--- | :--- |
| **Formatting** | `black --check .` | 88-char line length, Black style |
| **Linting** | `ruff check .` | Zero warnings or errors |
| **Type Checking** | `mypy framework network run.py` | Zero static type errors |
| **Unit Testing** | `pytest` | 100% test pass rate |

---

## 3. Branching & Commit Conventions

### Branch Naming
- Features: `feature/short-description` (e.g., `feature/5g-nr-messages`)
- Bug Fixes: `fix/short-description` (e.g., `fix/tcp-socket-timeout`)
- Documentation: `docs/short-description` (e.g., `docs/architecture-update`)

### Commit Messages
We follow Conventional Commits:
- `feat(scope): add feature description`
- `fix(scope): resolve issue description`
- `docs(scope): update documentation`
- `refactor(scope): internal structural improvement`

---

## 4. Pull Request Workflow

1. Fork the repository and create a new feature branch.
2. Implement changes following the architecture and style guidelines.
3. Ensure all local tests and linter commands pass:
   ```bash
   ruff check .
   black --check .
   mypy framework network run.py
   pytest
   ```
4. Submit a Pull Request targeting `main`.
5. Ensure GitHub Actions CI pipeline checks pass.
