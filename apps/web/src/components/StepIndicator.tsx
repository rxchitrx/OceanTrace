type StepIndicatorProps = {
  currentStep: number;
  detectionOnly: boolean;
};

export function StepIndicator({ currentStep, detectionOnly }: StepIndicatorProps) {
  const steps = detectionOnly
    ? ["Case loaded", "Detect slick", "Validate label"]
    : ["Case loaded", "Detect slick", "Reconstruct source", "Rank leads"];

  return (
    <ol className="step-list" aria-label="Analysis progress">
      {steps.map((step, index) => {
        const number = index + 1;
        const state = currentStep > number ? "complete" : currentStep === number ? "active" : "pending";
        return (
          <li className={`step ${state}`} key={step}>
            <span className="step-number" aria-hidden="true">{state === "complete" ? "✓" : number}</span>
            <span>{step}</span>
          </li>
        );
      })}
    </ol>
  );
}
