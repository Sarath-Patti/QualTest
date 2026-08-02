# QualTest

**Wireless Modem Validation & Test Automation Framework**

QualTest is a modular, high-performance test automation framework designed for validating wireless modem hardware, firmware, and protocol stack implementations.

---

## Current Milestone: v0.7 – Reporting & Metrics

The goal of milestone **v0.7** is to build a modular reporting engine that transforms test execution and validation results into structured HTML and CSV reports alongside calculated execution metrics.

### Features Implemented in v0.7:
- **Reporting Engine**: Core `ReportGenerator` aggregating execution metrics and producing reports.
- **Report Data Models**: Immutable dataclass models (`ReportSummary`, `TestCaseReport`, `ExecutionMetrics`).
- **HTML Report Generation**: Formatted HTML report saved at `reports/report.html` with status badges, summary metrics, and result tables.
- **CSV Report Generation**: Standard CSV report saved at `reports/report.csv` using Python's standard `csv` module.
- **Metrics Calculation**: Automatic calculation of pass percentage (`pass_rate`), minimum, maximum, and average response latencies (`latency_ms`), and total wall-clock duration.
- **CLI Integration**: Generate execution reports via `python run.py --run-all testcases/ --report`.

---

## Reporting Architecture

```
                             +-----------------------+
                             |        run.py         |
                             |      (--report)       |
                             +-----------+-----------+
                                         |
                                         v
                             +-----------------------+
                             |  framework.reporter   |
                             |  (ReportGenerator)    |
                             +-----------+-----------+
                                         |
                                         v
                             +-----------------------+
                             |   Calculate Metrics   |
                             |  (ExecutionMetrics)   |
                             +-----------+-----------+
                                         |
                       +-----------------+-----------------+
                       |                                   |
           +-----------v-----------+           +-----------v-----------+
           |   HTML Report Writer  |           |   CSV Report Writer   |
           | (reports/report.html) |           |  (reports/report.csv) |
           +-----------------------+           +-----------------------+
```

---

## Collected Metrics & Generated Reports

### Metrics Calculated

| Metric | Type | Description |
| :--- | :--- | :--- |
| `pass_rate` | Float | Percentage of testcases that passed validation (`0.0 - 100.0%`). |
| `average_latency_ms` | Float | Mean command response latency across all steps in milliseconds. |
| `maximum_latency_ms` | Float | Peak command response latency across all steps in milliseconds. |
| `minimum_latency_ms` | Float | Lowest command response latency across all steps in milliseconds. |
| `total_execution_time_ms` | Float | Overall wall-clock execution duration in milliseconds. |

### Generated Reports Output
- **HTML Report**: `reports/report.html`
- **CSV Report**: `reports/report.csv`

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
