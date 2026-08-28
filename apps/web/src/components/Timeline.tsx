import type { AnalysisResult } from "../types";

function formatTime(iso: string) {
  return new Date(iso).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", timeZone: "UTC" });
}

type TimelineProps = {
  result: AnalysisResult | null;
  currentTime: string | null;
  onTimeChange: (time: string) => void;
};

export function Timeline({ result, currentTime, onTimeChange }: TimelineProps) {
  const window = result?.release_window;
  if (!window) {
    return (
      <div className="timeline empty">
        {result?.analysis_mode === "detection_only"
          ? "Release reconstruction is intentionally disabled for this validation case."
          : "Run the case to reconstruct the likely release window."}
      </div>
    );
  }

  const start = new Date(window.start).getTime();
  const end = new Date(window.end).getTime();
  const current = currentTime ? new Date(currentTime).getTime() : end;

  return (
    <div className="timeline">
      <div className="timeline-labels">
        <span>{formatTime(window.start)} UTC</span>
        <strong>Likely release · {window.confidence_band} confidence</strong>
        <span>{formatTime(window.end)} UTC</span>
      </div>
      <input
        aria-label="Release-window time"
        type="range"
        min={start}
        max={end}
        step={15 * 60 * 1000}
        value={Math.max(start, Math.min(end, current))}
        onChange={(event) => onTimeChange(new Date(Number(event.target.value)).toISOString())}
      />
    </div>
  );
}
