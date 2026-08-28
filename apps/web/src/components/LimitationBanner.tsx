import React from "react";

export function LimitationBanner() {
  return (
    <div className="banner" style={{ fontSize: "0.85rem", lineHeight: "1.4" }}>
      <p style={{ margin: "0 0 6px 0", fontWeight: "bold", color: "#8dd8c3" }}>
        OCEANTRACE Investigation Tool
      </p>
      <p style={{ margin: "0 0 8px 0" }}>
        Ranks vessels as investigative leads using uncertainty-aware, explainable evidence fusion. Output is an investigative lead, not legal attribution.
      </p>
      <div style={{ fontSize: "0.75rem", opacity: 0.8, borderTop: "1px solid rgba(255,255,255,0.1)", paddingTop: "6px", display: "flex", justifyContent: "space-between" }}>
        <span>AIS: simulated</span>
        <span>Forcing: archived snapshot</span>
        <span>Detection: baseline threshold</span>
      </div>
    </div>
  );
}
