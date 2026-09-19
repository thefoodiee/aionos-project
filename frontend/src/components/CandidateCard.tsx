// components/CandidateCard.tsx
import { Award, Briefcase, FileCheck } from "lucide-react";
import { CandidateItem } from "@/types/team";

interface CandidateCardProps {
  candidate: CandidateItem;
}

export function CandidateCard({ candidate }: CandidateCardProps) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 text-left shadow-xs">
      <div className="flex items-start justify-between">
        <div>
          <h4 className="font-medium text-slate-900">{candidate.name}</h4>
          <p className="text-xs text-slate-500">{candidate.role} • {candidate.years_experience} yrs</p>
        </div>
        {candidate.relevance_score && (
          <span className="rounded bg-emerald-50 px-2 py-0.5 text-xs font-semibold text-emerald-700">
            Score: {candidate.relevance_score}
          </span>
        )}
      </div>

      <div className="mt-2.5 flex flex-wrap gap-1">
        {candidate.skills.slice(0, 4).map((s, idx) => (
          <span key={idx} className="rounded bg-slate-100 px-1.5 py-0.5 text-[11px] text-slate-600">
            {s}
          </span>
        ))}
      </div>

      {candidate.evidence && candidate.evidence.length > 0 && (
        <div className="mt-3 rounded bg-slate-50 p-2 text-[11px] text-slate-600 border border-slate-100">
          <span className="font-medium text-slate-700 block mb-0.5">Top Evidence Snippet:</span>
          <p className="line-clamp-2 italic">"{candidate.evidence[0]}"</p>
        </div>
      )}
    </div>
  );
}
