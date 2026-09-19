// app/page.tsx
"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Users,
  Briefcase,
  ArrowRight,
  Database,
  CheckCircle2,
  FileText,
  SlidersHorizontal,
  FolderGit2,
  Cpu,
  ChevronRight,
  Loader2,
} from "lucide-react";
import { employeeService } from "@/services/employeeService";
import { Employee } from "@/types/employee";

export default function DashboardPage() {
  const router = useRouter();
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [isSeeding, setIsSeeding] = useState(false);

  useEffect(() => {
    async function loadStats() {
      try {
        const data = await employeeService.getAll();
        setEmployees(data || []);
      } catch (err) {
        setEmployees([]);
      } finally {
        setLoading(false);
      }
    }
    loadStats();
  }, []);

  const handleLoadTestData = async () => {
    try {
      setIsSeeding(true);
      await employeeService.seedTestData();
      router.push("/team-builder?demo=true");
    } catch (err) {
      console.error("Failed to seed data:", err);
      router.push("/team-builder?demo=true");
    } finally {
      setIsSeeding(false);
    }
  };

  return (
    <div className="mx-auto max-w-7xl px-4 pt-8 sm:px-6 lg:px-8 space-y-8">
      {/* Top Banner / Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-gray-200 pb-5">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-gray-900">
            Engineering Resource & Team Composition
          </h1>
          <p className="text-xs text-gray-500 mt-0.5">
            Automated project staffing and candidate qualification engine based on verified profiles and project histories.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          <button
            type="button"
            onClick={handleLoadTestData}
            disabled={isSeeding}
            className="inline-flex items-center gap-1.5 rounded-md border border-gray-300 bg-white px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50 hover:text-gray-900 transition-colors shadow-2xs disabled:opacity-60 disabled:cursor-not-allowed"
            title="Upload seed data and navigate to prefilled project description"
          >
            {isSeeding ? (
              <>
                <Loader2 className="h-3.5 w-3.5 animate-spin text-gray-600" />
                <span>Loading Test Data...</span>
              </>
            ) : (
              <>
                <Database className="h-3.5 w-3.5 text-gray-500" />
                <span>Load Test Data</span>
              </>
            )}
          </button>
          <Link
            href="/employees"
            className="inline-flex items-center gap-1.5 rounded-md border border-gray-300 bg-white px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50 transition-colors shadow-2xs"
          >
            <Users className="h-3.5 w-3.5 text-gray-500" />
            <span>View Roster</span>
          </Link>
          <Link
            href="/team-builder"
            className="inline-flex items-center gap-1.5 rounded-md bg-gray-900 px-3.5 py-1.5 text-xs font-medium text-white hover:bg-gray-800 transition-colors shadow-xs"
          >
            <SlidersHorizontal className="h-3.5 w-3.5" />
            <span>Launch Planner</span>
          </Link>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-xs">
          <div className="flex items-center justify-between text-gray-500 text-xs font-medium">
            <span>Engineering Roster</span>
            <Users className="h-4 w-4 text-gray-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-gray-900">
              {loading ? "..." : employees.length}
            </span>
            <span className="text-[11px] text-gray-500">verified candidates</span>
          </div>
          <p className="mt-1 text-[11px] text-gray-400">
            Across Lead, Backend, Frontend, ML & QA
          </p>
        </div>

        <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-xs">
          <div className="flex items-center justify-between text-gray-500 text-xs font-medium">
            <span>Key Disciplines</span>
            <Briefcase className="h-4 w-4 text-gray-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-gray-900">6</span>
            <span className="text-[11px] text-gray-500">functional areas</span>
          </div>
          <p className="mt-1 text-[11px] text-gray-400">
            Lead, Backend, Frontend, ML, QA, DevOps
          </p>
        </div>

        <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-xs">
          <div className="flex items-center justify-between text-gray-500 text-xs font-medium">
            <span>Knowledge Base Chunks</span>
            <Database className="h-4 w-4 text-gray-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-gray-900">100+</span>
            <span className="text-[11px] text-gray-500">indexed excerpts</span>
          </div>
          <p className="mt-1 text-[11px] text-gray-400">
            Vector embeddings for semantic qualification
          </p>
        </div>

        <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-xs">
          <div className="flex items-center justify-between text-gray-500 text-xs font-medium">
            <span>Engine Status</span>
            <Cpu className="h-4 w-4 text-gray-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-sm font-semibold text-emerald-700 flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-emerald-500" /> Operational
            </span>
          </div>
          <p className="mt-1 text-[11px] text-gray-400">
            Hybrid search & constraint solver ready
          </p>
        </div>
      </div>

      {/* Quick Launch Staffing Planner Panel */}
      <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-gray-100 pb-4">
          <div>
            <h2 className="text-sm font-semibold text-gray-900">
              Staffing Planner Workbench
            </h2>
            <p className="text-xs text-gray-500 mt-0.5">
              Input natural language requirements or select a standard project template to run the team formation workflow.
            </p>
          </div>

          <Link
            href="/team-builder"
            className="inline-flex items-center gap-1 text-xs font-medium text-blue-600 hover:text-blue-700"
          >
            <span>Open full planner</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>

        {/* Project Spec Templates */}
        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3">
          <div
            onClick={handleLoadTestData}
            className="group cursor-pointer rounded-md border border-gray-200 bg-gray-50/50 p-4 hover:border-gray-300 hover:bg-gray-50 transition-all relative"
          >
            <div className="flex items-start justify-between">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                    Customer Support Platform Team (6 Members)
                  </span>
                  <span className="rounded bg-blue-50 px-1.5 py-0.5 text-[9px] font-semibold text-blue-700 border border-blue-200">
                    One-Click Seed & Fill
                  </span>
                </div>
                <p className="text-xs text-gray-500 leading-relaxed">
                  Tech Lead, 2 Backend Developers, 1 Frontend, 1 ML Engineer, 1 QA. Stack: React, FastAPI, PostgreSQL, AWS, LLM.
                </p>
              </div>
              <ChevronRight className="h-4 w-4 text-gray-400 group-hover:translate-x-0.5 transition-transform shrink-0 mt-0.5" />
            </div>
            <div className="mt-3 flex flex-wrap gap-1">
              <span className="rounded bg-white px-1.5 py-0.5 text-[10px] font-medium text-gray-600 border border-gray-200">
                React
              </span>
              <span className="rounded bg-white px-1.5 py-0.5 text-[10px] font-medium text-gray-600 border border-gray-200">
                FastAPI
              </span>
              <span className="rounded bg-white px-1.5 py-0.5 text-[10px] font-medium text-gray-600 border border-gray-200">
                PostgreSQL
              </span>
              <span className="rounded bg-white px-1.5 py-0.5 text-[10px] font-medium text-gray-600 border border-gray-200">
                AWS
              </span>
              <span className="rounded bg-white px-1.5 py-0.5 text-[10px] font-medium text-gray-600 border border-gray-200">
                LLM / RAG
              </span>
            </div>
          </div>

          <div
            onClick={() => router.push("/team-builder")}
            className="group cursor-pointer rounded-md border border-dashed border-gray-300 bg-white p-4 hover:border-gray-400 transition-all flex flex-col justify-center items-center text-center"
          >
            <SlidersHorizontal className="h-5 w-5 text-gray-400 mb-1" />
            <span className="text-xs font-semibold text-gray-900">
              Custom Project Specification
            </span>
            <p className="text-xs text-gray-500 mt-0.5">
              Enter specific headcount, disciplines, and required technical proficiencies.
            </p>
          </div>
        </div>
      </div>

      {/* Roster Overview Table */}
      <div className="rounded-lg border border-gray-200 bg-white shadow-xs overflow-hidden">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <div>
            <h2 className="text-sm font-semibold text-gray-900">Verified Engineering Roster</h2>
            <p className="text-xs text-gray-500 mt-0.5">Recent candidate additions and competency profiles</p>
          </div>
          <Link
            href="/employees"
            className="text-xs font-medium text-blue-600 hover:text-blue-700"
          >
            View all ({employees.length})
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-gray-50 text-gray-600 font-medium border-b border-gray-200">
              <tr>
                <th className="px-6 py-3">Candidate</th>
                <th className="px-6 py-3">Primary Role</th>
                <th className="px-6 py-3">Experience</th>
                <th className="px-6 py-3">Core Competencies</th>
                <th className="px-6 py-3 text-right">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 text-gray-700">
              {employees.slice(0, 6).map((emp) => (
                <tr key={emp.id} className="hover:bg-gray-50/70 transition-colors">
                  <td className="px-6 py-3.5 font-medium text-gray-900">
                    {emp.name}
                  </td>
                  <td className="px-6 py-3.5">
                    <span className="inline-flex items-center rounded-sm bg-gray-100 px-2 py-0.5 text-[11px] font-medium text-gray-700">
                      {emp.role}
                    </span>
                  </td>
                  <td className="px-6 py-3.5 text-gray-500">
                    {emp.years_experience} yrs
                  </td>
                  <td className="px-6 py-3.5">
                    <div className="flex flex-wrap gap-1">
                      {emp.skills?.slice(0, 4).map((s, idx) => (
                        <span
                          key={idx}
                          className="rounded bg-gray-50 px-1.5 py-0.5 text-[10px] text-gray-600 border border-gray-200"
                        >
                          {s.name}
                        </span>
                      ))}
                      {(emp.skills?.length || 0) > 4 && (
                        <span className="text-[10px] text-gray-400 self-center">
                          +{emp.skills.length - 4}
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-3.5 text-right">
                    <Link
                      href={`/employees/${emp.id}`}
                      className="text-xs font-medium text-gray-500 hover:text-gray-900"
                    >
                      Profile →
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
