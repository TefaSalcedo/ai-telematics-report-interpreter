"""
MCP Server for fleet telemetry analysis.

Exposes tools for data validation, performance analysis, anomaly detection,
multi-company comparison, and report generation via the Model Context Protocol.
"""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import FastMCP

from src.analyzers.anomaly_detector import AnomalyDetector
from src.analyzers.company_comparator import CompanyComparator
from src.analyzers.performance_analyzer import PerformanceAnalyzer
from src.models.telemetry import TelemetryReport
from src.reports.report_generator import ReportGenerator
from src.validators.data_validator import DataValidator

mcp = FastMCP(
    "fleet-telemetry-analyzer",
    instructions=(
        "Fleet telemetry analysis server. Receives JSON telemetry data from "
        "transport fleet providers and performs validation, performance analysis, "
        "anomaly detection, multi-company comparison, and report generation."
    ),
)

# --- Shared service instances ---
_validator = DataValidator()
_performance_analyzer = PerformanceAnalyzer()
_anomaly_detector = AnomalyDetector()
_comparator = CompanyComparator()
_report_generator = ReportGenerator()


def _parse_report(data: dict[str, Any]) -> TelemetryReport:
    """Parse raw dict into a TelemetryReport model."""
    return TelemetryReport(**data)


# ═══════════════════════════════════════════════════════
# TOOL: validate_telemetry_data
# ═══════════════════════════════════════════════════════

@mcp.tool()
def validate_telemetry_data(data: str) -> str:
    """Validate a telemetry JSON report for structural and logical correctness.

    Checks for missing required keys, negative values, out-of-range consumption,
    subtotal mismatches, duplicate vehicle IDs, and malformed dates.

    Args:
        data: JSON string containing the telemetry report.

    Returns:
        JSON string with validation result including status, errors, and warnings.
    """
    try:
        raw = json.loads(data)
    except json.JSONDecodeError as e:
        return json.dumps({"status": "invalid", "errors": [{"field": "json", "message": f"Invalid JSON: {e}"}], "warnings": []})

    # Structural validation on raw dict
    result = _validator.validate(raw)

    # If structurally valid, also run logical validation on parsed model
    if result.status == "valid":
        try:
            report = _parse_report(raw)
            logical_result = _validator.validate_parsed(report)
            result.warnings.extend(logical_result.warnings)
            result.errors.extend(logical_result.errors)
            if logical_result.errors:
                result.status = "invalid"
        except Exception as e:
            result.warnings.append(
                {"field": "model", "message": f"Could not parse model for logical validation: {e}", "severity": "warning"}
            )

    return result.model_dump_json(indent=2)


# ═══════════════════════════════════════════════════════
# TOOL: analyze_performance
# ═══════════════════════════════════════════════════════

@mcp.tool()
def analyze_performance(data: str) -> str:
    """Analyze fuel performance metrics for all vehicles in a telemetry report.

    Calculates fuel efficiency (km/gal), deviation from expected consumption,
    performance variation vs previous period, idle ratio, and consumption rate.
    Generates alerts based on business rules (>10% yellow, >20% red).

    Args:
        data: JSON string containing the telemetry report.

    Returns:
        JSON string with a list of performance alerts.
    """
    try:
        raw = json.loads(data)
        report = _parse_report(raw)
    except Exception as e:
        return json.dumps({"error": f"Failed to parse report: {e}"})

    alerts = _performance_analyzer.analyze(report)
    return json.dumps([a.model_dump() for a in alerts], indent=2, ensure_ascii=False)


# ═══════════════════════════════════════════════════════
# TOOL: detect_anomalies
# ═══════════════════════════════════════════════════════

@mcp.tool()
def detect_anomalies(data: str) -> str:
    """Detect anomalies in fleet telemetry data.

    Analyzes fuel discharge patterns, unauthorized loads, sensor behavior issues,
    and temporal patterns. Differentiates between theft, leaks, sensor failures,
    and operational errors.

    Args:
        data: JSON string containing the telemetry report.

    Returns:
        JSON string with a list of detected anomalies including severity,
        possible causes, and recommendations.
    """
    try:
        raw = json.loads(data)
        report = _parse_report(raw)
    except Exception as e:
        return json.dumps({"error": f"Failed to parse report: {e}"})

    anomalies = _anomaly_detector.detect(report)
    return json.dumps([a.model_dump() for a in anomalies], indent=2, ensure_ascii=False)


# ═══════════════════════════════════════════════════════
# TOOL: compare_reports
# ═══════════════════════════════════════════════════════

@mcp.tool()
def compare_reports(data_a: str, data_b: str) -> str:
    """Compare telemetry data from two different sources.

    Compares fleet-level and vehicle-level metrics between two reports to
    detect incoherences between data providers.

    Args:
        data_a: JSON string of the first telemetry report (e.g., Empresa A).
        data_b: JSON string of the second telemetry report (e.g., TransLogística S.A.).

    Returns:
        JSON string with comparison results for each metric.
    """
    try:
        report_a = _parse_report(json.loads(data_a))
        report_b = _parse_report(json.loads(data_b))
    except Exception as e:
        return json.dumps({"error": f"Failed to parse reports: {e}"})

    results = _comparator.compare(report_a, report_b)
    return json.dumps([r.model_dump() for r in results], indent=2, ensure_ascii=False)


# ═══════════════════════════════════════════════════════
# TOOL: generate_full_report
# ═══════════════════════════════════════════════════════

@mcp.tool()
def generate_full_report(data: str) -> str:
    """Generate a complete analysis report for a telemetry dataset.

    Runs validation, performance analysis, and anomaly detection, then
    assembles a final report with executive summary, key findings,
    critical vehicle ranking, and actionable recommendations.

    Args:
        data: JSON string containing the telemetry report.

    Returns:
        JSON string with the complete analysis report.
    """
    try:
        raw = json.loads(data)
        report = _parse_report(raw)
    except Exception as e:
        return json.dumps({"error": f"Failed to parse report: {e}"})

    validation = _validator.validate(raw)
    if validation.status == "valid":
        try:
            logical = _validator.validate_parsed(report)
            validation.warnings.extend(logical.warnings)
            validation.errors.extend(logical.errors)
            if logical.errors:
                validation.status = "invalid"
        except Exception:
            pass

    alerts = _performance_analyzer.analyze(report)
    anomalies = _anomaly_detector.detect(report)

    final = _report_generator.generate(
        report=report,
        validation=validation,
        performance_alerts=alerts,
        anomalies=anomalies,
    )

    return final.model_dump_json(indent=2)


# ═══════════════════════════════════════════════════════
# Entry point for MCP stdio transport
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    mcp.run(transport="stdio")
