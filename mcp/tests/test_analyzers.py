"""
Unit tests for performance analyzer and anomaly detector.
"""

import json
from pathlib import Path

import pytest

from src.analyzers.anomaly_detector import AnomalyDetector
from src.analyzers.performance_analyzer import PerformanceAnalyzer
from src.models.telemetry import TelemetryReport


SAMPLE_PATH = Path(__file__).parent.parent / "data" / "sample_report.json"


@pytest.fixture
def sample_report() -> TelemetryReport:
    """Load the sample report for testing."""
    with open(SAMPLE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return TelemetryReport(**data)


class TestPerformanceAnalyzer:
    """Tests for PerformanceAnalyzer."""

    def setup_method(self) -> None:
        self.analyzer = PerformanceAnalyzer()

    def test_returns_alerts(self, sample_report: TelemetryReport) -> None:
        alerts = self.analyzer.analyze(sample_report)
        assert isinstance(alerts, list)
        assert len(alerts) > 0

    def test_alert_has_required_fields(self, sample_report: TelemetryReport) -> None:
        alerts = self.analyzer.analyze(sample_report)
        for alert in alerts:
            assert alert.vehicle_id
            assert alert.alert_level
            assert alert.metric
            assert alert.message

    def test_detects_performance_drop(self, sample_report: TelemetryReport) -> None:
        alerts = self.analyzer.analyze(sample_report)
        perf_alerts = [a for a in alerts if a.metric == "performance_variation"]
        assert len(perf_alerts) > 0


class TestAnomalyDetector:
    """Tests for AnomalyDetector."""

    def setup_method(self) -> None:
        self.detector = AnomalyDetector()

    def test_returns_anomalies(self, sample_report: TelemetryReport) -> None:
        anomalies = self.detector.detect(sample_report)
        assert isinstance(anomalies, list)
        assert len(anomalies) > 0

    def test_detects_discharge_anomalies(self, sample_report: TelemetryReport) -> None:
        anomalies = self.detector.detect(sample_report)
        discharge_anomalies = [a for a in anomalies if a.category == "discharge"]
        assert len(discharge_anomalies) > 0

    def test_anomaly_has_required_fields(self, sample_report: TelemetryReport) -> None:
        anomalies = self.detector.detect(sample_report)
        for anomaly in anomalies:
            assert anomaly.anomaly_id
            assert anomaly.category
            assert anomaly.severity
            assert anomaly.vehicle_id
            assert anomaly.description

    def test_detects_temporal_patterns(self, sample_report: TelemetryReport) -> None:
        anomalies = self.detector.detect(sample_report)
        temporal = [a for a in anomalies if a.category == "temporal_pattern"]
        assert len(temporal) > 0
