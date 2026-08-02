# QualTest

**Wireless Modem Validation & Test Automation Framework**

QualTest is a modular, high-performance test automation framework designed for validating wireless modem hardware, firmware, and protocol stack implementations.

---

## Current Milestone: v0.2 – JSON Test Runner

The goal of milestone **v0.2** is to introduce a robust, extensible test case loading system capable of reading, validating, and representing test cases from JSON files without performing network execution.

### Features Implemented in v0.2:
- **Parser API**: Public entry point `load_testcase(path)` exposing clean loading interface.
- **Data Models**: Immutable dataclass representations (`TestCase`, `TestStep`).
- **Schema Validation**: Strict validation for required fields, supported protocols (`TCP`, `UDP`), port bounds (`1-65535`), timeout (`> 0`), retry (`>= 0`), and non-empty steps.
- **Custom Exception Hierarchy**: Framework exceptions (`TestCaseError`, `MissingTestCaseError`, `JSONParseError`, `InvalidSchemaError`, `InvalidProtocolError`, `InvalidConfigurationError`).
- **CLI Integration**: Extended `run.py` to support `--test <path>` for testcase loading, validation, and summary display.
- **Sample Testcases**: Configuration definitions included in `testcases/` (`attach_success.json`, `detach.json`, `ping.json`, `timeout.json`, `packet_loss.json`).

---

## Parser Architecture

```
                             +-----------------------+
                             |   framework.parser    |
                             |    (load_testcase)    |
                             +-----------+-----------+
                                         |
                                         v
                             +-----------------------+
                             |      JSONLoader       |
                             | (json_loader.py)      |
                             +-----------+-----------+
                                         |
                       +-----------------+-----------------+
                       |                                   |
           +-----------v-----------+           +-----------v-----------+
           |   Schema Validation   |           |  Exception Hierarchy  |
           | (Protocols, Bounds)   |           |    (exceptions.py)    |
           +-----------+-----------+           +-----------------------+
                       |
                       v
           +-----------------------+
           |     TestCase Model    |
           |      (models.py)      |
           +-----------------------+
```

---

## JSON Testcase Specification & Supported Fields

Testcases are formatted as JSON files containing top-level parameters and an ordered array of execution steps.

### Top-Level Fields

| Field | Type | Required | Description / Constraints |
| :--- | :--- | :--- | :--- |
| `name` | String | Yes | Name of the testcase (non-empty). |
| `description` | String | Yes | Summary of the test objective. |
| `protocol` | String | Yes | Supported network protocol: `"TCP"` or `"UDP"`. |
| `host` | String | Yes | Target host IP address or hostname. |
| `port` | Integer | Yes | Target port number (range: `1` to `65535`). |
| `timeout` | Float/Int | Yes | Step/Execution timeout in seconds (`> 0`). |
| `retry` | Integer | Yes | Number of retry attempts on failure (`>= 0`). |
| `steps` | Array | Yes | Non-empty array of test step objects. |

### Step Object Fields

| Field | Type | Required | Description / Constraints |
| :--- | :--- | :--- | :--- |
| `send` | String | Yes | Command or data payload string to send. |
| `expect` | String | Yes | Expected response string from target. |
| `delay` | Float/Int | No | Optional delay in seconds before step execution (default: `0.0`, must be `>= 0`). |

### Example Testcase (`attach_success.json`)

```json
{
  "name": "Attach Success Test",
  "description": "Validates successful network attach sequence via AT commands over TCP.",
  "protocol": "TCP",
  "host": "127.0.0.1",
  "port": 8080,
  "timeout": 5.0,
  "retry": 3,
  "steps": [
    {
      "send": "AT+CFUN=1",
      "expect": "OK",
      "delay": 0.5
    },
    {
      "send": "AT+CGATT=1",
      "expect": "OK",
      "delay": 1.0
    }
  ]
}
```

---

## Getting Started & Usage

### Inspect & Validate a Testcase
Run `run.py` with the `--test` (or `-t`) flag:

```bash
python run.py --test testcases/attach_success.json
```

---

## Development Roadmap

- [x] **v0.1 – Project Foundation**: Directory structure, configuration system, logging subsystem, CLI entry point, public module interfaces.
- [x] **v0.2 – JSON Test Runner**: JSON loader, schema validation, exception hierarchy, data models, sample testcases, CLI integration.
