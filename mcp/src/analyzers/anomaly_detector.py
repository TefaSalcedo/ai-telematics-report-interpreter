"""
Anomaly detection module for fleet telemetry data.

Detects:
  A. Fuel discharge anomalies (repeated location, engine off, gradual drops)
  B. Unauthorized loads (load/trip ratio, unusual locations, atypical volumes)
  C. Sensor behavior issues (irregular fluctuations, impossible jumps)
  D. Temporal patterns (anomalies concentrated by unit, location, time, route)
"""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from src.models.telemetry import (
    AlertLevel,
    AnomalyFinding,
    FuelEvent,
    TelemetryReport,
    VehicleData,
)
from src.utils.helpers import (
    generate_id,
    locations_are_close,
    mean,
    parse_iso_date,
    std_dev,
)


class AnomalyDetector:
    """Detects anomalies across all vehicles in a telemetry report."""

    def detect(self, report: TelemetryReport) -> list[AnomalyFinding]:
        """Run all anomaly detection routines and return findings."""
        findings: list[AnomalyFinding] = []
        for vehicle in report.vehicles:
            findings.extend(self._detect_discharge_anomalies(vehicle))
            findings.extend(self._detect_unauthorized_loads(vehicle))
            findings.extend(self._detect_sensor_issues(vehicle))
            findings.extend(self._detect_temporal_patterns(vehicle))
        return findings

    # --- A. DISCHARGE ANOMALIES ---

    def _detect_discharge_anomalies(self, vehicle: VehicleData) -> list[AnomalyFinding]:
        findings: list[AnomalyFinding] = []
        vid = vehicle.vehicle_id
        discharges = [e for e in vehicle.fuel_events if e.event_type == "discharge"]

        if not discharges:
            return findings

        # A1. Repeated discharges at the same location
        location_groups: dict[str, list[FuelEvent]] = defaultdict(list)
        for d in discharges:
            if d.location:
                key = f"{d.location.latitude:.3f},{d.location.longitude:.3f}"
                location_groups[key].append(d)

        for loc_key, events in location_groups.items():
            if len(events) >= 2:
                total_vol = sum(e.volume_liters for e in events)
                findings.append(AnomalyFinding(
                    anomaly_id=generate_id("DSC"),
                    category="discharge",
                    severity=AlertLevel.RED if len(events) >= 3 else AlertLevel.YELLOW,
                    vehicle_id=vid,
                    description=(
                        f"Se detectaron {len(events)} descargas en la misma ubicación "
                        f"({events[0].location.address if events[0].location else loc_key}), "
                        f"total: {total_vol:.1f}L."
                    ),
                    evidence={
                        "location": loc_key,
                        "event_count": len(events),
                        "total_volume_liters": total_vol,
                        "event_ids": [e.event_id for e in events],
                    },
                    possible_causes=[
                        "Posible robo de combustible",
                        "Punto de drenaje no autorizado",
                        "Fuga en la ubicación de estacionamiento",
                    ],
                    recommendation="Investigar la ubicación y revisar cámaras de seguridad.",
                ))

        # A2. Discharges with engine off
        engine_off_discharges = [d for d in discharges if not d.engine_running]
        if engine_off_discharges:
            for d in engine_off_discharges:
                ts = parse_iso_date(d.timestamp)
                hour = ts.hour if ts else -1
                is_night = 22 <= hour or hour <= 5
                severity = AlertLevel.RED if is_night else AlertLevel.YELLOW
                findings.append(AnomalyFinding(
                    anomaly_id=generate_id("DSC"),
                    category="discharge",
                    severity=severity,
                    vehicle_id=vid,
                    description=(
                        f"Descarga de {d.volume_liters:.1f}L con motor apagado "
                        f"({'horario nocturno' if is_night else 'horario diurno'}) "
                        f"en {d.location.address if d.location else 'ubicación desconocida'}."
                    ),
                    evidence={
                        "event_id": d.event_id,
                        "volume_liters": d.volume_liters,
                        "engine_running": d.engine_running,
                        "hour": hour,
                        "is_night": is_night,
                    },
                    possible_causes=[
                        "Robo de combustible",
                        "Drenaje por mantenimiento no registrado",
                        "Error de sensor",
                    ],
                    recommendation="Verificar con el operador y revisar registros de mantenimiento.",
                ))

        # A3. Small but frequent discharges (possible leak)
        small_discharges = [d for d in discharges if d.volume_liters < 50]
        if len(small_discharges) >= 3:
            total_small = sum(d.volume_liters for d in small_discharges)
            findings.append(AnomalyFinding(
                anomaly_id=generate_id("DSC"),
                category="discharge",
                severity=AlertLevel.YELLOW,
                vehicle_id=vid,
                description=(
                    f"Se detectaron {len(small_discharges)} descargas pequeñas (<50L) "
                    f"que suman {total_small:.1f}L. Posible fuga gradual."
                ),
                evidence={
                    "count": len(small_discharges),
                    "total_volume": total_small,
                    "event_ids": [d.event_id for d in small_discharges],
                },
                possible_causes=[
                    "Fuga lenta en el tanque o líneas de combustible",
                    "Sensor con lecturas erráticas",
                    "Robo hormiga",
                ],
                recommendation="Inspeccionar tanque y conexiones físicamente.",
            ))

        return findings

    # --- B. UNAUTHORIZED LOADS ---

    def _detect_unauthorized_loads(self, vehicle: VehicleData) -> list[AnomalyFinding]:
        findings: list[AnomalyFinding] = []
        vid = vehicle.vehicle_id
        loads = [e for e in vehicle.fuel_events if e.event_type == "load"]
        trips = vehicle.performance.number_of_trips

        if not loads:
            return findings

        # B1. Load/trip ratio anomaly
        if trips > 0:
            ratio = len(loads) / trips
            if ratio > 0.6:
                findings.append(AnomalyFinding(
                    anomaly_id=generate_id("ULD"),
                    category="unauthorized_load",
                    severity=AlertLevel.YELLOW,
                    vehicle_id=vid,
                    description=(
                        f"Ratio cargas/viajes alto: {len(loads)} cargas para {trips} viajes "
                        f"(ratio={ratio:.2f})."
                    ),
                    evidence={"loads": len(loads), "trips": trips, "ratio": round(ratio, 2)},
                    possible_causes=[
                        "Cargas innecesarias o no planificadas",
                        "Posible reventa de combustible",
                    ],
                    recommendation="Revisar política de carga y comparar con rutas asignadas.",
                ))

        # B2. Atypical load volumes
        volumes = [l.volume_liters for l in loads]
        if len(volumes) >= 2:
            avg_vol = mean(volumes)
            sd = std_dev(volumes)
            for load_event in loads:
                if sd > 0 and abs(load_event.volume_liters - avg_vol) > 2 * sd:
                    findings.append(AnomalyFinding(
                        anomaly_id=generate_id("ULD"),
                        category="unauthorized_load",
                        severity=AlertLevel.YELLOW,
                        vehicle_id=vid,
                        description=(
                            f"Volumen de carga atípico: {load_event.volume_liters:.1f}L "
                            f"(promedio={avg_vol:.1f}L, σ={sd:.1f}L) en evento {load_event.event_id}."
                        ),
                        evidence={
                            "event_id": load_event.event_id,
                            "volume": load_event.volume_liters,
                            "mean": round(avg_vol, 1),
                            "std_dev": round(sd, 1),
                        },
                        possible_causes=[
                            "Carga parcial no planificada",
                            "Error en el registro del sensor",
                        ],
                        recommendation="Verificar factura de carga contra volumen registrado.",
                    ))

        # B3. Load exceeding tank capacity
        tank = vehicle.tank_capacity_liters
        for load_event in loads:
            if load_event.fuel_level_after > tank * 1.05:
                findings.append(AnomalyFinding(
                    anomaly_id=generate_id("ULD"),
                    category="unauthorized_load",
                    severity=AlertLevel.RED,
                    vehicle_id=vid,
                    description=(
                        f"Nivel post-carga ({load_event.fuel_level_after:.1f}L) excede "
                        f"capacidad del tanque ({tank}L) en evento {load_event.event_id}."
                    ),
                    evidence={
                        "event_id": load_event.event_id,
                        "fuel_level_after": load_event.fuel_level_after,
                        "tank_capacity": tank,
                    },
                    possible_causes=[
                        "Error de calibración del sensor",
                        "Dato incorrecto del proveedor",
                    ],
                    recommendation="Recalibrar sensor y verificar datos con el proveedor.",
                ))

        return findings

    # --- C. SENSOR BEHAVIOR ---

    def _detect_sensor_issues(self, vehicle: VehicleData) -> list[AnomalyFinding]:
        findings: list[AnomalyFinding] = []
        vid = vehicle.vehicle_id
        events = sorted(vehicle.fuel_events, key=lambda e: e.timestamp)

        if len(events) < 2:
            return findings

        # C1. Impossible jumps between consecutive events
        for i in range(1, len(events)):
            prev = events[i - 1]
            curr = events[i]

            # The "after" of previous should be close to "before" of current
            gap = abs(curr.fuel_level_before - prev.fuel_level_after)
            if gap > 20 and curr.event_type != "load":
                findings.append(AnomalyFinding(
                    anomaly_id=generate_id("SNS"),
                    category="sensor",
                    severity=AlertLevel.YELLOW if gap < 50 else AlertLevel.RED,
                    vehicle_id=vid,
                    description=(
                        f"Salto abrupto de nivel entre eventos {prev.event_id} y {curr.event_id}: "
                        f"de {prev.fuel_level_after:.1f}L a {curr.fuel_level_before:.1f}L "
                        f"(diferencia={gap:.1f}L)."
                    ),
                    evidence={
                        "prev_event": prev.event_id,
                        "curr_event": curr.event_id,
                        "prev_level_after": prev.fuel_level_after,
                        "curr_level_before": curr.fuel_level_before,
                        "gap_liters": round(gap, 1),
                    },
                    possible_causes=[
                        "Falla del sensor de combustible",
                        "Consumo no registrado entre eventos",
                        "Posible manipulación del sensor",
                    ],
                    recommendation="Revisar historial continuo del sensor y verificar integridad física.",
                ))

            # C2. Odometer regression
            if curr.odometer_km < prev.odometer_km:
                findings.append(AnomalyFinding(
                    anomaly_id=generate_id("SNS"),
                    category="sensor",
                    severity=AlertLevel.RED,
                    vehicle_id=vid,
                    description=(
                        f"Regresión de odómetro entre {prev.event_id} ({prev.odometer_km}km) "
                        f"y {curr.event_id} ({curr.odometer_km}km)."
                    ),
                    evidence={
                        "prev_event": prev.event_id,
                        "curr_event": curr.event_id,
                        "prev_odometer": prev.odometer_km,
                        "curr_odometer": curr.odometer_km,
                    },
                    possible_causes=[
                        "Manipulación del odómetro",
                        "Error de transmisión de datos",
                    ],
                    recommendation="Verificar integridad del odómetro y datos GPS.",
                ))

        # C3. Consumption by movement vs total consumption mismatch
        consumption_events = [e for e in events if e.event_type == "consumption"]
        total_consumption_events = sum(e.volume_liters for e in consumption_events)
        reported_consumption = vehicle.fuel_summary.total_fuel_consumed_liters

        if reported_consumption > 0 and total_consumption_events > 0:
            diff_pct = abs(total_consumption_events - reported_consumption) / reported_consumption * 100
            if diff_pct > 15:
                findings.append(AnomalyFinding(
                    anomaly_id=generate_id("SNS"),
                    category="sensor",
                    severity=AlertLevel.YELLOW,
                    vehicle_id=vid,
                    description=(
                        f"Discrepancia entre consumo por eventos ({total_consumption_events:.1f}L) "
                        f"y consumo total reportado ({reported_consumption:.1f}L): {diff_pct:.1f}%."
                    ),
                    evidence={
                        "events_consumption": round(total_consumption_events, 1),
                        "reported_consumption": reported_consumption,
                        "difference_pct": round(diff_pct, 1),
                    },
                    possible_causes=[
                        "Eventos de consumo no registrados",
                        "Error de acumulación del sensor",
                    ],
                    recommendation="Solicitar datos crudos del sensor para verificación.",
                ))

        return findings

    # --- D. TEMPORAL PATTERNS ---

    def _detect_temporal_patterns(self, vehicle: VehicleData) -> list[AnomalyFinding]:
        findings: list[AnomalyFinding] = []
        vid = vehicle.vehicle_id
        discharges = [e for e in vehicle.fuel_events if e.event_type == "discharge"]

        if not discharges:
            return findings

        # D1. Discharges concentrated at specific hours
        hours: list[int] = []
        for d in discharges:
            ts = parse_iso_date(d.timestamp)
            if ts:
                hours.append(ts.hour)

        if hours:
            hour_counts = Counter(hours)
            most_common_hour, count = hour_counts.most_common(1)[0]
            if count >= 2:
                findings.append(AnomalyFinding(
                    anomaly_id=generate_id("TMP"),
                    category="temporal_pattern",
                    severity=AlertLevel.YELLOW,
                    vehicle_id=vid,
                    description=(
                        f"Patrón temporal: {count} descargas concentradas alrededor de las "
                        f"{most_common_hour:02d}:00h."
                    ),
                    evidence={
                        "hour": most_common_hour,
                        "count": count,
                        "hour_distribution": dict(hour_counts),
                    },
                    possible_causes=[
                        "Patrón de robo recurrente",
                        "Rutina operativa que genera descargas",
                    ],
                    recommendation="Correlacionar con turnos de operadores y vigilancia.",
                ))

        # D2. Anomalies concentrated on specific routes
        route_events: dict[str, int] = defaultdict(int)
        for d in discharges:
            if d.location and d.location.address:
                route_events[d.location.address] += 1

        for route, count in route_events.items():
            if count >= 2:
                findings.append(AnomalyFinding(
                    anomaly_id=generate_id("TMP"),
                    category="temporal_pattern",
                    severity=AlertLevel.YELLOW,
                    vehicle_id=vid,
                    description=(
                        f"Patrón geográfico: {count} descargas asociadas a '{route}'."
                    ),
                    evidence={"location": route, "count": count},
                    possible_causes=[
                        "Punto de drenaje recurrente",
                        "Zona con problemas de seguridad",
                    ],
                    recommendation="Evaluar seguridad en la ruta/ubicación indicada.",
                ))

        return findings
