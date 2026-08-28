import type { Vessel } from "../types";

const WEIGHTS: Record<string, number> = {
  origin_region_overlap: 35,
  release_time_match: 20,
  drift_consistency: 25,
  trajectory_heading: 10,
  ais_data_quality: 10,
};

function label(key: string) {
  return key.replace(/_/g, " ").replace(/\b\w/g, (character) => character.toUpperCase());
}

export function EvidenceCard({ vessel }: { vessel: Vessel }) {
  return (
    <article className="evidence">
      <header className="evidence-header">
        <div>
          <p className="kicker">Selected lead</p>
          <h3>{vessel.name}</h3>
          <p className="vessel-meta">MMSI {vessel.mmsi} · {vessel.vessel_type.replaceAll("_", " ")}</p>
        </div>
        <div className="score-block"><strong>{vessel.lead_score.toFixed(1)}</strong><span>/ 100</span></div>
      </header>

      <p className="distance-readout">Nearest reconstructed source distance <strong>{vessel.nearest_distance_km.toFixed(1)} km</strong></p>

      <section aria-labelledby="evidence-breakdown">
        <h4 id="evidence-breakdown">Evidence breakdown</h4>
        <div className="score-list">
          {Object.entries(vessel.components).map(([key, value]) => (
            <div className="score-row" key={key}>
              <div><span>{label(key)}</span><small>{WEIGHTS[key] ?? 0}% weight</small></div>
              <div className="score-track" aria-label={`${label(key)} ${Math.round(value * 100)} out of 100`}>
                <span style={{ width: `${Math.max(0, Math.min(1, value)) * 100}%` }} />
              </div>
              <strong>{Math.round(value * 100)}</strong>
            </div>
          ))}
        </div>
      </section>

      <section className="evidence-notes" aria-labelledby="evidence-reasons">
        <h4 id="evidence-reasons">Why this lead ranked here</h4>
        <ul>{vessel.reasons.map((reason) => <li key={reason}>{reason}</li>)}</ul>
      </section>

      {vessel.warnings.length > 0 && (
        <section className="warning-notes" aria-labelledby="evidence-warnings">
          <h4 id="evidence-warnings">Data cautions</h4>
          <ul>{vessel.warnings.map((warning) => <li key={warning}>{warning}</li>)}</ul>
        </section>
      )}
    </article>
  );
}
