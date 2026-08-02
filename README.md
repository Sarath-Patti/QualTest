# QualTest

**Wireless Modem Validation & Test Automation Framework**

QualTest is a modular, high-performance test automation framework designed for validating wireless modem hardware, firmware, and protocol stack implementations.

---

## Current Milestone: v0.4 – Validation Engine

The goal of milestone **v0.4** is to build a reusable validation engine capable of comparing simulator responses against expected outputs defined in JSON testcases, measuring step latencies, and producing structured execution summaries.

### Features Implemented in v0.4:
- **Validation Engine**: Core `ValidationEngine` executing testcase steps against TCP/UDP targets.
- **Validation States**: Enum-based state outcomes (`PASS`, `FAIL`, `ERROR`, `TIMEOUT`, `UNKNOWN`).
- **Data Models**: Immutable dataclass models (`ValidationStep`, `ValidationResult`, `ExecutionSummary`).
- **Latency Measurement**: High-precision per-step command latency measurement (`latency_ms`).
- **Custom Exceptions**: Specialized exception hierarchy (`ValidationError`, `ResponseMismatchError`, `TimeoutError`, `ExecutionError`).
- **Public Validation API**: Public entry point `validate(testcase)`.
- **CLI Integration**: Run testcase execution and validation via `python run.py --run <testcase_path>`.

---

## Validation Engine Architecture

```
                             +-----------------------+
                             |        run.py         |
                             |  (--run <testcase>)   |
                             +-----------+-----------+
                                         |
                                         v
                             +-----------------------+
                             |  framework.validator  |
                             |  (validate API call)  |
                             +-----------+-----------+
                                         |
                                         v
                             +-----------------------+
                             |   ValidationEngine    |
                             |      (engine.py)      |
                             +-----------+-----------+
                                         |
            +----------------------------+----------------------------+
            |                            |                            |
+-----------v-----------+    +-----------v-----------+    +-----------v-----------+
| Network Protocol      |    | Latency Measurement   |    | Validation States     |
| (TCPClient/UDPClient) |    | (time.perf_counter)   |    | (PASS/FAIL/TIMEOUT..) |
+-----------+-----------+    +-----------+-----------+    +-----------+-----------+
            |                            |                            |
            +----------------------------+----------------------------+
                                         |
                                         v
                             +-----------------------+
                             |   ExecutionSummary    |
                             |      (models.py)      |
                             +-----------------------+
```

---

## Validation Execution Flow

1. **Testcase Loading**: Load and parse JSON testcase using `load_testcase()`.
2. **Network Connection**: Connect to target `host:port` via `TCPClient` or `UDPClient`.
3. **Step Execution Loop**:
   - Apply optional step delay.
   - Record start timestamp.
   - Send command string over socket.
   - Receive response string (or handle socket timeout/error).
   - Record end timestamp and compute `latency_ms`.
4. **Step Comparison**: Compare `actual_response` against `expected_response`.
5. **State Assignment**: Assign `PASS`, `FAIL`, `TIMEOUT`, or `ERROR` state.
6. **Summary Generation**: Aggregate metrics into an immutable `ExecutionSummary`.

---

## Validation States

| State | Enum Value | Description |
| :--- | :--- | :--- |
| **PASS** | `ValidationState.PASS` | Actual response matched expected response exactly. |
| **FAIL** | `ValidationState.FAIL` | Actual response differed from expected response. |
| **TIMEOUT** | `ValidationState.TIMEOUT` | Command execution or socket response timed out. |
| **ERROR** | `ValidationState.ERROR` | Connection or socket error occurred during step. |
| **UNKNOWN** | `ValidationState.UNKNOWN` | Uninitialized or indeterminate step status. |

---

## Executing & Validating a Testcase

### Run Testcase Validation
```bash
python run.py --run testcases/attach_success.json
```

### Inspect Testcase Schema Only
```bash
python run.py --test testcases/attach_success.json
```

### Start Modem Network Simulator
```bash
python run.py --simulator tcp
```

---

## Development Roadmap

- [x] **v0.1 – Project Foundation**: Directory structure, configuration system, logging subsystem, CLI entry point, public module interfaces.
- [x] **v0.2 – JSON Test Runner**: JSON loader, schema validation, exception hierarchy, data models, sample testcases, CLI integration.
- [x] **v0.3 – Network Simulator**: TCP/UDP simulator servers, modem event engine, latency simulation, sample client, CLI integration.
- [x] **v0.4 – Validation Engine**: Step validation engine, latency measurement, validation state Enums, execution summary, CLI execution support.
