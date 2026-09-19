// app/employees/[id]/page.tsx
"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, Briefcase, Calendar, Mail, FileText } from "lucide-react";
import { Employee } from "@/types/employee";
import { employeeService } from "@/services/employeeService";

export default function EmployeeDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const employeeId = parseInt(resolvedParams.id, 10);

  const [employee, setEmployee] = useState<Employee | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"overview" | "resume">("overview");

  useEffect(() => {
    async function load() {
      try {
        const data = await employeeService.getById(employeeId);
        setEmployee(data);
      } catch (err) {
        console.error("Failed to load candidate details:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [employeeId]);

  if (loading) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-16 text-center text-xs text-gray-400">
        Loading candidate dossier...
      </div>
    );
  }

  if (!employee) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-16 text-center">
        <p className="text-sm font-semibold text-gray-800">Candidate Not Found</p>
        <Link href="/employees" className="mt-2 inline-block text-xs text-gray-600 hover:underline">
          ← Return to Roster
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-4 pt-8 sm:px-6 lg:px-8 space-y-6">
      <div>
        <Link
          href="/employees"
          className="inline-flex items-center gap-1.5 text-xs font-medium text-gray-500 hover:text-gray-900 transition-colors"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          <span>Return to Engineering Roster</span>
        </Link>
      </div>

      {/* Dossier Card */}
      <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-xs">
        {/* Profile Header */}
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 border-b border-gray-100 pb-5">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-md bg-gray-900 text-white font-semibold text-base">
              {employee.name.charAt(0)}
            </div>
            <div>
              <h1 className="text-lg font-bold text-gray-900">{employee.name}</h1>
              <p className="text-xs text-gray-600 font-medium">{employee.role}</p>
              <div className="mt-1 flex flex-wrap items-center gap-3 text-xs text-gray-500">
                <span className="flex items-center gap-1">
                  <Briefcase className="h-3.5 w-3.5 text-gray-400" />
                  {employee.department || "Engineering"}
                </span>
                <span>•</span>
                <span className="flex items-center gap-1">
                  <Calendar className="h-3.5 w-3.5 text-gray-400" />
                  {employee.years_experience} years
                </span>
                {employee.email && (
                  <>
                    <span>•</span>
                    <span className="flex items-center gap-1">
                      <Mail className="h-3.5 w-3.5 text-gray-400" />
                      {employee.email}
                    </span>
                  </>
                )}
              </div>
            </div>
          </div>

          <div>
            <span className="rounded bg-gray-100 px-2.5 py-1 text-xs font-medium text-gray-700 border border-gray-200">
              ID #{employee.id}
            </span>
          </div>
        </div>

        {/* Tab switcher */}
        <div className="mt-4 flex border-b border-gray-200 text-xs font-medium">
          <button
            onClick={() => setActiveTab("overview")}
            className={`pb-2.5 px-3 border-b-2 transition-colors ${
              activeTab === "overview"
                ? "border-gray-900 text-gray-900 font-semibold"
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
          >
            Profile & Project Track Record
          </button>
          <button
            onClick={() => setActiveTab("resume")}
            className={`pb-2.5 px-3 border-b-2 transition-colors ${
              activeTab === "resume"
                ? "border-gray-900 text-gray-900 font-semibold"
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
          >
            Raw Resume Document
          </button>
        </div>

        {activeTab === "overview" && (
          <div className="mt-5 space-y-6">
            {/* Skills */}
            <div>
              <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-900 mb-2.5">
                Technical Competencies
              </h3>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                {employee.skills?.map((skill, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between rounded border border-gray-200 bg-gray-50/50 px-3 py-2 text-xs"
                  >
                    <span className="font-medium text-gray-900">{skill.name}</span>
                    <span className="text-[11px] text-gray-500 capitalize font-mono">
                      {skill.proficiency}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Past Projects */}
            <div>
              <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-900 mb-2.5">
                Documented Project Experience
              </h3>
              <div className="space-y-2.5">
                {employee.projects && employee.projects.length > 0 ? (
                  employee.projects.map((proj, idx) => (
                    <div
                      key={idx}
                      className="rounded border border-gray-200 bg-white p-3.5 text-xs shadow-2xs"
                    >
                      <div className="flex items-center justify-between">
                        <h4 className="font-semibold text-gray-900">{proj.name}</h4>
                        <span className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] text-gray-600 font-medium border border-gray-200">
                          {proj.domain || "General"}
                        </span>
                      </div>
                      <p className="mt-1.5 text-gray-600 leading-relaxed">{proj.description}</p>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-gray-400 italic">No project history recorded.</p>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === "resume" && (
          <div className="mt-5">
            <div className="rounded border border-gray-200 bg-gray-50 p-4">
              <div className="flex items-center justify-between mb-2.5 text-xs text-gray-500 border-b border-gray-200 pb-2">
                <span>Source: {employee.resume_filename || "Fictional Candidate Record"}</span>
                <span className="font-mono text-[11px]">Indexed Excerpt</span>
              </div>
              <pre className="whitespace-pre-wrap font-mono text-xs text-gray-800 leading-relaxed max-h-96 overflow-y-auto">
                {employee.resume_text || "No raw resume text available."}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
