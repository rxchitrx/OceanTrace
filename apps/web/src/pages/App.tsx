import { useEffect, useMemo, useState } from "react";
import { fetchCase, fetchCases, runCase } from "../api/client";
import type { AnalysisResult, CasePayload, CaseSummary, Vessel } from "../types";
import { MapView } from "../components/MapView";
import { Timeline } from "../components/Timeline";
import { EvidenceCard } from "../components/EvidenceCard";
import { StepIndicator } from "../components/StepIndicator";

import { LimitationBanner } from "../components/LimitationBanner";

function formatIso(value: string) {
  return (
    new Date(value).toLocaleString("en-IN", {
      dateStyle: "medium",
      timeStyle: "short",
      timeZone: "UTC",
    }) + " UTC"
  );
}

export function App() {
  const [cases, setCases] = useState<CaseSummary[]>([]);
  const [selectedCaseId, setSelectedCaseId] = useState("arabian_sea_demo");
  const [casePayload, setCasePayload] = useState<CasePayload | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [selected, setSelected] = useState<Vessel | null>(null);
  const [status, setStatus] = useState("Loading cases...");
  const [error, setError] = useState<string | null>(null);
  const [activeLayers, setActiveLayers] = useState<string[]>([]);
  const [currentTime, setCurrentTime] = useState<string | null>(null);
  const [sarBounds, setSarBounds] = useState<any | null>(null);
  const [currentStep, setCurrentStep] = useState(1);

  useEffect(() => {
    fetchCases()
      .then((items) => {
        setCases(items);
        if (items.length > 0) {
          setSelectedCaseId(items[0].id);
        }
      })
      .catch(() => setError("Could not load case list. Falling back to offline demo data."))
      .finally(() => setStatus("Ready"));
  }, []);

  useEffect(() => {
    if (!selectedCaseId) {
      return;
    }
    setStatus("Loading case metadata...");
    setCurrentStep(1);
    setResult(null);
    setSelected(null);
    
    fetchCase(selectedCaseId)
      .then((payload) => {
        setCasePayload(payload);
        setActiveLayers(payload.available_layers);
      })
      .catch(() => setError("Could not load case metadata. Using local fallback case."))
      .finally(() => setStatus("Ready"));
      
    // Fetch SAR bounds
    fetch(`/api/cases/${selectedCaseId}/sar/bounds`)
      .then((res) => (res.ok ? res.json() : null))
      .then((bounds) => setSarBounds(bounds))
      .catch(() => setSarBounds(null));
  }, [selectedCaseId]);

  async function handleRunAnalysis() {
    setStatus("Running deterministic analysis...");
    setError(null);
    setCurrentStep(2); // Detect
    try {
      // Simulate pipeline steps for demo visual effect
      await new Promise(r => setTimeout(r, 600));
      setCurrentStep(3); // Drift
      await new Promise(r => setTimeout(r, 800));
      
      const payload = await runCase(selectedCaseId);
      setResult(payload);
      setSelected(payload.vessels[0] ?? null);
      setCurrentTime(payload.release_window.end);
      
      setCurrentStep(4); // Correlate
      setStatus("Analysis complete");
      if (!error) {
        setError(null);
      }
    } catch (runError) {
      setError(runError instanceof Error ? runError.message : "Analysis failed.");
      setStatus("Run failed");
      setCurrentStep(1);
    }
  }

  const heatmapSummary = useMemo(() => {
    if (!result || result.source_region.heatmap_points.length === 0) {
      return "Awaiting analysis run";
    }
    const topPoint = result.source_region.heatmap_points.reduce((best, point) =>
      point.weight > best.weight ? point : best,
    );
    return `${topPoint.weight.toFixed(2)} peak at ${topPoint.latitude.toFixed(3)}, ${topPoint.longitude.toFixed(3)}`;
  }, [result]);

  const toggleLayer = (layer: string) => {
    setActiveLayers((prev) =>
      prev.includes(layer) ? prev.filter((l) => l !== layer) : [...prev, layer]
    );
  };

  return (
    <main className="app-shell">
      <section className="panel left">
        <p className="eyebrow">OceanTrace</p>
        <h1>Investigation Workspace</h1>
        <p className="copy">
          Explainable oil-spill lead generation from slick detection, drift
          reconstruction, and AIS correlation.
        </p>
        <label className="control-block">
          <span>Loaded case</span>
          <select
            value={selectedCaseId}
            onChange={(event) => setSelectedCaseId(event.target.value)}
          >
            {cases.map((item) => (
              <option key={item.id} value={item.id}>
                {item.region} ({item.scenario_type})
              </option>
            ))}
          </select>
        </label>
        
        <StepIndicator currentStep={currentStep} />
        
        <div style={{ marginTop: "20px", display: "flex", flexDirection: "column", gap: "8px" }}>
          <strong>Layers</strong>
          {casePayload?.available_layers.map((layer) => (
            <label key={layer} style={{ display: "flex", alignItems: "center", gap: "8px", cursor: "pointer" }}>
              <input
                type="checkbox"
                checked={activeLayers.includes(layer)}
                onChange={() => toggleLayer(layer)}
              />
              {layer.replace("_", " ")}
            </label>
          ))}
        </div>

        <button className="run-button" style={{ marginTop: "24px", width: "100%" }} onClick={handleRunAnalysis}>
          Run Analysis
        </button>
        <div className="meta-card">
          <p>Status: {status}</p>
          <p>
            Observation:{" "}
            {casePayload ? formatIso(casePayload.manifest.observation_time) : "Loading..."}
          </p>
        </div>
        <LimitationBanner />
        {casePayload ? (
          <div className="meta-card">
            <p>Region: {casePayload.manifest.region}</p>
            <p>Scenario: {casePayload.manifest.scenario_type}</p>
            <p>Notes: {casePayload.manifest.notes.join(" | ")}</p>
          </div>
        ) : null}
        {error ? <div className="error-card">{error}</div> : null}
      </section>

      <section className="panel center">
        <div className="map-card" style={{ display: "flex", flexDirection: "column", height: "100%" }}>
          <div className="map-header">
            <span>Map</span>
            <span>{result?.release_window.confidence_band ?? "pending"} confidence</span>
          </div>
          
          <div style={{ position: "relative", flexGrow: 1, minHeight: "420px", borderRadius: "18px", overflow: "hidden" }}>
            <MapView 
              result={result}
              spillPolygon={casePayload?.spill_polygon}
              sarBounds={sarBounds}
              sarImageUrl={`/api/cases/${selectedCaseId}/sar/image`}
              selectedVesselId={selected?.vessel_id ?? null}
              onVesselSelect={(id) => {
                const v = result?.vessels.find((v) => v.vessel_id === id);
                if (v) setSelected(v);
              }}
              layers={activeLayers}
              aisTracks={casePayload?.ais_tracks ?? null}
            />
          </div>
          
          <Timeline 
            result={result}
            currentTime={currentTime}
            onTimeChange={setCurrentTime}
          />
          
          <div className="meta-grid" style={{ marginTop: "14px" }}>
            <div>
              <span>Detector score</span>
              <strong>{result ? result.detector.score.toFixed(3) : "--"}</strong>
            </div>
            <div>
              <span>Heatmap peak</span>
              <strong>{heatmapSummary}</strong>
            </div>
          </div>
        </div>
      </section>

      <section className="panel right">
        <h2>Ranked Investigative Leads</h2>
        <div className="candidate-list">
          {(result?.vessels ?? []).map((vessel) => (
            <button
              key={vessel.vessel_id}
              className={selected?.vessel_id === vessel.vessel_id ? "candidate active" : "candidate"}
              onClick={() => setSelected(vessel)}
            >
              <span>{vessel.name}</span>
              <strong>{vessel.lead_score.toFixed(1)}</strong>
            </button>
          ))}
        </div>
        {selected ? (
          <EvidenceCard vessel={selected} />
        ) : (
          <div className="evidence">
            <p>Run the analysis to see candidate evidence.</p>
          </div>
        )}
      </section>
    </main>
  );
}
