"""
Multi-company comparison module.

Compares telemetry data from two different sources (e.g., Empresa A and
TransLogística S.A.) to detect incoherences and validate data consistency.
"""

from __future__ import annotations

from src.models.telemetry import ComparisonResult, TelemetryReport
from src.utils.helpers import deviation_percent, mean


class CompanyComparator:
    """Compares equivalent metrics between two telemetry reports."""

    COHERENCE_THRESHOLD_PCT = 15.0

    def compare(
        self, report_a: TelemetryReport, report_b: TelemetryReport
    ) -> list[ComparisonResult]:
        """Compare two reports and return a list of comparison results."""
        results: list[ComparisonResult] = []

        results.extend(self._compare_fleet_totals(report_a, report_b))
        results.extend(self._compare_matching_vehicles(report_a, report_b))

        return results

    # --- Fleet-Level Comparisons ---

    def _compare_fleet_totals(
        self, report_a: TelemetryReport, report_b: TelemetryReport
    ) -> list[ComparisonResult]:
        results: list[ComparisonResult] = []

        metrics = self._extract_fleet_metrics(report_a, report_b)
        for metric_name, val_a, val_b in metrics:
            diff = val_b - val_a
            diff_pct = deviation_percent(val_a, val_b) if val_a != 0 else 0.0
            is_coherent = abs(diff_pct) <= self.COHERENCE_THRESHOLD_PCT

            note = ""
            if not is_coherent:
                note = (
                    f"Incoherencia detectada: diferencia de {diff_pct:+.1f}% entre fuentes "
                    f"para '{metric_name}'."
                )

            results.append(ComparisonResult(
                metric=metric_name,
                provider_a_value=round(val_a, 2),
                provider_b_value=round(val_b, 2),
                difference=round(diff, 2),
                difference_percent=round(diff_pct, 2),
                is_coherent=is_coherent,
                note=note,
            ))

        return results

    def _extract_fleet_metrics(
        self, report_a: TelemetryReport, report_b: TelemetryReport
    ) -> list[tuple[str, float, float]]:
        """Extract comparable fleet-level metrics from both reports."""
        metrics: list[tuple[str, float, float]] = []

        # Total fuel consumed
        consumed_a = sum(v.fuel_summary.total_fuel_consumed_liters for v in report_a.vehicles)
        consumed_b = sum(v.fuel_summary.total_fuel_consumed_liters for v in report_b.vehicles)
        metrics.append(("total_fuel_consumed_liters", consumed_a, consumed_b))

        # Total fuel loaded
        loaded_a = sum(v.fuel_summary.total_fuel_loaded_liters for v in report_a.vehicles)
        loaded_b = sum(v.fuel_summary.total_fuel_loaded_liters for v in report_b.vehicles)
        metrics.append(("total_fuel_loaded_liters", loaded_a, loaded_b))

        # Total distance
        dist_a = sum(v.performance.distance_km for v in report_a.vehicles)
        dist_b = sum(v.performance.distance_km for v in report_b.vehicles)
        metrics.append(("total_distance_km", dist_a, dist_b))

        # Average performance (km/gal)
        perfs_a = [v.performance.performance_km_per_gallon for v in report_a.vehicles if v.performance.performance_km_per_gallon > 0]
        perfs_b = [v.performance.performance_km_per_gallon for v in report_b.vehicles if v.performance.performance_km_per_gallon > 0]
        if perfs_a and perfs_b:
            metrics.append(("avg_performance_km_per_gallon", mean(perfs_a), mean(perfs_b)))

        return metrics

    # --- Vehicle-Level Comparisons ---

    def _compare_matching_vehicles(
        self, report_a: TelemetryReport, report_b: TelemetryReport
    ) -> list[ComparisonResult]:
        """Compare metrics for vehicles that appear in both reports."""
        results: list[ComparisonResult] = []

        vehicles_b_map = {v.vehicle_id: v for v in report_b.vehicles}

        for va in report_a.vehicles:
            vb = vehicles_b_map.get(va.vehicle_id)
            if vb is None:
                continue

            vid = va.vehicle_id

            vehicle_metrics = [
                (f"{vid}_fuel_consumed", va.fuel_summary.total_fuel_consumed_liters, vb.fuel_summary.total_fuel_consumed_liters),
                (f"{vid}_distance_km", va.performance.distance_km, vb.performance.distance_km),
                (f"{vid}_fuel_loaded", va.fuel_summary.total_fuel_loaded_liters, vb.fuel_summary.total_fuel_loaded_liters),
                (f"{vid}_km_per_gallon", va.performance.performance_km_per_gallon, vb.performance.performance_km_per_gallon),
            ]

            for metric_name, val_a, val_b in vehicle_metrics:
                diff = val_b - val_a
                diff_pct = deviation_percent(val_a, val_b) if val_a != 0 else 0.0
                is_coherent = abs(diff_pct) <= self.COHERENCE_THRESHOLD_PCT

                note = ""
                if not is_coherent:
                    note = (
                        f"Datos inconsistentes entre proveedores para {vid} "
                        f"en métrica '{metric_name}': {diff_pct:+.1f}%."
                    )

                results.append(ComparisonResult(
                    metric=metric_name,
                    provider_a_value=round(val_a, 2),
                    provider_b_value=round(val_b, 2),
                    difference=round(diff, 2),
                    difference_percent=round(diff_pct, 2),
                    is_coherent=is_coherent,
                    note=note,
                ))

        return results
