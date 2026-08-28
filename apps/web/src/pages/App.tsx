import { useEffect, useMemo, useState } from "react";
import { fetchCase, fetchCases, fetchSarBounds, runCase, sarImageUrl } from "../api/client";
import { EvidenceCard } from "../components/EvidenceCard";
import { LimitationBanner } from "../components/LimitationBanner";
import { MapView } from "../components/MapView";
import { StepIndicator } from "../components/StepIndicator";
import { Timeline } from "../components/Timeline";
import type { AnalysisResult, CasePayload, CaseSummary, SarBounds, Vessel } from "../types";

function formatIso(value: string) {
  return `${new Date(value).toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "UTC",
  })} UTC`;
}

function layerLabel(layer: string) {
  const labels: Record<string, string> = {
    sar_image: "SAR scene",
    spill_polygon: "Slick outline",
    source_heatmap: "Source probability",
    particle_paths: "Drift paths",
    ais_tracks: "AIS tracks",
  };
  return labels[layer] ?? layer.replaceAll("_", " ");
}

export function App() {
  const [cases, setCases] = useState<CaseSummary[]>([]);
  const [selectedCaseId, setSelectedCaseId] = useState("");
  const [casePayload, setCasePayload] = useState<CasePayload | null>(null);
  const [sarBounds, setSarBounds] = useState<SarBounds | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [selected, setSelected] = useState<Vessel | null>(null);
  const [activeLayers, setActiveLayers] = useState<string[]>([]);
  const [currentTime, setCurrentTime] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    fetchCases()
      .then((items) => {
        if (!active) return;
        setCases(items);
        const preferred = items.find((item) => item.id === "arabian_sea_demo") ?? items[0];
        if (preferred) setSelectedCaseId(preferred.id);
        else setError("No case folders were found by the API.");
      })
      .catch((reason: unknown) => {
        if (active) setError(reason instanceof Error ? reason.message : "Could not load cases.");
      })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (!selectedCaseId) return;
    let active = true;
    setLoading(true);
    setError(null);
    setCasePayload(null);
    setSarBounds(null);
    setResult(null);
    setSelected(null);
    setCurrentTime(null);
    setCurrentStep(0);

    Promise.all([fetchCase(selectedCaseId), fetchSarBounds(selectedCaseId)])
      .then(([payload, bounds]) => {
        if (!active) return;
        setCasePayload(payload);
        setSarBounds(bounds);
        setActiveLayers(payload.available_layers);
        setCurrentStep(1);
      })
      .catch((reason: unknown) => {
        if (active) setError(reason instanceof Error ? reason.message : "Could not load the selected case.");
      })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [selectedCaseId]);

  const detectionOnly = casePayload?.manifest.scenario_type === "detection_validation";

  async function handleRunAnalysis() {
    if (!selectedCaseId || !casePayload) return;
    setRunning(true);
    setError(null);
    setCurrentStep(2);
    try {
      const payload = await runCase(selectedCaseId);
      setResult(payload);
      setSelected(payload.vessels[0] ?? null);
      setCurrentTime(payload.release_window?.end ?? null);
      setCurrentStep(payload.analysis_mode === "detection_only" ? 4 : 5);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Analysis failed.");
      setCurrentStep(1);
    } finally {
      setRunning(false);
    }
  }

  const peak = useMemo(() => {
    const points = result?.source_region?.heatmap_points ?? [];
    if (points.length === 0) return null;
    return points.reduce((best, point) => point.weight > best.weight ? point : best);
  }, [result]);

  const toggleLayer = (layer: string) => {
    setActiveLayers((current) => current.includes(layer)
      ? current.filter((item) => item !== layer)
      : [...current, layer]);
  };

  return (
    <main className="app-frame">
      <header className="topbar">
        <div className="brand-mark" aria-hidden="true"><span>OT</span></div>
        <div className="brand-copy">
          <p>OceanTrace / investigation console</p>
          <span>Satellite slick detection · source reconstruction · AIS correlation</span>
        </div>
        <div className={`system-state ${error ? "fault" : ""}`}>
          <i aria-hidden="true" />{error ? "attention required" : running ? "analysis running" : loading ? "loading case" : "system ready"}
        </div>
      </header>

      <div className="workspace">
        <aside className="case-rail">
          <section>
            <p className="section-index">01 / CASE</p>
            <h1>Reconstruct the trail behind the slick.</h1>
            <p className="intro">A bounded, explainable prototype for screening maritime pollution evidence.</p>
          </section>

          <label className="case-picker">
            <span>Loaded case</span>
            <select
              value={selectedCaseId}
              onChange={(event) => setSelectedCaseId(event.target.value)}
              disabled={loading || running}
            >
              {cases.map((item) => <option key={item.id} value={item.id}>{item.region}</option>)}
            </select>
          </label>

          <StepIndicator currentStep={currentStep} detectionOnly={Boolean(detectionOnly)} />

          <section className="layer-panel" aria-labelledby="layers-heading">
            <h2 id="layers-heading">Map layers</h2>
            <div className="layer-list">
              {casePayload?.available_layers.map((layer) => (
                <label key={layer}>
                  <input type="checkbox" checked={activeLayers.includes(layer)} onChange={() => toggleLayer(layer)} />
                  <span aria-hidden="true" />{layerLabel(layer)}
                </label>
              ))}
            </div>
          </section>

          <button className="run-button" onClick={handleRunAnalysis} disabled={!casePayload || running || loading}>
            <span>{running ? "Processing evidence…" : detectionOnly ? "Run detector validation" : "Run full analysis"}</span>
            <b aria-hidden="true">→</b>
          </button>

          {casePayload && <LimitationBanner casePayload={casePayload} />}
          {error && <div className="error-card" role="alert"><strong>Could not continue</strong><span>{error}</span></div>}
        </aside>

        <section className="map-column" aria-label="Geospatial analysis">
          <div className="map-heading">
            <div>
              <p className="section-index">02 / GEOSPATIAL EVIDENCE</p>
              <h2>{casePayload?.manifest.region ?? "Waiting for case data"}</h2>
            </div>
            <div className="observation-time">
              <span>Observation</span>
              <strong>{casePayload ? formatIso(casePayload.manifest.observation_time) : "—"}</strong>
            </div>
          </div>

          <div className="map-stage">
            {casePayload && sarBounds ? (
              <MapView
                result={result}
                spillPolygon={casePayload.spill_polygon}
                sarBounds={sarBounds}
                sarImageUrl={sarImageUrl(selectedCaseId)}
                selectedVesselId={selected?.vessel_id ?? null}
                onVesselSelect={(id) => {
                  const vessel = result?.vessels.find((item) => item.vessel_id === id);
                  if (vessel) setSelected(vessel);
                }}
                layers={activeLayers}
                aisTracks={casePayload.ais_tracks}
                currentTime={currentTime}
              />
            ) : (
              <div className="map-loading"><span />{error ? "Map unavailable" : "Loading geospatial evidence"}</div>
            )}
            <div className="map-legend">
              <span><i className="legend-slick" />detected slick</span>
              {!detectionOnly && <><span><i className="legend-source" />source probability</span><span><i className="legend-ais" />AIS tracks</span></>}
            </div>
          </div>

          <Timeline result={result} currentTime={currentTime} onTimeChange={setCurrentTime} />

          <div className="metric-strip">
            <div><span>Detector confidence</span><strong>{result ? `${(result.detector.score * 100).toFixed(1)}%` : "—"}</strong></div>
            <div><span>{detectionOnly ? "Label overlap (IoU)" : "Ensemble hypotheses"}</span><strong>{detectionOnly ? (result?.detector_evaluation ? result.detector_evaluation.best_bbox_iou.toFixed(3) : "—") : (result?.source_region?.heatmap_points.length ?? "—")}</strong></div>
            <div><span>{detectionOnly ? "Reference objects" : "Peak source"}</span><strong>{detectionOnly ? (result?.detector_evaluation?.reference_object_count ?? "—") : (peak ? `${peak.latitude.toFixed(3)}, ${peak.longitude.toFixed(3)}` : "—")}</strong></div>
          </div>
        </section>

        <aside className="evidence-rail">
          <div className="evidence-title">
            <p className="section-index">03 / {detectionOnly ? "VALIDATION" : "LEADS"}</p>
            <h2>{detectionOnly ? "Detector evidence" : "Ranked investigative leads"}</h2>
          </div>

          {detectionOnly ? (
            <div className="validation-panel">
              <span className="validation-stamp">DARTIS / REAL SAR</span>
              <h3>{result ? "Detection evaluated" : "Ready for validation"}</h3>
              <p>{result ? "The pixel-derived candidate is compared with the original Pascal VOC annotation." : "Run the detector against a labelled Sentinel-1-derived oil/water patch."}</p>
              {result?.detector_evaluation && (
                <dl>
                  <div><dt>Best bbox IoU</dt><dd>{result.detector_evaluation.best_bbox_iou.toFixed(3)}</dd></div>
                  <div><dt>Labelled objects</dt><dd>{result.detector_evaluation.reference_object_count}</dd></div>
                  <div><dt>Method</dt><dd>{result.detector.method.replaceAll("_", " ")}</dd></div>
                </dl>
              )}
            </div>
          ) : (
            <>
              <div className="candidate-list">
                {(result?.vessels ?? []).map((vessel, index) => (
                  <button
                    key={vessel.vessel_id}
                    className={selected?.vessel_id === vessel.vessel_id ? "candidate active" : "candidate"}
                    onClick={() => setSelected(vessel)}
                  >
                    <span className="rank">{String(index + 1).padStart(2, "0")}</span>
                    <span><strong>{vessel.name}</strong><small>{vessel.vessel_type.replaceAll("_", " ")}</small></span>
                    <b>{vessel.lead_score.toFixed(1)}</b>
                  </button>
                ))}
              </div>
              {selected ? <EvidenceCard vessel={selected} /> : <div className="empty-evidence"><span>NO RANKING YET</span><p>Run the full analysis to compare candidate vessel tracks.</p></div>}
            </>
          )}

          {casePayload && (
            <details className="case-notes">
              <summary>Data notes & provenance</summary>
              <ul>{casePayload.manifest.notes.map((note) => <li key={note}>{note}</li>)}</ul>
              {casePayload.manifest.data_sources.map((source) => <p key={source.name}>{source.name} · {source.license}</p>)}
            </details>
          )}
        </aside>
      </div>
    </main>
  );
}
