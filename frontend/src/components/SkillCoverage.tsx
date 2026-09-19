// components/SkillCoverage.tsx
import { Check, X } from "lucide-react";

interface SkillCoverageProps {
  skillCoverage: Record<string, boolean>;
}

export function SkillCoverage({ skillCoverage }: SkillCoverageProps) {
  const entries = Object.entries(skillCoverage || {});

  if (entries.length === 0) {
    return null;
  }

  const coveredCount = entries.filter(([_, covered]) => covered).length;
  const allCovered = coveredCount === entries.length;

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-xs">
      <div className="flex items-center justify-between mb-3 border-b border-gray-100 pb-3">
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-gray-900">
            Competency Matrix Verification
          </h4>
          <p className="text-[11px] text-gray-500 mt-0.5">
            Cross-referenced against verified profiles in composed team
          </p>
        </div>
        <span
          className={`rounded px-2 py-0.5 text-xs font-medium border ${
            allCovered
              ? "bg-emerald-50 text-emerald-800 border-emerald-200"
              : "bg-amber-50 text-amber-800 border-amber-200"
          }`}
        >
          {coveredCount}/{entries.length} Satisfied
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
        {entries.map(([skill, isCovered]) => (
          <div
            key={skill}
            className={`flex items-center justify-between rounded border px-3 py-2 text-xs ${
              isCovered
                ? "border-gray-200 bg-gray-50/60 text-gray-800"
                : "border-rose-200 bg-rose-50 text-rose-800"
            }`}
          >
            <span className="font-medium text-gray-900">{skill}</span>
            {isCovered ? (
              <span className="flex h-4 w-4 items-center justify-center text-emerald-600">
                <Check className="h-3.5 w-3.5 stroke-[2.5]" />
              </span>
            ) : (
              <span className="flex h-4 w-4 items-center justify-center text-rose-600">
                <X className="h-3.5 w-3.5 stroke-[2.5]" />
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
