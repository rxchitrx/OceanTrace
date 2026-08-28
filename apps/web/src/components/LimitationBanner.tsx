import type { CasePayload } from "../types";

export function LimitationBanner({ casePayload }: { casePayload: CasePayload }) {
  const detectionOnly = casePayload.manifest.scenario_type === "detection_validation";
  return (
    <aside className="notice" aria-label="Use limitation">
      <strong>{detectionOnly ? "Validation case" : "Investigative support only"}</strong>
      <p>
        {detectionOnly
          ? "This real labelled SAR patch evaluates slick detection only. It does not identify a vessel."
          : "Scores prioritize leads for review. They are not proof of discharge or legal attribution."}
      </p>
      <div className="provenance-row">
        <span>AIS: {casePayload.manifest.ais_type.replaceAll("_", " ")}</span>
        <span>Forcing: {casePayload.manifest.forcing_type.replaceAll("_", " ")}</span>
      </div>
    </aside>
  );
}
