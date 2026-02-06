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
} from "lucide-react";

// Default sample report that matches the sample_report.json file
const SAMPLE_REPORT = {
  cliente: "Empresa Demo",
  periodo: "01-02-2025 a 07-02-2025",
  indicadores: {
    distancia_total_km: 3200,
    consumo_total_litros: 450,
    excesos_velocidad: 12,
    tiempo_ralenti_minutos: 340,
    frenadas_bruscas: 8,
  },
  vehiculos: [
    {
      placa: "ABC123",
      distancia_km: 1200,
      consumo_litros: 160,
      excesos_velocidad: 7,
    },
    {
      placa: "XYZ789",
      distancia_km: 2000,
      consumo_litros: 290,
      excesos_velocidad: 5,
    },
  ],
};

// Backend API URL - uses environment variable or defaults to localhost
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

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
    // Validate JSON first
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
              <span className="profile-btn__label">Visión ejecutiva</span>
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

              {parsedReport.indicadores && (
                <div className="indicators">
                  <div className="indicator">
                    <div className="indicator__value">
                      {parsedReport.indicadores.distancia_total_km?.toLocaleString()}
                    </div>
                    <div className="indicator__label">Km Totales</div>
                  </div>
                  <div className="indicator">
                    <div className="indicator__value">
                      {parsedReport.indicadores.consumo_total_litros}
                    </div>
                    <div className="indicator__label">Litros Consumidos</div>
                  </div>
                  <div className="indicator">
                    <div className="indicator__value" style={{ color: "var(--color-danger)" }}>
                      {parsedReport.indicadores.excesos_velocidad}
                    </div>
                    <div className="indicator__label">Excesos Velocidad</div>
                  </div>
                  <div className="indicator">
                    <div className="indicator__value" style={{ color: "var(--color-warning)" }}>
                      {parsedReport.indicadores.tiempo_ralenti_minutos}
                    </div>
                    <div className="indicator__label">Min. Ralentí</div>
                  </div>
                  <div className="indicator">
                    <div className="indicator__value" style={{ color: "var(--color-danger)" }}>
                      {parsedReport.indicadores.frenadas_bruscas}
                    </div>
                    <div className="indicator__label">Frenadas Bruscas</div>
                  </div>
                </div>
              )}

              {parsedReport.vehiculos && (
                <div style={{ marginTop: "1.25rem" }}>
                  <h3 style={{
                    fontSize: "0.85rem",
                    fontWeight: 600,
                    color: "var(--color-text-secondary)",
                    marginBottom: "0.5rem",
                  }}>
                    Vehículos ({parsedReport.vehiculos.length})
                  </h3>
                  {parsedReport.vehiculos.map((v, i) => (
                    <div
                      key={i}
                      style={{
                        background: "var(--color-bg)",
                        borderRadius: "var(--radius-sm)",
                        padding: "0.75rem",
                        marginBottom: "0.5rem",
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        fontSize: "0.85rem",
                      }}
                    >
                      <strong>{v.placa}</strong>
                      <span style={{ color: "var(--color-text-secondary)" }}>
                        {v.distancia_km} km · {v.consumo_litros} L · {v.excesos_velocidad} excesos
                      </span>
                    </div>
                  ))}
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
