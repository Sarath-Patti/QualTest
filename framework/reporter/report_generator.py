"""Report generation engine for QualTest framework.

Transforms test execution and validation metrics into structured HTML and CSV reports.
Calculates pass rates, wall-clock durations, min/max/avg response latencies, and step details.
"""

import csv
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Sequence, Union

from framework.config import Settings, get_settings
from framework.logger import get_logger
from framework.reporter.models import (
    ExecutionMetrics,
    ReportSummary,
    TestCaseReport,
)
from framework.scheduler.models import ExecutionResult, SchedulerSummary
from framework.validator.models import ExecutionSummary, ValidationState

logger = get_logger("Reporter.Generator")


class ReportGenerator:
    """Generates structured HTML and CSV reports from execution summaries."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        """Initializes ReportGenerator.

        Args:
            settings: Optional Settings instance.
        """
        self.settings = settings or get_settings()
        self.reports_dir = self.settings.reports_dir
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def calculate_metrics(
        self,
        results: Sequence[Union[ExecutionResult, ExecutionSummary]],
        total_wall_time_ms: float,
    ) -> Tuple[ReportSummary, ExecutionMetrics, List[TestCaseReport]]:
        """Calculates execution performance metrics from result objects.

        Args:
            results: Sequence of ExecutionResult or ExecutionSummary instances.
            total_wall_time_ms: Total wall-clock execution time in milliseconds.

        Returns:
            Tuple[ReportSummary, ExecutionMetrics, List[TestCaseReport]]: Calculated metrics tuple.
        """
        logger.info("Report generation started")

        tc_reports: List[TestCaseReport] = []
        all_latencies: List[float] = []
        passed_count = 0
        failed_count = 0

        for item in results:
            if isinstance(item, ExecutionResult):
                name = item.testcase_name
                status_str = item.execution_status.value
                exec_time = item.execution_time_ms
                failure_reason = item.error_message or "None"

                step_latencies: List[float] = []
                if item.summary and item.summary.step_results:
                    step_latencies = [s.latency_ms for s in item.summary.step_results]
                    all_latencies.extend(step_latencies)
                    if failure_reason == "None" and item.execution_status != ValidationState.PASS:
                        # Extract failure details from step results
                        failed_steps = [s for s in item.summary.step_results if s.status != ValidationState.PASS]
                        if failed_steps:
                            first_fail = failed_steps[0]
                            failure_reason = f"Step #{first_fail.step_number} [{first_fail.status.value}]: Sent '{first_fail.command_sent}', Expected '{first_fail.expected_response}', Got '{first_fail.actual_response}'"

                avg_lat = (sum(step_latencies) / len(step_latencies)) if step_latencies else 0.0

                if item.execution_status == ValidationState.PASS:
                    passed_count += 1
                else:
                    failed_count += 1

            elif isinstance(item, ExecutionSummary):
                name = item.testcase_name
                status_str = item.final_status.value
                exec_time = item.execution_time_ms
                failure_reason = "None"

                step_latencies = [s.latency_ms for s in item.step_results]
                all_latencies.extend(step_latencies)
                avg_lat = (sum(step_latencies) / len(step_latencies)) if step_latencies else 0.0

                if item.final_status != ValidationState.PASS:
                    failed_steps = [s for s in item.step_results if s.status != ValidationState.PASS]
                    if failed_steps:
                        first_fail = failed_steps[0]
                        failure_reason = f"Step #{first_fail.step_number} [{first_fail.status.value}]: Sent '{first_fail.command_sent}', Expected '{first_fail.expected_response}', Got '{first_fail.actual_response}'"

                if item.final_status == ValidationState.PASS:
                    passed_count += 1
                else:
                    failed_count += 1

            tc_reports.append(
                TestCaseReport(
                    testcase_name=name,
                    status=status_str,
                    execution_time_ms=exec_time,
                    average_latency_ms=avg_lat,
                    failure_reason=failure_reason,
                )
            )

        total_tc = len(tc_reports)
        pass_rate = (passed_count / total_tc * 100.0) if total_tc > 0 else 0.0
        avg_latency = (sum(all_latencies) / len(all_latencies)) if all_latencies else 0.0
        max_latency = max(all_latencies) if all_latencies else 0.0
        min_latency = min(all_latencies) if all_latencies else 0.0

        summary = ReportSummary(
            total_testcases=total_tc,
            passed=passed_count,
            failed=failed_count,
            execution_time_ms=total_wall_time_ms,
        )

        metrics = ExecutionMetrics(
            pass_rate=pass_rate,
            average_latency_ms=avg_latency,
            maximum_latency_ms=max_latency,
            minimum_latency_ms=min_latency,
            total_execution_time_ms=total_wall_time_ms,
        )

        logger.info(
            "Metrics calculated: pass_rate=%.1f%%, avg_latency=%.2fms, min_latency=%.2fms, max_latency=%.2fms",
            pass_rate,
            avg_latency,
            min_latency,
            max_latency,
        )

        return summary, metrics, tc_reports

    def generate_html_report(
        self,
        summary: ReportSummary,
        metrics: ExecutionMetrics,
        tc_reports: List[TestCaseReport],
        output_path: Optional[Path] = None,
    ) -> Path:
        """Generates a clean, professional HTML report.

        Args:
            summary: ReportSummary object.
            metrics: ExecutionMetrics object.
            tc_reports: List of TestCaseReport objects.
            output_path: Target HTML file path. Defaults to reports/report.html.

        Returns:
            Path: Path to written HTML report.
        """
        target_path = output_path or (self.reports_dir / "report.html")
        logger.info("HTML report generation started: %s", target_path)

        rows_html = ""
        for tc in tc_reports:
            badge_class = "pass" if tc.status == "PASS" else "fail"
            rows_html += f"""
            <tr>
                <td><strong>{tc.testcase_name}</strong></td>
                <td><span class="badge {badge_class}">{tc.status}</span></td>
                <td>{tc.execution_time_ms:.2f} ms</td>
                <td>{tc.average_latency_ms:.2f} ms</td>
                <td>{tc.failure_reason}</td>
            </tr>"""

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QualTest Execution Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0; padding: 24px; background-color: #f8f9fa; color: #212529;
        }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        .header {{ margin-bottom: 24px; border-bottom: 2px solid #e9ecef; padding-bottom: 16px; }}
        .header h1 {{ margin: 0; color: #0f172a; font-size: 28px; }}
        .header p {{ margin: 6px 0 0 0; color: #64748b; font-size: 14px; }}
        .grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }}
        .card {{ background: #ffffff; padding: 16px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); text-align: center; border: 1px solid #e2e8f0; }}
        .card .value {{ font-size: 24px; font-weight: 700; margin-top: 4px; color: #0f172a; }}
        .card .label {{ font-size: 12px; text-transform: uppercase; color: #64748b; font-weight: 600; letter-spacing: 0.5px; }}
        table {{ width: 100%; border-collapse: collapse; background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; }}
        th, td {{ padding: 12px 16px; text-align: left; border-bottom: 1px solid #e2e8f0; font-size: 14px; }}
        th {{ background-color: #f1f5f9; color: #475569; font-weight: 600; text-transform: uppercase; font-size: 12px; letter-spacing: 0.5px; }}
        tr:last-child td {{ border-bottom: none; }}
        .badge {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 700; text-transform: uppercase; }}
        .badge.pass {{ background-color: #dcfce7; color: #15803d; }}
        .badge.fail {{ background-color: #fee2e2; color: #b91c1c; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>QualTest Execution Report</h1>
            <p>Generated at: {summary.generated_at}</p>
        </div>

        <div class="grid">
            <div class="card">
                <div class="label">Total Testcases</div>
                <div class="value">{summary.total_testcases}</div>
            </div>
            <div class="card">
                <div class="label">Pass Rate</div>
                <div class="value">{metrics.pass_rate:.1f}%</div>
            </div>
            <div class="card">
                <div class="label">Passed / Failed</div>
                <div class="value" style="color: #15803d;">{summary.passed} <span style="color: #64748b; font-size: 16px;">/</span> <span style="color: #b91c1c;">{summary.failed}</span></div>
            </div>
            <div class="card">
                <div class="label">Avg Latency</div>
                <div class="value">{metrics.average_latency_ms:.2f} ms</div>
            </div>
        </div>

        <table>
            <thead>
                <tr>
                    <th>Testcase Name</th>
                    <th>Status</th>
                    <th>Execution Duration</th>
                    <th>Avg Latency</th>
                    <th>Failure Reason</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
</body>
</html>
"""

        with open(target_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info("HTML report generated: %s", target_path)
        return target_path

    def generate_csv_report(
        self,
        tc_reports: List[TestCaseReport],
        output_path: Optional[Path] = None,
    ) -> Path:
        """Generates a CSV report using standard python csv module.

        Args:
            tc_reports: List of TestCaseReport objects.
            output_path: Target CSV file path. Defaults to reports/report.csv.

        Returns:
            Path: Path to written CSV report.
        """
        target_path = output_path or (self.reports_dir / "report.csv")
        logger.info("CSV report generation started: %s", target_path)

        headers = [
            "Testcase Name",
            "Status",
            "Execution Time (ms)",
            "Average Latency (ms)",
            "Failure Reason",
        ]

        with open(target_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for tc in tc_reports:
                writer.writerow(
                    [
                        tc.testcase_name,
                        tc.status,
                        f"{tc.execution_time_ms:.2f}",
                        f"{tc.average_latency_ms:.2f}",
                        tc.failure_reason,
                    ]
                )

        logger.info("CSV report generated: %s", target_path)
        return target_path

    def generate_all(
        self,
        summary_source: Union[SchedulerSummary, ExecutionSummary, Sequence[Union[ExecutionResult, ExecutionSummary]]],
        total_wall_time_ms: Optional[float] = None,
    ) -> Tuple[Path, Path]:
        """Convenience method to calculate metrics and generate both HTML and CSV reports.

        Args:
            summary_source: SchedulerSummary, ExecutionSummary, or sequence of results.
            total_wall_time_ms: Optional wall-clock time override.

        Returns:
            Tuple[Path, Path]: (html_report_path, csv_report_path) tuple.
        """
        if isinstance(summary_source, SchedulerSummary):
            results = summary_source.results
            wall_time = total_wall_time_ms or summary_source.total_execution_time_ms
        elif isinstance(summary_source, ExecutionSummary):
            results = [summary_source]
            wall_time = total_wall_time_ms or summary_source.execution_time_ms
        else:
            results = list(summary_source)
            wall_time = total_wall_time_ms or 0.0

        summary, metrics, tc_reports = self.calculate_metrics(results, wall_time)
        html_path = self.generate_html_report(summary, metrics, tc_reports)
        csv_path = self.generate_csv_report(tc_reports)

        logger.info("Report generation completed: HTML=%s, CSV=%s", html_path, csv_path)
        return html_path, csv_path
