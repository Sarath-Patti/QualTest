# QualTest

**Wireless Modem Validation & Test Automation Framework**

QualTest is a modular, high-performance test automation framework designed for validating wireless modem hardware, firmware, and protocol stack implementations.

---

## Current Milestone: v0.3 – Network Simulator

The goal of milestone **v0.3** is to build a reusable TCP/UDP-based modem network simulator capable of emulating basic modem communication for future automated validation.

### Features Implemented in v0.3:
- **Simulator Abstraction**: Base simulator class (`BaseSimulator`) and protocol-agnostic controller (`NetworkSimulator`).
- **TCP Simulator Server & Client**: Multithreaded TCP server (`TCPServer`) and client (`TCPClient`).
- **UDP Simulator Server & Client**: Datagram UDP server (`UDPServer`) and client (`UDPClient`).
- **Modem Events**: Automated mapping for modem events (`ATTACH_REQUEST`, `DETACH_REQUEST`, `PING`, `STATUS`, `UNKNOWN_COMMAND`).
- **Configurable Settings**: Support for configurable host, port, protocol, and simulated response latency.
- **CLI Integration**: Run TCP or UDP simulator via `python run.py --simulator tcp` or `python run.py --simulator udp` with graceful shutdown handling.
- **Sample Client Script**: Lightweight utility (`scripts/sample_client.py`) for manual command testing over TCP/UDP.

---

## Network Simulator Architecture

```
                             +-----------------------+
                             |        run.py         |
                             |  (--simulator tcp|udp) |
                             +-----------+-----------+
                                         |
                                         v
                             +-----------------------+
                             |   NetworkSimulator    |
                             | (network_simulator.py)|
                             +-----------+-----------+
                                         |
                       +-----------------+-----------------+
                       |                                   |
           +-----------v-----------+           +-----------v-----------+
           |       TCPServer       |           |       UDPServer       |
           |  (network/tcp/server) |           |  (network/udp/server) |
           +-----------+-----------+           +-----------+-----------+
                       |                                   |
                       +-----------------+-----------------+
                                         |
                                         v
                             +-----------------------+
                             |     BaseSimulator     |
                             |   (Modem Event Engine)|
                             +-----------------------+
```

---

## Supported Modem Commands & Responses

The simulator provides built-in responses for common modem control events:

| Incoming Command | Simulated Response | Description |
| :--- | :--- | :--- |
| `ATTACH_REQUEST` | `ATTACH_ACCEPT` | Simulates EPS/GPRS network attach request. |
| `DETACH_REQUEST` | `DETACH_ACCEPT` | Simulates network detach request. |
| `PING` | `PONG` | Simulates data channel connectivity check. |
| `STATUS` | `MODEM_READY` | Simulates modem operating state query. |
| *(Any Other Command)* | `UNKNOWN_COMMAND` | Default response for unhandled commands. |

---

## Starting the Simulator

### Run TCP Modem Simulator
```bash
python run.py --simulator tcp
```

### Run UDP Modem Simulator
```bash
python run.py --simulator udp
```

### Manual Testing with Sample Client
In a separate terminal window:

```bash
# Test TCP Simulator
python scripts/sample_client.py --protocol tcp --command ATTACH_REQUEST

# Test UDP Simulator
python scripts/sample_client.py --protocol udp --command PING
```

---

## JSON Testcase Inspection & Validation

```bash
python run.py --test testcases/attach_success.json
```

---

## Development Roadmap

- [x] **v0.1 – Project Foundation**: Directory structure, configuration system, logging subsystem, CLI entry point, public module interfaces.
- [x] **v0.2 – JSON Test Runner**: JSON loader, schema validation, exception hierarchy, data models, sample testcases, CLI integration.
- [x] **v0.3 – Network Simulator**: TCP/UDP simulator servers, modem event engine, latency simulation, sample client, CLI integration.
