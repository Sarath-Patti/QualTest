# QualTest

**Wireless Modem Validation & Test Automation Framework**

QualTest is a modular, high-performance test automation framework designed for validating wireless modem hardware, firmware, and protocol stack implementations.

---

## Current Milestone: v0.6 – Concurrent Test Scheduler

The goal of milestone **v0.6** is to implement a scalable concurrent test scheduler capable of discovering, queueing, and executing multiple testcases simultaneously using Python's `ThreadPoolExecutor`.

### Features Implemented in v0.6:
- **Concurrent Test Scheduler**: Core `ConcurrentScheduler` engine managing worker thread pools.
- **Multithreaded Execution Model**: Discovers and dispatches multiple independent testcases in parallel via `ThreadPoolExecutor`.
- **Scheduler Data Models**: Immutable dataclass models (`ExecutionTask`, `ExecutionResult`, `SchedulerSummary`).
- **Worker Error Isolation**: Fault isolation ensuring failing testcases or worker exceptions do not crash the scheduler pool.
- **Scheduler Lifecycle**: Full lifecycle control (`initialize`, `start`, `submit_task`, `wait_for_completion`, `cancel_pending_tasks`, `shutdown`).
- **CLI Integration**: Batch execution of testcase suites via `python run.py --run-all testcases/`.

---

## Concurrent Test Scheduler Architecture

```
                             +-----------------------+
                             |        run.py         |
                             |  (--run-all <dir>)    |
                             +-----------+-----------+
                                         |
                                         v
                             +-----------------------+
                             |  framework.scheduler  |
                             |  (ConcurrentScheduler)|
                             +-----------+-----------+
                                         |
                                         v
                             +-----------------------+
                             |  ThreadPoolExecutor   |
                             | (Worker Thread Pool)  |
                             +----+-------------+----+
                                  |             |
           +----------------------+             +----------------------+
           |                                                           |
           v                                                           v
+-----------------------+                                   +-----------------------+
|  Worker Thread #1     |                                   |  Worker Thread #N     |
| (load & validate TC1) |                                   | (load & validate TCN) |
+-----------+-----------+                                   +-----------+-----------+
            |                                                           |
            +---------------------------+-------------------------------+
                                        |
                                        v
                            +-----------------------+
                            |   SchedulerSummary    |
                            |      (models.py)      |
                            +-----------------------+
```

---

## Scheduler Lifecycle & Concurrent Execution Model

1. **Discovery**: Discover all `.json` testcase files in target directory.
2. **Initialization**: Initialize `ConcurrentScheduler` with thread pool size (`max_workers`).
3. **Queueing & Submission**: Submit each testcase as an `ExecutionTask` to `ThreadPoolExecutor`.
4. **Parallel Execution**: Worker threads execute `load_testcase()` and `validate()` independently in parallel.
5. **Fault Isolation**: Catch and record parser or worker exceptions per task without interrupting other workers.
6. **Result Aggregation**: Aggregate thread-safe `ExecutionResult` records into an immutable `SchedulerSummary`.
7. **Shutdown**: Perform graceful thread pool shutdown.

---

## CLI Usage

### Run All Testcases Concurrently
```bash
python run.py --run-all testcases/
```

### Run Single Testcase Execution & Validation
```bash
python run.py --run testcases/attach_success.json
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
- [x] **v0.6 – Concurrent Test Scheduler**: ThreadPoolExecutor scheduler, parallel batch testcase execution, scheduler lifecycle, thread-safe result aggregation, CLI `--run-all` support.
