import React from "react";

type StepIndicatorProps = {
  currentStep: number;
};

export function StepIndicator({ currentStep }: StepIndicatorProps) {
  const steps = [
    "Load Case",
    "Run Detection",
    "Run Source Reconstruction",
    "Show Vessel Correlation"
  ];

  return (
    <div className="step-list" style={{ display: "flex", flexDirection: "column", gap: "10px", margin: "24px 0" }}>
      {steps.map((step, index) => {
        const stepNum = index + 1;
        const isActive = currentStep === stepNum;
        const isCompleted = currentStep > stepNum;
        
        return (
          <div 
            key={index} 
            style={{ 
              display: "flex", 
              alignItems: "center", 
              gap: "12px",
              opacity: isActive || isCompleted ? 1 : 0.4,
              transition: "opacity 0.3s"
            }}
          >
            <div 
              style={{ 
                width: "24px", 
                height: "24px", 
                borderRadius: "50%", 
                display: "flex", 
                alignItems: "center", 
                justifyContent: "center",
                fontSize: "0.8rem",
                background: isActive ? "#8dd8c3" : isCompleted ? "rgba(255,255,255,0.1)" : "transparent",
                border: isActive ? "none" : isCompleted ? "1px solid rgba(255,255,255,0.3)" : "1px solid rgba(255,255,255,0.1)",
                color: isActive ? "#000" : "#fff"
              }}
            >
              {isCompleted ? "✓" : stepNum}
            </div>
            <div style={{ color: isActive ? "#8dd8c3" : "inherit", fontWeight: isActive ? "bold" : "normal" }}>
              {step}
            </div>
          </div>
        );
      })}
    </div>
  );
}
