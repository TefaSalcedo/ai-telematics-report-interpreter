import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import {
  Brain,
  FileText,
  UserCog,
  Briefcase,
  Wrench,
  Sparkles,
  Upload,
  BarChart3,
  Fuel,
  AlertTriangle,
  TrendingDown,
} from "lucide-react";

// Default sample report matching real Wialon telematics data
const SAMPLE_REPORT = {
  cliente: "TransLogística S.A.",
  periodo: "27-01-2025 a 02-02-2025",
  promedios_flota: {
    viajes_totales: 557,
    consumo_viajes_gal: 1142.3,
    consumo_movimiento_gal: 1225.5,
    consumo_sin_movimiento_gal: 427.1,
    horas_motor_encendido: 37.3,
    total_llenados: 1524,
    total_descargas: 323,
    distancia_total_km: 8190,
  },
  rendimiento: {
    rendimiento_actual_km_gal: 5.9,
    rendimiento_anterior_km_gal: 9.7,
    consumo_total_gal: 1385.4,
    consumo_semana_anterior_gal: 809.0,
    consumo_esperado_gal: 846.3,
    desviacion_gal: 539.1,
  },
  anomalias_combustible: [
    { unidad: "SOS012", ubicacion_inicial: "Guayabetal, Cundinamarca", ubicacion_final: "Guayabetal, Cundinamarca", tanque: "Tanque izquierdo", cantidad_gal: 51.2 },
    { unidad: "USB890", ubicacion_inicial: "Guayabetal, Cundinamarca", ubicacion_final: "Guayabetal, Cundinamarca", tanque: "Tanque total", cantidad_gal: 46.0 },
    { unidad: "USB890", ubicacion_inicial: "Guayabetal, Cundinamarca", ubicacion_final: "Guayabetal, Cundinamarca", tanque: "Tanque total", cantidad_gal: 41.3 },
    { unidad: "SOS012", ubicacion_inicial: "Vía Bogotá - Villavicencio", ubicacion_final: "Vía Bogotá - Villavicencio", tanque: "Tanque izquierdo", cantidad_gal: 37.0 },
    { unidad: "TAM273", ubicacion_inicial: "Chipaque, La Caldera", ubicacion_final: "Chipaque, La Caldera", tanque: "Tanque Derecho", cantidad_gal: 17.7 },
    { unidad: "TAM273", ubicacion_inicial: "Guayabetal", ubicacion_final: "Guayabetal", tanque: "Tanque Izquierdo", cantidad_gal: 11.6 },
  ],
  cargas_no_autorizadas: [
    { unidad: "TAM273", ubicacion: "Vía Bogotá - Funza, Mosquera", cantidad_gal: 196.4, num_cargas: 2 },
    { unidad: "USB890", ubicacion: "Zona Guayabetal", cantidad_gal: 143.2, num_cargas: 5 },
    { unidad: "TAM691", ubicacion: "Múltiples ubicaciones", cantidad_gal: 133.3, num_cargas: 6 },
    { unidad: "JKU614", ubicacion: "Múltiples ubicaciones", cantidad_gal: 130.3, num_cargas: 5 },
    { unidad: "FSU329", ubicacion: "Av. Calle 71B Sur", cantidad_gal: 118.4, num_cargas: 5 },
  ],
  resumen_vehiculos: [
    { unidad: "TAM273", eventos_descarga: 16, total_descarga_gal: 108.1, eventos_carga_no_autorizada: 2, total_carga_no_autorizada_gal: 196.4 },
    { unidad: "USB890", eventos_descarga: 5, total_descarga_gal: 95.8, eventos_carga_no_autorizada: 5, total_carga_no_autorizada_gal: 143.2 },
    { unidad: "SOS012", eventos_descarga: 2, total_descarga_gal: 88.2, eventos_carga_no_autorizada: 0, total_carga_no_autorizada_gal: 0 },
    { unidad: "FSU329", eventos_descarga: 5, total_descarga_gal: 12.1, eventos_carga_no_autorizada: 5, total_carga_no_autorizada_gal: 118.4 },
    { unidad: "SQY562", eventos_descarga: 4, total_descarga_gal: 14.9, eventos_carga_no_autorizada: 0, total_carga_no_autorizada_gal: 0 },
  ],
};

