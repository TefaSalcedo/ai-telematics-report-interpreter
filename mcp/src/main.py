"""
CLI entry point for the fleet telemetry analysis system.

Usage:
    python -m src.main data/sample_report.json
    python -m src.main data/report_a.json --compare data/report_b.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.analyzers.anomaly_detector import AnomalyDetector
from src.analyzers.company_comparator import CompanyComparator
from src.analyzers.performance_analyzer import PerformanceAnalyzer
from src.models.telemetry import TelemetryReport
from src.reports.report_generator import ReportGenerator
from src.validators.data_validator import DataValidator


def load_json(filepath: str) -> dict:
    """Load and parse a JSON file."""
    path = Path(filepath)
    if not path.exists():
        print(f"Error: archivo no encontrado: {filepath}", file=sys.stderr)
        sys.exit(1)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: JSON inválido en {filepath}: {e}", file=sys.stderr)
        sys.exit(1)


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'═' * 60}")
    print(f"  {title}")
    print(f"{'═' * 60}")


def run_analysis(data_path: str, compare_path: str | None = None) -> None:
    """Run the full analysis pipeline and print results to stdout."""
    # Load primary data
    raw_data = load_json(data_path)

    # Initialize services
    validator = DataValidator()
    perf_analyzer = PerformanceAnalyzer()
    anomaly_detector = AnomalyDetector()
    report_generator = ReportGenerator()

    # Step 1: Validation
    print_section("1. VALIDACIÓN DE DATOS")
    validation = validator.validate(raw_data)
    print(f"  Estado: {validation.status.upper()}")
    if validation.errors:
        print(f"  Errores ({len(validation.errors)}):")
        for err in validation.errors:
            print(f"    ✗ [{err.field}] {err.message}")
    if validation.warnings:
        print(f"  Advertencias ({len(validation.warnings)}):")
        for warn in validation.warnings:
            print(f"    ⚠ [{warn.field}] {warn.message}")
    if not validation.errors and not validation.warnings:
        print("  ✓ Sin errores ni advertencias.")

    # Parse model
    try:
        report = TelemetryReport(**raw_data)
    except Exception as e:
        print(f"\nError fatal al parsear el reporte: {e}", file=sys.stderr)
        sys.exit(1)

    # Logical validation
    logical_validation = validator.validate_parsed(report)
    validation.warnings.extend(logical_validation.warnings)
    validation.errors.extend(logical_validation.errors)
    if logical_validation.errors:
        validation.status = "invalid"

    if logical_validation.warnings:
        print(f"  Advertencias lógicas adicionales ({len(logical_validation.warnings)}):")
        for warn in logical_validation.warnings:
            print(f"    ⚠ [{warn.field}] {warn.message}")

    # Step 2: Performance Analysis
    print_section("2. ANÁLISIS DE RENDIMIENTO")
    alerts = perf_analyzer.analyze(report)
    if alerts:
        for alert in alerts:
            icon = "🔴" if alert.alert_level.value in ("red", "critical") else "🟡"
            print(f"  {icon} {alert.message}")
    else:
        print("  ✓ Sin alertas de rendimiento.")

    # Step 3: Anomaly Detection
    print_section("3. DETECCIÓN DE ANOMALÍAS")
    anomalies = anomaly_detector.detect(report)
    if anomalies:
        for anomaly in anomalies:
            icon = "🔴" if anomaly.severity.value in ("red", "critical") else "🟡"
            print(f"  {icon} [{anomaly.category}] {anomaly.description}")
            if anomaly.possible_causes:
                for cause in anomaly.possible_causes:
                    print(f"      → {cause}")
            if anomaly.recommendation:
                print(f"      ★ {anomaly.recommendation}")
    else:
        print("  ✓ Sin anomalías detectadas.")

    # Step 4: Multi-company comparison (optional)
    comparison = []
    if compare_path:
        print_section("4. COMPARACIÓN MULTIEMPRESA")
        raw_b = load_json(compare_path)
        try:
            report_b = TelemetryReport(**raw_b)
        except Exception as e:
            print(f"  Error al parsear reporte de comparación: {e}", file=sys.stderr)
            report_b = None

        if report_b:
            comparator = CompanyComparator()
            comparison = comparator.compare(report, report_b)
            for comp in comparison:
                icon = "✓" if comp.is_coherent else "✗"
                print(
                    f"  {icon} {comp.metric}: "
                    f"A={comp.provider_a_value}, B={comp.provider_b_value} "
                    f"(diff={comp.difference_percent:+.1f}%)"
                )
                if comp.note:
                    print(f"      {comp.note}")

    # Step 5: Final Report
    print_section("5. REPORTE FINAL")
    final_report = report_generator.generate(
        report=report,
        validation=validation,
        performance_alerts=alerts,
        anomalies=anomalies,
        comparison=comparison,
    )

    # Executive summary
    print(f"\n{final_report.executive_summary}")

    # Key findings
    if final_report.key_findings:
        print("\n  HALLAZGOS CLAVE:")
        for finding in final_report.key_findings:
            print(f"    • {finding}")

    # Critical vehicles
    if final_report.critical_vehicles:
        print("\n  VEHÍCULOS CRÍTICOS (por puntaje de riesgo):")
        for cv in final_report.critical_vehicles:
            print(
                f"    [{cv['vehicle_id']}] Riesgo={cv['risk_score']} "
                f"(alertas={cv['alert_count']}, anomalías={cv['anomaly_count']})"
            )
            for issue in cv.get("top_issues", []):
                print(f"      - {issue}")

    # Recommendations
    if final_report.recommendations:
        print("\n  RECOMENDACIONES:")
        for idx, rec in enumerate(final_report.recommendations, 1):
            print(f"    {idx}. {rec}")

    # Export JSON report
    output_path = Path(data_path).stem + "_analysis.json"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_report.model_dump_json(indent=2))
    print(f"\n  📄 Reporte completo exportado a: {output_path}")


def main() -> None:
    """Parse CLI arguments and run analysis."""
    parser = argparse.ArgumentParser(
        description="Fleet Telemetry Analysis System - Fuel Sensor Analytics"
    )
    parser.add_argument(
        "input_file",
        help="Path to the JSON telemetry report file.",
    )
    parser.add_argument(
        "--compare",
        dest="compare_file",
        default=None,
        help="Optional: path to a second JSON report for multi-company comparison.",
    )

    args = parser.parse_args()
    run_analysis(args.input_file, args.compare_file)


if __name__ == "__main__":
    main()
