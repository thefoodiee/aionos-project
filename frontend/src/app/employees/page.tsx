// app/employees/page.tsx
"use client";

import { useState, useEffect } from "react";
import {
  Users,
  Search,
  Filter,
  Plus,
  Upload,
  CheckCircle2,
  AlertCircle,
  X,
  Loader2,
} from "lucide-react";
import { Employee, ResumeExtraction } from "@/types/employee";
import { employeeService } from "@/services/employeeService";
import { EmployeeCard } from "@/components/EmployeeCard";

export default function EmployeesPage() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selectedRole, setSelectedRole] = useState("all");

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [extractedPreview, setExtractedPreview] = useState<ResumeExtraction | null>(null);

  useEffect(() => {
    loadEmployees();
  }, []);

  async function loadEmployees() {
    setLoading(true);
    try {
      const data = await employeeService.getAll();
      setEmployees(data || []);
    } catch (err) {
      console.error("Failed to load employees:", err);
    } finally {
      setLoading(false);
    }
  }

  const filteredEmployees = employees.filter((emp) => {
    const matchesSearch =
      search === "" ||
      emp.name.toLowerCase().includes(search.toLowerCase()) ||
      emp.role.toLowerCase().includes(search.toLowerCase()) ||
      emp.skills?.some((s) => s.name.toLowerCase().includes(search.toLowerCase()));

    const matchesRole =
      selectedRole === "all" ||
      emp.role.toLowerCase().includes(selectedRole.toLowerCase());

    return matchesSearch && matchesRole;
  });

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadError(null);
    setExtractedPreview(null);

    try {
      const result = await employeeService.uploadResume(file);
      setExtractedPreview(result);
    } catch (err: any) {
      setUploadError(err.response?.data?.detail || "Failed to parse candidate file");
    } finally {
      setUploading(false);
    }
  };

  const handleSaveEmployee = async () => {
    if (!extractedPreview) return;
    setSaving(true);
    try {
      await employeeService.createEmployee({
        name: extractedPreview.name,
        role: extractedPreview.role,
        department: extractedPreview.department || "Engineering",
        years_experience: extractedPreview.years_experience,
        skills: extractedPreview.skills,
        projects: extractedPreview.projects,
        resume_filename: extractedPreview.filename,
        resume_text: extractedPreview.raw_text,
      });
      setIsModalOpen(false);
      setExtractedPreview(null);
      await loadEmployees();
    } catch (err: any) {
      setUploadError(err.response?.data?.detail || "Failed to save candidate profile");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="mx-auto max-w-7xl px-4 pt-8 sm:px-6 lg:px-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-gray-200 pb-5">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-gray-900 flex items-center gap-2">
            <Users className="h-5 w-5 text-gray-800" />
            Engineering Roster
          </h1>
          <p className="text-xs text-gray-500 mt-0.5">
            Verified candidate records, skill proficiencies, and documented project histories.
          </p>
        </div>

        <button
          onClick={() => {
            setIsModalOpen(true);
            setExtractedPreview(null);
            setUploadError(null);
          }}
          className="inline-flex items-center gap-1.5 rounded-md bg-gray-900 px-3.5 py-1.5 text-xs font-medium text-white hover:bg-gray-800 transition-colors shadow-xs self-start sm:self-auto"
        >
          <Plus className="h-3.5 w-3.5" />
          <span>Import Resume</span>
        </button>
      </div>

      {/* Toolbar */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-gray-400" />
          <input
            type="text"
            placeholder="Search candidate name, role, or technical skill (e.g. FastAPI, React, AWS, PyTorch)..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-md border border-gray-200 bg-white py-1.5 pl-9 pr-3 text-xs text-gray-900 placeholder-gray-400 focus:border-gray-900 focus:outline-hidden focus:ring-1 focus:ring-gray-900"
          />
        </div>

        <div className="flex items-center gap-2">
          <Filter className="h-3.5 w-3.5 text-gray-400 shrink-0" />
          <select
            value={selectedRole}
            onChange={(e) => setSelectedRole(e.target.value)}
            className="rounded-md border border-gray-200 bg-white px-2.5 py-1.5 text-xs text-gray-700 focus:border-gray-900 focus:outline-hidden"
          >
            <option value="all">All Roles</option>
            <option value="lead">Technical Lead</option>
            <option value="backend">Backend Engineer</option>
            <option value="frontend">Frontend Engineer</option>
            <option value="ml">ML Engineer</option>
            <option value="qa">QA Engineer</option>
            <option value="devops">DevOps Engineer</option>
          </select>
        </div>
      </div>

      {/* Candidate Grid */}
      <div>
        {loading ? (
          <div className="flex flex-col items-center justify-center py-16 text-gray-400">
            <Loader2 className="h-6 w-6 animate-spin text-gray-700 mb-2" />
            <p className="text-xs">Loading candidate directory...</p>
          </div>
        ) : filteredEmployees.length === 0 ? (
          <div className="rounded-lg border border-dashed border-gray-300 bg-white p-12 text-center">
            <p className="text-xs font-medium text-gray-700">No candidates match your criteria.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredEmployees.map((emp) => (
              <EmployeeCard key={emp.id} employee={emp} />
            ))}
          </div>
        )}
      </div>

      {/* Import Candidate Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/40 p-4 backdrop-blur-2xs">
          <div className="w-full max-w-2xl rounded-lg border border-gray-200 bg-white p-6 shadow-xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-gray-100 pb-3">
              <div>
                <h3 className="text-sm font-semibold text-gray-900">Import Candidate Profile</h3>
                <p className="text-xs text-gray-500">
                  Select a candidate resume in PDF, Word DOCX, or Image format.
                </p>
              </div>
              <button
                onClick={() => setIsModalOpen(false)}
                className="rounded p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            {uploadError && (
              <div className="mt-3 flex items-center gap-2 rounded bg-rose-50 p-2.5 text-xs text-rose-700 border border-rose-200">
                <AlertCircle className="h-4 w-4 shrink-0" />
                <span>{uploadError}</span>
              </div>
            )}

            {!extractedPreview && (
              <div className="mt-5">
                <label className="flex flex-col items-center justify-center rounded-lg border-2 border-dashed border-gray-300 p-8 text-center cursor-pointer hover:border-gray-400 hover:bg-gray-50/50 transition-colors">
                  <Upload className="h-6 w-6 text-gray-500 mb-2" />
                  <span className="text-xs font-semibold text-gray-900">
                    Upload resume document
                  </span>
                  <span className="text-[11px] text-gray-400 mt-0.5">
                    Supports .pdf, .docx, .png, .jpg, .webp
                  </span>
                  <input
                    type="file"
                    accept=".pdf,.docx,.doc,.png,.jpg,.jpeg,.webp,.txt"
                    onChange={handleFileUpload}
                    disabled={uploading}
                    className="hidden"
                  />
                </label>

                {uploading && (
                  <div className="mt-3 flex items-center justify-center gap-2 text-xs font-medium text-gray-700">
                    <Loader2 className="h-3.5 w-3.5 animate-spin text-gray-900" />
                    <span>Processing file and extracting profile data...</span>
                  </div>
                )}
              </div>
            )}

            {extractedPreview && (
              <div className="mt-4 space-y-4">
                <div className="rounded bg-emerald-50 p-2.5 border border-emerald-200 text-xs text-emerald-800 flex items-center gap-2">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 shrink-0" />
                  <span>
                    Parsed <strong>{extractedPreview.filename}</strong>. Review extracted profile before committing to database.
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div>
                    <label className="font-medium text-gray-700 block mb-1">Candidate Name</label>
                    <input
                      type="text"
                      value={extractedPreview.name}
                      onChange={(e) =>
                        setExtractedPreview({ ...extractedPreview, name: e.target.value })
                      }
                      className="w-full rounded border border-gray-200 p-2 text-xs text-gray-900"
                    />
                  </div>
                  <div>
                    <label className="font-medium text-gray-700 block mb-1">Primary Role</label>
                    <input
                      type="text"
                      value={extractedPreview.role}
                      onChange={(e) =>
                        setExtractedPreview({ ...extractedPreview, role: e.target.value })
                      }
                      className="w-full rounded border border-gray-200 p-2 text-xs text-gray-900"
                    />
                  </div>
                  <div>
                    <label className="font-medium text-gray-700 block mb-1">Years Experience</label>
                    <input
                      type="number"
                      step="0.5"
                      value={extractedPreview.years_experience}
                      onChange={(e) =>
                        setExtractedPreview({
                          ...extractedPreview,
                          years_experience: parseFloat(e.target.value) || 0,
                        })
                      }
                      className="w-full rounded border border-gray-200 p-2 text-xs text-gray-900"
                    />
                  </div>
                  <div>
                    <label className="font-medium text-gray-700 block mb-1">Department</label>
                    <input
                      type="text"
                      value={extractedPreview.department || "Engineering"}
                      onChange={(e) =>
                        setExtractedPreview({ ...extractedPreview, department: e.target.value })
                      }
                      className="w-full rounded border border-gray-200 p-2 text-xs text-gray-900"
                    />
                  </div>
                </div>

                <div>
                  <label className="font-medium text-gray-700 block text-xs mb-1">
                    Extracted Competencies ({extractedPreview.skills?.length || 0})
                  </label>
                  <div className="flex flex-wrap gap-1 p-2 border border-gray-200 rounded bg-gray-50 max-h-24 overflow-y-auto">
                    {extractedPreview.skills?.map((s, idx) => (
                      <span
                        key={idx}
                        className="rounded bg-white px-1.5 py-0.5 text-[11px] font-medium text-gray-700 border border-gray-200"
                      >
                        {s.name} ({s.proficiency || "intermediate"})
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex items-center justify-end gap-2 border-t border-gray-100 pt-3">
                  <button
                    type="button"
                    onClick={() => setExtractedPreview(null)}
                    className="rounded border border-gray-300 px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50"
                  >
                    Select Another
                  </button>
                  <button
                    type="button"
                    onClick={handleSaveEmployee}
                    disabled={saving}
                    className="inline-flex items-center gap-1.5 rounded bg-gray-900 px-3.5 py-1.5 text-xs font-medium text-white hover:bg-gray-800 disabled:opacity-50 shadow-xs"
                  >
                    {saving && <Loader2 className="h-3 w-3 animate-spin" />}
                    <span>Save Candidate</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
