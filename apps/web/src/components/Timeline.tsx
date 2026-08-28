import React from "react";
import type { AnalysisResult } from "../types";

function formatTime(iso: string) {
  return new Date(iso).toLocaleTimeString("en-IN", { timeStyle: "short", timeZone: "UTC" });
}

type TimelineProps = {
  result: AnalysisResult | null;
  currentTime: string | null;
  onTimeChange: (time: string) => void;
};

export function Timeline({ result, currentTime, onTimeChange }: TimelineProps) {
  if (!result) {
    return <div className="timeline">Run analysis to populate release-window playback.</div>;
  }

  const start = new Date(result.release_window.start).getTime();
  const end = new Date(result.release_window.end).getTime();
  const current = currentTime ? new Date(currentTime).getTime() : end;

  const progress = Math.max(0, Math.min(100, ((current - start) / (end - start)) * 100));

  return (
    <div className="timeline" style={{ display: "flex", flexDirection: "column", gap: "10px", marginTop: "10px", zIndex: 10, position: "relative" }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", background: "rgba(0,0,0,0.5)", padding: "4px", borderRadius: "4px" }}>
        <span>{formatTime(result.release_window.start)}</span>
        <span style={{ color: "#8dd8c3" }}>Release window ({result.release_window.confidence_band} confidence)</span>
        <span>{formatTime(result.release_window.end)}</span>
      </div>
      
      <div style={{ position: "relative", height: "4px", background: "rgba(255,255,255,0.2)", borderRadius: "2px" }}>
        <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: `${progress}%`, background: "#8dd8c3", borderRadius: "2px" }}></div>
        <input 
          type="range" 
          min={start} 
          max={end} 
          value={current}
          onChange={(e) => onTimeChange(new Date(Number(e.target.value)).toISOString())}
          style={{ position: "absolute", width: "100%", top: "-8px", margin: 0, opacity: 0, cursor: "pointer" }}
        />
        <div style={{ 
          position: "absolute", 
          left: `calc(${progress}% - 6px)`, 
          top: "-4px", 
          width: "12px", 
          height: "12px", 
          background: "#fff", 
          borderRadius: "50%",
          pointerEvents: "none"
        }}></div>
      </div>
    </div>
  );
}
