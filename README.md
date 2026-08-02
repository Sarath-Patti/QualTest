# QualTest

**Wireless Modem Validation & Test Automation Framework**

QualTest is a modular, high-performance test automation framework designed for validating wireless modem hardware, firmware, and protocol stack implementations.

---

## Current Milestone: v0.5 – Failure Injection Engine

The goal of milestone **v0.5** is to introduce a configurable, protocol-independent failure injection engine capable of simulating realistic wireless network anomalies during network simulation.

### Features Implemented in v0.5:
- **Failure Injection Engine**: Protocol-independent engine (`FailureInjector`) simulating wireless network anomalies.
- **Supported Failure Types**:
  - Packet Loss (`packet_loss_percentage`)
  - Artificial Response Delay (`minimum_delay_ms`, `maximum_delay_ms`)
  - Connection Timeout (`timeout_probability`)
  - Connection Reset / Disconnect (`disconnect_probability`)
  - Malformed Response (`malformed_response_probability`)
- **JSON Configuration**: Configurable parameters loaded from `config/failure.json`.
- **Server Integration**: Optional failure injection integrated into `TCPServer` and `UDPServer`.
- **CLI Integration**: Run network simulator with failure injection using `python run.py --simulator tcp --failure-config config/failure.json`.

---

## Failure Injection Engine Architecture

```
                             +-----------------------+
                             |        run.py         |
                             |  (--failure-config)   |
                             +-----------+-----------+
                                         |
                                         v
                             +-----------------------+
                             |    FailureInjector    |
                             | (failure_injector.py) |
                             +-----------+-----------+
                                         |
                       +-----------------+-----------------+
                       |                                   |
           +-----------v-----------+           +-----------v-----------+
           |       TCPServer       |           |       UDPServer       |
           |  (network/tcp/server) |           |  (network/udp/server) |
           +-----------------------+           +-----------------------+
```

---

## Supported Failure Types & Configuration Format

Failures are configured via JSON in `config/failure.json`:

```json
{
  "enabled": true,
  "packet_loss_percentage": 5.0,
  "minimum_delay_ms": 50.0,
  "maximum_delay_ms": 250.0,
  "timeout_probability": 0.02,
  "disconnect_probability": 0.01,
  "malformed_response_probability": 0.03
}
```

### Supported Failure Settings

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `enabled` | Boolean | Master toggle to enable or disable failure injection. |
| `packet_loss_percentage` | Float | Percentage chance to drop outgoing simulator responses (`0.0 - 100.0`). |
| `minimum_delay_ms` | Float | Minimum artificial response delay in milliseconds. |
| `maximum_delay_ms` | Float | Maximum artificial response delay in milliseconds. |
| `timeout_probability` | Float | Probability of suppressing response to trigger client timeout (`0.0 - 1.0`). |
| `disconnect_probability` | Float | Probability of dropping active client connection (`0.0 - 1.0`). |
| `malformed_response_probability` | Float | Probability of returning malformed garbage response (`0.0 - 1.0`). |

---

## CLI Usage

### Run Network Simulator with Failure Injection
```bash
python run.py --simulator tcp --failure-config config/failure.json
```

### Run Testcase Execution & Validation
```bash
python run.py --run testcases/attach_success.json
```

---

## Development Roadmap

- [x] **v0.1 – Project Foundation**: Directory structure, configuration system, logging subsystem, CLI entry point, public module interfaces.
- [x] **v0.2 – JSON Test Runner**: JSON loader, schema validation, exception hierarchy, data models, sample testcases, CLI integration.
- [x] **v0.3 – Network Simulator**: TCP/UDP simulator servers, modem event engine, latency simulation, sample client, CLI integration.
- [x] **v0.4 – Validation Engine**: Step validation engine, latency measurement, validation state Enums, execution summary, CLI execution support.
- [x] **v0.5 – Failure Injection Engine**: Configurable failure injector, simulated network anomalies (loss, delay, timeout, disconnect, malformed payloads), CLI failure config support.
