import React from "react";
import type { Vessel } from "../types";

export function EvidenceCard({ vessel }: { vessel: Vessel }) {
  const getScoreColor = (score: number) => {
    if (score >= 0.7) return "#8dd8c3";
    if (score >= 0.4) return "#ffdb71";
    return "#ff8e78";
  };

  const getWeight = (key: string) => {
    const weights: Record<string, number> = {
      origin_region_overlap: 35,
      release_time_match: 20,
      drift_consistency: 25,
      trajectory_heading: 10,
      ais_data_quality: 10,
    };
    return weights[key] || 0;
  };

  const formatKey = (key: string) => {
    return key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
  };

  return (
    <div className="evidence">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "12px" }}>
        <div>
          <h3 style={{ margin: "0 0 4px 0", color: "#8dd8c3" }}>{vessel.name}</h3>
          <div style={{ fontSize: "0.85rem", opacity: 0.8 }}>
            MMSI: {vessel.mmsi || "Unknown"} • {vessel.vessel_type?.toUpperCase() || "VESSEL"}
          </div>
        </div>
        <div style={{ textAlign: "right" }}>
          <div style={{ fontSize: "1.5rem", fontWeight: "bold" }}>{vessel.lead_score.toFixed(1)}</div>
          <div style={{ fontSize: "0.75rem", opacity: 0.7 }}>Lead Score</div>
        </div>
      </div>

      <div style={{ marginBottom: "16px", fontSize: "0.9rem" }}>
        <strong>Nearest Distance:</strong> {vessel.nearest_distance_km} km
      </div>

      <div style={{ marginBottom: "20px" }}>
        <strong style={{ display: "block", marginBottom: "8px" }}>Evidence Breakdown</strong>
        <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
          {Object.entries(vessel.components).map(([key, value]) => (
            <div key={key}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", marginBottom: "4px" }}>
                <span>{formatKey(key)} <span style={{ opacity: 0.5 }}>({getWeight(key)}%)</span></span>
                <strong>{(value * 100).toFixed(0)}/100</strong>
              </div>
              <div style={{ height: "6px", background: "rgba(255,255,255,0.1)", borderRadius: "3px", overflow: "hidden" }}>
                <div 
                  style={{ 
                    height: "100%", 
                    width: `${value * 100}%`, 
                    background: getScoreColor(value),
                    borderRadius: "3px" 
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      <div style={{ marginBottom: "16px" }}>
        <strong style={{ display: "block", marginBottom: "8px" }}>Reasons</strong>
        <ul style={{ margin: 0, paddingLeft: "20px", fontSize: "0.9rem", color: "#cae5dc" }}>
          {vessel.reasons.map((reason, idx) => (
            <li key={idx} style={{ marginBottom: "4px" }}>{reason}</li>
          ))}
        </ul>
      </div>

      {vessel.warnings && vessel.warnings.length > 0 && (
        <div>
          <strong style={{ display: "block", marginBottom: "8px", color: "#ffdb71" }}>Warnings</strong>
          <ul style={{ margin: 0, paddingLeft: "20px", fontSize: "0.9rem", color: "#ffdb71" }}>
            {vessel.warnings.map((warning, idx) => (
              <li key={idx} style={{ marginBottom: "4px" }}>{warning}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
