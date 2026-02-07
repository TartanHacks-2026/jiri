import { CheckCircle2, Circle, CircleDot, CircleX } from "lucide-react";

import type { PlanStep } from "@/lib/event-contract";

interface PlanCardProps {
  goal: string;
  steps: PlanStep[];
}

function StepStatusIcon({ status }: { status: PlanStep["status"] }) {
  if (status === "done") {
    return <CheckCircle2 className="h-4 w-4 text-success" />;
  }
  if (status === "active") {
    return <CircleDot className="h-4 w-4 text-accent" />;
  }
  if (status === "error") {
    return <CircleX className="h-4 w-4 text-danger" />;
  }

  return <Circle className="h-4 w-4 text-muted-foreground" />;
}

export function PlanCard({ goal, steps }: PlanCardProps) {
  return (
    <div className="space-y-3">
      <h3 className="text-sm uppercase tracking-[0.16em] text-muted-foreground">
        Agent Plan
      </h3>
      <div className="space-y-3">
        <p className="text-sm text-foreground">{goal}</p>

        {steps.length === 0 ? (
          <div className="rounded-lg border border-dashed border-border/70 p-3 text-sm text-muted-foreground">
            Planner is warming up.
          </div>
        ) : (
          <div className="space-y-2">
            {steps.map((step) => (
              <div
                key={step.id}
                className="flex items-start gap-2 rounded-lg border border-border/65 bg-background/40 px-3 py-2"
              >
                <StepStatusIcon status={step.status} />
                <p className="text-sm text-foreground">{step.label}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
