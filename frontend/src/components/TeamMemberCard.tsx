// components/TeamMemberCard.tsx
"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, FileText, CheckCircle2, AlertCircle } from "lucide-react";
import { TeamMember } from "@/types/team";

interface TeamMemberCardProps {
  member: TeamMember;
}

export function TeamMemberCard({ member }: TeamMemberCardProps) {
  const [showEvidence, setShowEvidence] = useState(false);
  const fitPercentage = Math.round(member.project_fit * 100);

  return (
    <div className="flex flex-col justify-between rounded-lg border border-gray-200 bg-white p-5 shadow-xs hover:border-gray-300 transition-colors">
      <div>
        {/* Top header */}
        <div className="flex items-start justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-semibold text-gray-900">{member.name}</h3>
              <span className="rounded-sm bg-gray-100 px-2 py-0.5 text-[11px] font-medium text-gray-800 border border-gray-200">
                {member.assigned_role}
              </span>
            </div>
            <p className="text-[11px] text-gray-500 mt-0.5">Current Role: {member.role}</p>
          </div>

          <div className="text-right">
            <span className="inline-flex items-center rounded-sm bg-gray-50 px-2 py-0.5 text-[11px] font-semibold text-gray-700 border border-gray-200">
              {fitPercentage}% Match
            </span>
          </div>
        </div>

        {/* Why Selected / Staffing Rationale */}
        <div className="mt-3.5 rounded-md bg-gray-50 p-3 text-xs text-gray-700 border border-gray-200/80 leading-relaxed">
          <span className="text-[11px] font-semibold text-gray-900 block mb-1">
            Placement Rationale
          </span>
          <p>{member.why_selected}</p>
        </div>

        {/* Competencies */}
        <div className="mt-3">
          <span className="text-[11px] font-medium text-gray-500 block mb-1.5">
            Verified Competencies
          </span>
          <div className="flex flex-wrap gap-1">
            {member.skills.map((skill, idx) => (
              <span
                key={idx}
                className="rounded-sm bg-white px-2 py-0.5 text-[11px] text-gray-700 border border-gray-200"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>

        {/* Strengths & Gaps */}
        <div className="mt-3 grid grid-cols-1 gap-2 text-[11px] border-t border-gray-100 pt-2.5">
          {member.strengths && member.strengths.length > 0 && (
            <div className="text-gray-600">
              <span className="font-medium text-gray-900 block mb-0.5">Key Strengths:</span>
              <ul className="list-disc list-inside space-y-0.5 pl-0.5">
                {member.strengths.slice(0, 2).map((st, i) => (
                  <li key={i} className="truncate">{st}</li>
                ))}
              </ul>
            </div>
          )}

          {member.gaps && member.gaps.length > 0 && (
            <div className="text-gray-500">
              <span className="font-medium text-gray-700 block mb-0.5">Identified Gaps:</span>
              <ul className="list-disc list-inside space-y-0.5 pl-0.5">
                {member.gaps.slice(0, 2).map((gp, i) => (
                  <li key={i} className="truncate">{gp}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Expandable Document Excerpts (RAG Evidence) */}
      <div className="mt-4 border-t border-gray-100 pt-3">
        <button
          type="button"
          onClick={() => setShowEvidence(!showEvidence)}
          className="flex w-full items-center justify-between text-xs font-medium text-gray-600 hover:text-gray-900 py-0.5"
        >
          <span className="flex items-center gap-1.5">
            <FileText className="h-3.5 w-3.5 text-gray-400" />
            <span>{showEvidence ? "Hide Document Excerpts" : "View Document Excerpts"}</span>
          </span>
          {showEvidence ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
        </button>

        {showEvidence && (
          <div className="mt-2.5 rounded-md border border-gray-200 bg-gray-50/70 p-3 text-xs space-y-2">
            <div className="text-[11px] font-medium text-gray-700 border-b border-gray-200 pb-1 flex justify-between">
              <span>Indexed Resume & Project References</span>
              <span className="text-gray-400 font-mono">pgvector</span>
            </div>
            {member.evidence && member.evidence.length > 0 ? (
              member.evidence.map((snippet, idx) => (
                <div key={idx} className="rounded bg-white p-2.5 border border-gray-200 text-gray-700 shadow-2xs">
                  <p className="text-[11px] leading-relaxed text-gray-600 italic">"{snippet}"</p>
                  <span className="mt-1 block text-[10px] text-gray-400 font-mono">
                    Ref: Section Excerpt #{idx + 1}
                  </span>
                </div>
              ))
            ) : (
              <p className="text-xs text-gray-400 italic">No direct excerpts recorded.</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
