// components/AgentWorkflow.tsx
import { Check, Loader2, RefreshCw } from "lucide-react";
import { cn } from "@/lib/utils";

interface AgentStepConfig {
  id: string;
  name: string;
  description: string;
}

const AGENT_STEPS: AgentStepConfig[] = [
  {
    id: "project_analyzer",
    name: "Specification Analysis",
    description: "Extracts role headcounts, seniority levels, and technical competencies",
  },
  {
    id: "candidate_retriever",
    name: "Candidate Retrieval (Hybrid Search)",
    description: "Executes SQL relational filters and vector similarity search across resume chunks",
  },
  {
    id: "candidate_evaluator",
    name: "Profile Evaluation",
    description: "Scores candidate background against required criteria using verified evidence",
  },
  {
    id: "team_builder",
    name: "Team Composition & Optimization",
    description: "Solves slot allocation to maximize collective skill coverage and balance",
  },
  {
    id: "team_validator",
    name: "Constraint Validation",
    description: "Verifies headcount and mandatory skill fulfillment; triggers re-query if needed",
  },
  {
    id: "explanation",
    name: "Staffing Brief & Justifications",
    description: "Compiles documented justifications and executive team overview",
  },
];

interface AgentWorkflowProps {
  currentNode: string | null;
  completedNodes: Record<string, string>;
  isProcessing: boolean;
  retryCount?: number;
}

export function AgentWorkflow({
  currentNode,
  completedNodes,
  isProcessing,
  retryCount = 0,
}: AgentWorkflowProps) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-xs">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-100 pb-3 mb-4">
        <div>
          <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-900">
            Pipeline Execution
          </h3>
          <p className="text-[11px] text-gray-500 mt-0.5">
            6-stage qualification & team solver
          </p>
        </div>

        {isProcessing && (
          <div className="flex items-center gap-1.5 text-[11px] font-medium text-blue-700 bg-blue-50 border border-blue-100 rounded px-2 py-0.5">
            <Loader2 className="h-3 w-3 animate-spin" />
            <span>Processing</span>
          </div>
        )}

        {retryCount > 1 && !isProcessing && (
          <div className="text-[11px] font-medium text-amber-800 bg-amber-50 border border-amber-200 rounded px-2 py-0.5">
            Cycle {retryCount}
          </div>
        )}
      </div>

      {/* Stepper Timeline */}
      <div className="space-y-3">
        {AGENT_STEPS.map((step, idx) => {
          const isCompleted = Boolean(completedNodes[step.id]);
          const isActive = currentNode === step.id && isProcessing;
          const summary = completedNodes[step.id];

          return (
            <div
              key={step.id}
              className={cn(
                "relative flex items-start gap-3 rounded-md p-2.5 transition-colors text-xs",
                isActive && "bg-blue-50/50 border border-blue-100",
                isCompleted && "bg-gray-50/70 border border-transparent",
                !isActive && !isCompleted && "opacity-40"
              )}
            >
              {/* Step indicator dot */}
              <div className="mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center">
                {isCompleted ? (
                  <Check className="h-3.5 w-3.5 text-emerald-600 stroke-[2.5]" />
                ) : isActive ? (
                  <Loader2 className="h-3.5 w-3.5 text-blue-600 animate-spin" />
                ) : (
                  <span className="h-1.5 w-1.5 rounded-full bg-gray-300" />
                )}
              </div>

              {/* Text details */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <span
                    className={cn(
                      "font-medium",
                      isActive ? "text-blue-900 font-semibold" : "text-gray-900"
                    )}
                  >
                    {step.name}
                  </span>
                  <span className="text-[10px] text-gray-400 font-mono">0{idx + 1}</span>
                </div>

                {isCompleted && summary ? (
                  <p className="mt-1 text-[11px] text-gray-600 font-mono bg-white rounded px-2 py-1 border border-gray-200 truncate">
                    {summary}
                  </p>
                ) : (
                  <p className="text-[11px] text-gray-500 mt-0.5 leading-snug">
                    {step.description}
                  </p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
