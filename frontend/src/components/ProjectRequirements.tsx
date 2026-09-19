// components/ProjectRequirements.tsx
import { Check, Users } from "lucide-react";
import { ProjectRoleRequirement, TeamMember } from "@/types/team";
import { formatRoleName } from "@/lib/utils";

interface ProjectRequirementsProps {
  roles: ProjectRoleRequirement[];
  team: TeamMember[];
}

export function ProjectRequirements({ roles, team }: ProjectRequirementsProps) {
  if (!roles || roles.length === 0) return null;

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-xs">
      <div className="flex items-center justify-between mb-3 border-b border-gray-100 pb-3">
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-gray-900">
            Headcount & Role Allocation
          </h4>
          <p className="text-[11px] text-gray-500 mt-0.5">Discipline targets vs assigned roster</p>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-gray-600 font-medium">
          <Users className="h-3.5 w-3.5 text-gray-500" />
          <span>{team.length} Placed</span>
        </div>
      </div>

      <div className="space-y-2">
        {roles.map((r, idx) => {
          const roleLabel = formatRoleName(r.role);
          const matchedCount = team.filter((m) =>
            m.assigned_role.toLowerCase().includes(r.role.toLowerCase().replace("_", " ")) ||
            r.role.toLowerCase().replace("_", " ").includes(m.assigned_role.toLowerCase())
          ).length;
          const satisfied = matchedCount >= r.count;

          return (
            <div
              key={idx}
              className="flex items-center justify-between rounded border border-gray-200/80 bg-gray-50 px-3 py-2 text-xs"
            >
              <div className="flex items-center gap-2">
                <span className="font-medium text-gray-900">{roleLabel}</span>
                <span className="text-gray-400 font-mono">target: {r.count}</span>
              </div>

              <div className="flex items-center gap-2">
                <span className="text-gray-600 font-medium">
                  {matchedCount}/{r.count} Allocated
                </span>
                {satisfied ? (
                  <span className="flex h-4 w-4 items-center justify-center text-emerald-600">
                    <Check className="h-3.5 w-3.5 stroke-[2.5]" />
                  </span>
                ) : (
                  <span className="rounded bg-amber-100 px-1.5 py-0.5 text-[10px] font-medium text-amber-800">
                    Partial
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
