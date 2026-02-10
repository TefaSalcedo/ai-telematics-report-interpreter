"""
Report generation module.

Produces a structured final report combining validation results,
performance alerts, anomaly findings, and recommendations.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from src.models.telemetry import (
    AlertLevel,
    AnomalyFinding,
    ComparisonResult,
    FinalReport,
    PerformanceAlert,
    TelemetryReport,
    ValidationResult,
)
from src.utils.helpers import format_period


class ReportGenerator:
    """Generates the final structured analysis report."""

    def generate(
        self,
        report: TelemetryReport,
        validation: ValidationResult,
        performance_alerts: list[PerformanceAlert],
        anomalies: list[AnomalyFinding],
        comparison: list[ComparisonResult] | None = None,
    ) -> FinalReport:
        """Assemble all analysis results into a FinalReport."""
        period = format_period(report.period_start, report.period_end)
        key_findings = self._build_key_findings(validation, performance_alerts, anomalies)
        critical_vehicles = self._rank_critical_vehicles(performance_alerts, anomalies)
        recommendations = self._build_recommendations(anomalies, performance_alerts)
        executive_summary = self._build_executive_summary(
            report, validation, performance_alerts, anomalies
        )

        return FinalReport(
            client=report.client,
            period=period,
            validation=validation,
            key_findings=key_findings,
            performance_alerts=performance_alerts,
            anomalies=anomalies,
            critical_vehicles=critical_vehicles,
            comparison=comparison or [],
            recommendations=recommendations,
            executive_summary=executive_summary,
        )

    # --- Key Findings ---

    def _build_key_findings(
        self,
        validation: ValidationResult,
        alerts: list[PerformanceAlert],
        anomalies: list[AnomalyFinding],
    ) -> list[str]:
        findings: list[str] = []

        # Validation summary
        if validation.status == "invalid":
            findings.append(
                f"⚠ Datos con errores de validación: {len(validation.errors)} error(es), "
                f"{len(validation.warnings)} advertencia(s)."
            )
        elif validation.warnings:
            findings.append(
                f"Datos válidos con {len(validation.warnings)} advertencia(s)."
            )
        else:
            findings.append("Datos válidos sin errores ni advertencias.")

        # Performance alerts
        red_alerts = [a for a in alerts if a.alert_level in (AlertLevel.RED, AlertLevel.CRITICAL)]
        yellow_alerts = [a for a in alerts if a.alert_level == AlertLevel.YELLOW]
        if red_alerts:
            findings.append(f"🔴 {len(red_alerts)} alerta(s) de rendimiento crítica(s).")
        if yellow_alerts:
            findings.append(f"🟡 {len(yellow_alerts)} alerta(s) de rendimiento moderada(s).")

        # Anomalies
        red_anomalies = [a for a in anomalies if a.severity in (AlertLevel.RED, AlertLevel.CRITICAL)]
        if red_anomalies:
            findings.append(f"🔴 {len(red_anomalies)} anomalía(s) severa(s) detectada(s).")

        total_anomalies = len(anomalies)
        if total_anomalies > 0:
            categories = Counter(a.category for a in anomalies)
            cat_str = ", ".join(f"{cat}: {cnt}" for cat, cnt in categories.most_common())
            findings.append(f"Total de anomalías: {total_anomalies} ({cat_str}).")

        # Discharge summary
        discharge_anomalies = [a for a in anomalies if a.category == "discharge"]
        if discharge_anomalies:
            findings.append(
                f"Se detectaron {len(discharge_anomalies)} evento(s) de descarga sospechoso(s)."
            )

        return findings

    # --- Critical Vehicles Ranking ---

    def _rank_critical_vehicles(
        self,
        alerts: list[PerformanceAlert],
        anomalies: list[AnomalyFinding],
    ) -> list[dict[str, Any]]:
        vehicle_scores: Counter[str] = Counter()

        severity_weights = {
            AlertLevel.GREEN: 0,
            AlertLevel.YELLOW: 1,
            AlertLevel.RED: 3,
            AlertLevel.CRITICAL: 5,
        }

        for alert in alerts:
            vehicle_scores[alert.vehicle_id] += severity_weights.get(alert.alert_level, 0)

        for anomaly in anomalies:
            vehicle_scores[anomaly.vehicle_id] += severity_weights.get(anomaly.severity, 0)

        ranked = []
        for vid, score in vehicle_scores.most_common():
            vid_alerts = [a for a in alerts if a.vehicle_id == vid]
            vid_anomalies = [a for a in anomalies if a.vehicle_id == vid]
            ranked.append({
                "vehicle_id": vid,
                "risk_score": score,
                "alert_count": len(vid_alerts),
                "anomaly_count": len(vid_anomalies),
                "top_issues": [
                    a.description for a in sorted(
                        vid_anomalies, key=lambda x: severity_weights.get(x.severity, 0), reverse=True
                    )[:3]
                ],
            })

        return ranked

    # --- Recommendations ---

    def _build_recommendations(
        self,
        anomalies: list[AnomalyFinding],
        alerts: list[PerformanceAlert],
    ) -> list[str]:
        recs: list[str] = []
        seen: set[str] = set()

        # Collect unique recommendations from anomalies
        for anomaly in anomalies:
            if anomaly.recommendation and anomaly.recommendation not in seen:
                recs.append(anomaly.recommendation)
                seen.add(anomaly.recommendation)

        # Add general recommendations based on patterns
        categories = Counter(a.category for a in anomalies)

        if categories.get("discharge", 0) >= 2:
            rec = "Implementar monitoreo en tiempo real de descargas con alertas inmediatas."
            if rec not in seen:
                recs.append(rec)
                seen.add(rec)

        if categories.get("sensor", 0) >= 1:
            rec = "Programar mantenimiento preventivo de sensores de combustible."
            if rec not in seen:
                recs.append(rec)
                seen.add(rec)

        if categories.get("unauthorized_load", 0) >= 1:
            rec = "Revisar y reforzar la política de autorización de cargas de combustible."
            if rec not in seen:
                recs.append(rec)
                seen.add(rec)

        high_idle = [a for a in alerts if a.metric == "idle_ratio"]
        if high_idle:
            rec = "Capacitar operadores en reducción de tiempos de ralentí."
            if rec not in seen:
                recs.append(rec)
                seen.add(rec)

        return recs

    # --- Executive Summary ---

    def _build_executive_summary(
        self,
        report: TelemetryReport,
        validation: ValidationResult,
        alerts: list[PerformanceAlert],
        anomalies: list[AnomalyFinding],
    ) -> str:
        period = format_period(report.period_start, report.period_end)
        n_vehicles = len(report.vehicles)
        n_alerts = len(alerts)
        n_anomalies = len(anomalies)

        red_count = sum(
            1 for a in anomalies if a.severity in (AlertLevel.RED, AlertLevel.CRITICAL)
        ) + sum(
            1 for a in alerts if a.alert_level in (AlertLevel.RED, AlertLevel.CRITICAL)
        )

        lines = [
            "═══════════════════════════════════════════════════════",
            f"  RESUMEN EJECUTIVO — {report.client}",
            f"  Periodo: {period}",
            f"  Proveedor de datos: {report.provider}",
            "═══════════════════════════════════════════════════════",
            "",
            f"  Vehículos analizados: {n_vehicles}",
            f"  Estado de validación: {validation.status.upper()}",
            f"  Alertas de rendimiento: {n_alerts}",
            f"  Anomalías detectadas: {n_anomalies}",
            f"  Hallazgos críticos (rojo/crítico): {red_count}",
            "",
        ]

        if red_count > 0:
            lines.append("  ⚠ SE REQUIERE ATENCIÓN INMEDIATA ⚠")
        else:
            lines.append("  ✓ Sin hallazgos críticos en este periodo.")

        lines.append("═══════════════════════════════════════════════════════")

        return "\n".join(lines)
