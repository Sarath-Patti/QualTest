# QualTest v2

**Wireless Modem Validation & Test Automation Framework**

QualTest v2 is a modular, high-performance test automation framework designed for validating wireless modem hardware, firmware, and protocol stack implementations.

---

## Current Milestone: v0.1 – Project Foundation

The goal of milestone **v0.1** is to establish a clean, production-quality architectural foundation supporting future development of the automation framework.

### Features Implemented in v0.1:
- Centralized immutable configuration system supporting environment variables (`framework.config.settings`).
- Thread-safe singleton logging subsystem with console and rotating file output (`framework.logger.logger`).
- CLI entry point (`run.py`) for configuration validation, logging setup, and environment verification.
- Complete directory structure and clean public interface definitions for future framework modules.

---

## Architecture Diagram

```
                             +-----------------------+
                             |        run.py         |
                             |   (CLI Entry Point)   |
                             +-----------+-----------+
                                         |
                       +-----------------+-----------------+
                       |                                   |
           +-----------v-----------+           +-----------v-----------+
           |   framework.config    |           |   framework.logger    |
           |      (Settings)       |           |   (FrameworkLogger)   |
           +-----------+-----------+           +-----------+-----------+
                       |                                   |
       +---------------+-----------------------------------+---------------+
       |               |               |               |               |
+------v------+ +------v------+ +------v------+ +------v------+ +------v------+
|  executor   | |  scheduler  | |  validator  | |  simulator  | |   parser    |
| (Interface) | | (Interface) | | (Interface) | | (Interface) | | (Interface) |
+-------------+ +-------------+ +-------------+ +-------------+ +-------------+
       |               |               |               |               |
+------v------+ +------v------+ +---------------------------------------------+
|  reporter   | |    utils    | |               network                       |
| (Interface) | |  (Helpers)  | |        (tcp / udp Interfaces)               |
+-------------+ +-------------+ +---------------------------------------------+
```

---

## Directory Structure

```
QualTest-v2/
│
├── framework/
│   ├── executor/        # Test suite execution interface
│   ├── scheduler/       # Test job scheduling & queue interface
│   ├── validator/       # Response validation & rule checking interface
│   ├── simulator/       # Wireless modem emulation interface
│   ├── logger/          # Singleton thread-safe logging subsystem
│   ├── parser/          # Log and configuration parsing interface
│   ├── reporter/        # Execution report generation interface
│   ├── config/          # Centralized configuration & settings
│   └── utils/           # Helper utilities
│
├── network/             # Modem network communication protocols
│   ├── tcp/             # TCP socket client interface
│   └── udp/             # UDP datagram client interface
│
├── testcases/           # Test case definitions directory
├── logs/                # Execution logs directory
├── reports/             # Generated test reports directory
├── scripts/             # Utility and automation scripts
├── docs/                # Project documentation
├── tests/               # Unit and integration test suites
│
├── run.py               # CLI entry point script
├── requirements.txt     # Dependency specifications
├── README.md            # Framework documentation
├── VERSION              # Version metadata
├── LICENSE              # License metadata
└── .gitignore           # Git ignore rules
```

---

## Getting Started

### Prerequisites
- **Python 3.10+**

### Environment Configuration
The configuration system supports environment variable overrides:

| Variable Name | Description | Default |
| :--- | :--- | :--- |
| `QUALTEST_ENV` | Operating environment | `development` |
| `QUALTEST_LOG_LEVEL` | Application logging level | `INFO` |
| `QUALTEST_LOGS_DIR` | Directory path for output logs | `<ROOT>/logs` |
| `QUALTEST_REPORTS_DIR` | Directory path for output reports | `<ROOT>/reports` |
| `QUALTEST_TESTCASES_DIR` | Directory path for testcase files | `<ROOT>/testcases` |

---

## Development Roadmap

- [x] **v0.1 – Project Foundation**: Directory structure, configuration system, logging subsystem, CLI entry point, public module interfaces.
- [ ] **v0.2 – Serial & Socket Protocol Stack**: Implementation of TCP/UDP networking and AT command framing.
- [ ] **v0.3 – Modem Simulator**: Simulated AT command engine and RF state machine implementation.
- [ ] **v0.4 – Test Engine & Parser**: Execution engine, testcase parser, and validation engine.
- [ ] **v0.5 – Reporting & CI Integration**: HTML/JUnit reporter, parallel scheduler, and CI pipeline support.