// Backend API URL - uses environment variable or defaults to localhost
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

// Severity badge based on TOTAL gallons (discharges + unauthorized loads)
// Thresholds MUST match prompt section 7 to avoid UI/LLM discrepancy
const SeverityBadge = ({ gal, events }) => {
  let color, label;
  // Escalation: >5 events regardless of gallons → one level up
  const escalated = events > 5;
  if (gal > 50 || (escalated && gal > 20)) { color = "#ef4444"; label = "CRÍTICO"; }
  else if (gal > 20 || (escalated && gal > 10)) { color = "#f59e0b"; label = "ALTO"; }
  else if (gal > 10) { color = "#3b82f6"; label = "MEDIO"; }
  else { color = "#94a3b8"; label = "BAJO"; }
  return (
    <span
      title={`Total: ${gal.toFixed(1)} gal | ${events} eventos${escalated ? " (escalado por >5 eventos)" : ""}`}
      style={{
        background: `${color}22`,
        color: color,
        padding: "2px 8px",
        borderRadius: "4px",
        fontSize: "0.65rem",
        fontWeight: 700,
        letterSpacing: "0.5px",
        cursor: "help",
      }}
    >{label}</span>
  );
};

function App() {
  const [jsonText, setJsonText] = useState(
    JSON.stringify(SAMPLE_REPORT, null, 2)
  );
  const [profile, setProfile] = useState("gerente");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [parsedReport, setParsedReport] = useState(SAMPLE_REPORT);

  // Validate and parse JSON whenever the text changes
  const handleJsonChange = (text) => {
    setJsonText(text);
    setError(null);
    try {
      const parsed = JSON.parse(text);
      setParsedReport(parsed);
    } catch {
      setParsedReport(null);
    }
  };

  // Load the sample report into the text area
  const handleLoadSample = () => {
    const sample = JSON.stringify(SAMPLE_REPORT, null, 2);
    setJsonText(sample);
    setParsedReport(SAMPLE_REPORT);
    setError(null);
  };

  // Send the report to the backend for AI interpretation
  const handleInterpret = async () => {
    let reportData;
    try {
      reportData = JSON.parse(jsonText);
    } catch {
      setError("El JSON ingresado no es válido. Revisa el formato.");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/interpret`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          report: reportData,
          profile: profile,
        }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(
          errData.detail || `Error del servidor: ${response.status}`
        );
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(
        err.message || "Error al conectar con el servidor. ¿Está corriendo el backend?"
      );
    } finally {
      setLoading(false);
    }
  };

  // Calculate totals for preview
  const totalDescargas = parsedReport?.resumen_vehiculos?.reduce((s, v) => s + (v.total_descarga_gal || 0), 0) || 0;
  const totalCargasNA = parsedReport?.resumen_vehiculos?.reduce((s, v) => s + (v.total_carga_no_autorizada_gal || 0), 0) || 0;

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <h1 className="header__title">
          <Brain style={{ display: "inline", verticalAlign: "middle" }} />
          {" "}AI Telematics Report Interpreter
        </h1>
        <p className="header__subtitle">
          Interpreta reportes de telemetría con inteligencia artificial
        </p>
      </header>

      <div className="grid">
        {/* Left Column: Input */}
        <div className="card">
          <h2 className="card__title">
            <UserCog /> Perfil de Usuario
          </h2>

          {/* Profile Selector */}
          <div className="profile-selector">
            <button
              className={`profile-btn ${profile === "gerente" ? "profile-btn--active" : ""}`}
              onClick={() => setProfile("gerente")}
            >
              <Briefcase size={20} />
              Gerente de Flota
              <span className="profile-btn__label">Costos y pérdidas</span>
            </button>
            <button
              className={`profile-btn ${profile === "operaciones" ? "profile-btn--active" : ""}`}
              onClick={() => setProfile("operaciones")}
            >
              <Wrench size={20} />
              Jefe de Operaciones
              <span className="profile-btn__label">Detalle técnico</span>
            </button>
          </div>

          <h2 className="card__title" style={{ marginTop: "1rem" }}>
            <FileText /> Datos del Reporte (JSON)
          </h2>

          {/* JSON Text Area */}
          <textarea
            className={`json-input ${error && !parsedReport ? "json-input--error" : ""}`}
            value={jsonText}
            onChange={(e) => handleJsonChange(e.target.value)}
            placeholder='Pega aquí tu JSON de reporte...'
            spellCheck={false}
          />

          {/* Action Buttons */}
          <div className="btn-row">
            <button className="btn btn--secondary" onClick={handleLoadSample}>
              <Upload size={16} /> Cargar Ejemplo
            </button>
            <button
              className="btn btn--primary"
              onClick={handleInterpret}
              disabled={loading || !parsedReport}
            >
              {loading ? (
                <>
                  <span className="spinner" /> Interpretando...
                </>
              ) : (
                <>
                  <Sparkles size={16} /> Interpretar con AI
                </>
              )}
            </button>
          </div>

          {error && <div className="error">{error}</div>}
        </div>

        {/* Right Column: Data Preview */}
        <div className="card">
          <h2 className="card__title">
            <BarChart3 /> Vista Previa del Reporte
          </h2>

          {parsedReport ? (
            <>
              <p style={{ color: "var(--color-text-secondary)", fontSize: "0.85rem" }}>
                <strong style={{ color: "var(--color-text)" }}>
                  {parsedReport.cliente}
                </strong>{" "}
                — {parsedReport.periodo}
              </p>

              {/* Fleet Averages */}
              {parsedReport.promedios_flota && (
                <div className="indicators" style={{ marginTop: "0.75rem" }}>
                  <div className="indicator">
                    <div className="indicator__value">
                      {parsedReport.promedios_flota.distancia_total_km?.toLocaleString()}
                    </div>
                    <div className="indicator__label">Km Totales</div>
                  </div>
                  <div className="indicator">
                    <div className="indicator__value">
                      {parsedReport.promedios_flota.viajes_totales}
                    </div>
                    <div className="indicator__label">Viajes</div>
                  </div>
                  <div className="indicator">
                    <div className="indicator__value" style={{ color: "var(--color-warning)" }}>
                      {parsedReport.promedios_flota.total_descargas}
                    </div>
                    <div className="indicator__label">Descargas</div>
                  </div>
                  <div className="indicator">
                    <div className="indicator__value">
                      {parsedReport.promedios_flota.total_llenados}
                    </div>
                    <div className="indicator__label">Llenados</div>
                  </div>
                </div>
              )}

              {/* Fuel Performance */}
              {parsedReport.rendimiento && (
                <div style={{ marginTop: "1rem" }}>
                  <h3 style={{ fontSize: "0.8rem", fontWeight: 600, color: "var(--color-text-secondary)", marginBottom: "0.5rem", display: "flex", alignItems: "center", gap: "0.4rem" }}>
                    <Fuel size={14} /> Rendimiento de Combustible
                  </h3>
                  <div className="indicators">
                    <div className="indicator">
                      <div className="indicator__value" style={{ color: "var(--color-danger)" }}>
                        {parsedReport.rendimiento.rendimiento_actual_km_gal}
                      </div>
                      <div className="indicator__label">km/gal Actual</div>
                    </div>
                    <div className="indicator">
                      <div className="indicator__value" style={{ color: "var(--color-success)" }}>
                        {parsedReport.rendimiento.rendimiento_anterior_km_gal}
                      </div>
                      <div className="indicator__label">km/gal Anterior</div>
                    </div>
                    <div className="indicator">
                      <div className="indicator__value" style={{ color: "var(--color-danger)" }}>
                        {parsedReport.rendimiento.consumo_total_gal}
                      </div>
                      <div className="indicator__label">Gal Consumidos</div>
                    </div>
                    <div className="indicator">
                      <div className="indicator__value" style={{ color: "var(--color-warning)" }}>
                        +{parsedReport.rendimiento.desviacion_gal}
                      </div>
                      <div className="indicator__label">Gal Desviación</div>
                    </div>
                  </div>
                </div>
              )}

              {/* Vehicle Anomaly Summary */}
              {parsedReport.resumen_vehiculos && (
                <div style={{ marginTop: "1rem" }}>
                  <h3 style={{ fontSize: "0.8rem", fontWeight: 600, color: "var(--color-text-secondary)", marginBottom: "0.5rem", display: "flex", alignItems: "center", gap: "0.4rem" }}>
                    <AlertTriangle size={14} /> Vehículos con Anomalías ({parsedReport.resumen_vehiculos.length})
                  </h3>
                  <div style={{ display: "flex", gap: "0.5rem", marginBottom: "0.5rem", fontSize: "0.75rem" }}>
                    <span style={{ background: "rgba(239,68,68,0.1)", color: "var(--color-danger)", padding: "4px 10px", borderRadius: "6px" }}>
                      Descargas: {totalDescargas.toFixed(1)} gal
                    </span>
                    <span style={{ background: "rgba(245,158,11,0.1)", color: "var(--color-warning)", padding: "4px 10px", borderRadius: "6px" }}>
                      Cargas N/A: {totalCargasNA.toFixed(1)} gal
                    </span>
                  </div>
                  {parsedReport.resumen_vehiculos.map((v, i) => (
                    <div
                      key={i}
                      style={{
                        background: "var(--color-bg)",
                        borderRadius: "var(--radius-sm)",
                        padding: "0.6rem 0.75rem",
                        marginBottom: "0.4rem",
                        fontSize: "0.8rem",
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                      }}
                    >
                      <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                        <strong>{v.unidad}</strong>
                        <SeverityBadge
                          gal={(v.total_descarga_gal || 0) + (v.total_carga_no_autorizada_gal || 0)}
                          events={(v.eventos_descarga || 0) + (v.eventos_carga_no_autorizada || 0)}
                        />
                      </div>
                      <span style={{ color: "var(--color-text-secondary)", fontSize: "0.75rem" }}>
                        {v.eventos_descarga} desc. ({v.total_descarga_gal} gal)
                        {v.total_carga_no_autorizada_gal > 0 && (
                          <> · {v.eventos_carga_no_autorizada} cargas N/A ({v.total_carga_no_autorizada_gal} gal)</>
                        )}
                      </span>
                    </div>
                  ))}
                </div>
              )}

              {/* Anomaly count */}
              {parsedReport.anomalias_combustible && (
                <div style={{ marginTop: "0.75rem", fontSize: "0.75rem", color: "var(--color-text-secondary)", display: "flex", alignItems: "center", gap: "0.4rem" }}>
                  <TrendingDown size={14} />
                  {parsedReport.anomalias_combustible.length} eventos de anomalía detallados en el JSON
                </div>
              )}
            </>
          ) : (
            <div className="empty-state">
              <FileText size={48} />
              <p>Ingresa un JSON válido para ver la vista previa</p>
            </div>
          )}
        </div>

        {/* Full Width: AI Result */}
        {result && (
          <div className="card result">
            <h2 className="card__title">
              <Sparkles /> Interpretación AI —{" "}
              {result.profile === "gerente"
                ? "Gerente de Flota"
                : "Jefe de Operaciones"}
            </h2>
            <div className="result__content">
              <ReactMarkdown>{result.interpretation}</ReactMarkdown>
            </div>
            <div className="result__meta">
              <span>Modelo: {result.model_used}</span>
              {result.tokens_used && (
                <span>Tokens usados: {result.tokens_used}</span>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
