// components/EmployeeCard.tsx
import Link from "next/link";
import { ChevronRight } from "lucide-react";
import { Employee } from "@/types/employee";

interface EmployeeCardProps {
  employee: Employee;
}

export function EmployeeCard({ employee }: EmployeeCardProps) {
  const displaySkills = employee.skills?.slice(0, 5) || [];
  const remainingCount = (employee.skills?.length || 0) - displaySkills.length;

  return (
    <div className="group flex flex-col justify-between rounded-lg border border-gray-200 bg-white p-4 shadow-xs hover:border-gray-300 transition-colors">
      <div>
        <div className="flex items-start justify-between gap-2">
          <div>
            <h3 className="text-sm font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
              {employee.name}
            </h3>
            <p className="text-xs text-gray-600 mt-0.5">{employee.role}</p>
          </div>
          <span className="inline-flex items-center rounded-sm bg-gray-100 px-1.5 py-0.5 text-[10px] font-medium text-gray-700">
            {employee.department || "Engineering"}
          </span>
        </div>

        <div className="mt-2.5 text-[11px] text-gray-500 font-medium">
          <span>{employee.years_experience} years experience</span>
          {employee.resume_filename && (
            <span className="text-gray-400"> • {employee.resume_filename}</span>
          )}
        </div>

        <div className="mt-3 flex flex-wrap gap-1">
          {displaySkills.map((s, idx) => (
            <span
              key={idx}
              className="rounded-sm bg-gray-50 px-1.5 py-0.5 text-[11px] font-medium text-gray-700 border border-gray-200"
            >
              {s.name}
            </span>
          ))}
          {remainingCount > 0 && (
            <span className="rounded-sm bg-gray-50 px-1.5 py-0.5 text-[10px] text-gray-400 border border-gray-100">
              +{remainingCount}
            </span>
          )}
        </div>
      </div>

      <div className="mt-4 border-t border-gray-100 pt-2.5">
        <Link
          href={`/employees/${employee.id}`}
          className="flex items-center justify-between text-xs font-medium text-gray-600 group-hover:text-gray-900 transition-colors"
        >
          <span>View profile & project history</span>
          <ChevronRight className="h-3.5 w-3.5 text-gray-400 group-hover:translate-x-0.5 transition-transform" />
        </Link>
      </div>
    </div>
  );
}
