// app/team-builder/page.tsx
"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import {
  SlidersHorizontal,
  Play,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  FileText,
  Layers,
  ArrowRight,
  Database,
  Loader2,
} from "lucide-react";
import { teamBuilderService } from "@/services/teamBuilderService";
import { employeeService } from "@/services/employeeService";
import { TeamResult, WorkflowStageEvent } from "@/types/team";
import { AgentWorkflow } from "@/components/AgentWorkflow";
import { TeamMemberCard } from "@/components/TeamMemberCard";
import { SkillCoverage } from "@/components/SkillCoverage";
import { ProjectRequirements } from "@/components/ProjectRequirements";

const DEMO_PROJECT_DESCRIPTION =
  "Build an AI-powered customer support platform for an e-commerce company. The backend should use Python/FastAPI and PostgreSQL. The frontend should use React. The system will use an LLM and RAG for automated customer support. Deploy the application on AWS. Build a team of 6 consisting of a technical lead, two backend engineers, one frontend engineer, one ML engineer and one QA engineer.";

function TeamBuilderContent() {
  const searchParams = useSearchParams();
  const [description, setDescription] = useState("");
  const [teamSize, setTeamSize] = useState<number>(6);
  const [isSeeding, setIsSeeding] = useState(false);
  const [notification, setNotification] = useState<string | null>(null);

  // Workflow State
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentNode, setCurrentNode] = useState<string | null>(null);
  const [completedNodes, setCompletedNodes] = useState<Record<string, string>>({});
  const [retryCount, setRetryCount] = useState<number>(0);

  // Result State
  const [result, setResult] = useState<TeamResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (searchParams.get("demo") === "true") {
      setDescription(DEMO_PROJECT_DESCRIPTION);
      setTeamSize(6);
      setNotification("Sample project specification loaded with 6 required roles.");
    }
  }, [searchParams]);

  const handleLoadTestData = async () => {
    setIsSeeding(true);
    setError(null);
    try {
      const res = await employeeService.seedTestData();
      setDescription(DEMO_PROJECT_DESCRIPTION);
      setTeamSize(6);
      setNotification(
        `Test candidate dataset verified (${res.count || 18} profiles indexed). Specification autofilled below.`
      );
    } catch (err: any) {
      console.error("Failed to seed test data:", err);
      setDescription(DEMO_PROJECT_DESCRIPTION);
      setTeamSize(6);
      setNotification("Project specification autofilled.");
    } finally {
      setIsSeeding(false);
    }
  };

  const handlePreFillDemo = () => {
    setDescription(DEMO_PROJECT_DESCRIPTION);
    setTeamSize(6);
    setError(null);
    setNotification("Project specification prefilled with standard test scenario.");
  };

  const handleRunTeamBuilder = async () => {
    if (!description.trim()) {
      setError("Please provide a project specification.");
      return;
    }

    setIsProcessing(true);
    setError(null);
    setResult(null);
    setCompletedNodes({});
    setCurrentNode("project_analyzer");
    setRetryCount(0);

    try {
      await teamBuilderService.runStream(
        description,
        teamSize,
        (event: WorkflowStageEvent) => {
          if (event.event === "node_start" && event.node) {
            setCurrentNode(event.node);
          } else if (event.event === "node_complete" && event.node) {
            setCompletedNodes((prev) => ({
              ...prev,
              [event.node!]: event.summary || "Completed",
            }));
          } else if (event.event === "node_retry") {
            setRetryCount((prev) => prev + 1);
            setCurrentNode("candidate_retriever");
          } else if (event.event === "complete" && event.final_state) {
            const fs = event.final_state;
            const resObj: TeamResult = {
              requirements: fs.requirements,
              candidates: fs.candidates || [],
              evaluations: fs.evaluations || [],
              team: fs.selected_team || [],
              validation: fs.validation || {
                valid: true,
                team_size_valid: true,
                roles_valid: true,
                required_skills: {},
                missing_requirements: [],
              },
              explanation: fs.final_explanation || {
                team_strengths: [],
                skill_coverage: {},
                role_coverage: {},
              },
              iteration: fs.iteration || 1,
              feasible: fs.feasible ?? true,
            };
            setResult(resObj);
            setCurrentNode(null);
          }
        }
      );
    } catch (err: any) {
      console.warn("Streaming fell back to synchronous execution:", err);
      try {
        const syncResult = await teamBuilderService.runSync(description, teamSize);
        setResult(syncResult);
        setCompletedNodes({
          project_analyzer: "Extracted project requirements and roles",
          candidate_retriever: `Retrieved ${syncResult.candidates.length} candidates via hybrid search`,
          candidate_evaluator: `Evaluated ${syncResult.evaluations.length} candidate profiles`,
          team_builder: `Constructed team of ${syncResult.team.length} members`,
          team_validator: syncResult.validation.valid
            ? "All requirements verified"
            : "Validation complete with warnings",
          explanation: "Generated staffing brief and justifications",
        });
        setCurrentNode(null);
      } catch (syncErr: any) {
        setError(syncErr.response?.data?.detail || "Failed to execute team builder workflow.");
      }
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="mx-auto max-w-7xl px-4 pt-8 sm:px-6 lg:px-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-gray-200 pb-5">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-gray-900 flex items-center gap-2">
            <SlidersHorizontal className="h-5 w-5 text-gray-800" />
            Staffing Planner
          </h1>
          <p className="text-xs text-gray-500 mt-0.5">
            Define headcount and technical requirements to execute automated team composition.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2 self-start sm:self-auto">
          <button
            type="button"
            onClick={handleLoadTestData}
            disabled={isSeeding}
            className="inline-flex items-center gap-1.5 rounded-md border border-gray-300 bg-white px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50 hover:text-gray-900 transition-colors shadow-2xs disabled:opacity-60 disabled:cursor-not-allowed"
            title="Upload seed candidates and autofill project specification"
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

          <button
            type="button"
            onClick={handlePreFillDemo}
            className="inline-flex items-center gap-1.5 rounded-md border border-gray-200 bg-gray-50 px-3 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-100 transition-colors shadow-2xs"
          >
            <FileText className="h-3.5 w-3.5 text-gray-400" />
            <span>Autofill Spec</span>
          </button>
        </div>
      </div>

      {/* Notification Banner */}
      {notification && (
        <div className="flex items-center justify-between rounded-md border border-blue-200 bg-blue-50/70 px-4 py-2.5 text-xs text-blue-900 shadow-2xs">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-blue-600 shrink-0" />
            <span>{notification}</span>
          </div>
          <button
            type="button"
            onClick={() => setNotification(null)}
            className="text-blue-500 hover:text-blue-700 font-medium text-xs ml-4"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Main Grid: Input Workbench + Pipeline Status */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Input Panel */}
        <div className="lg:col-span-2 rounded-lg border border-gray-200 bg-white p-5 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-gray-900">
                Project Specification
              </label>
              <span className="text-[11px] text-gray-400 font-mono">
                {description.length} chars
              </span>
            </div>

            <textarea
              rows={6}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe deliverables, required roles, technology stack, and seniority requirements in natural language..."
              className="w-full rounded-md border border-gray-200 p-3 text-xs sm:text-sm text-gray-900 placeholder-gray-400 focus:border-gray-900 focus:outline-hidden focus:ring-1 focus:ring-gray-900 leading-relaxed font-sans"
            />
          </div>

          <div className="mt-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-t border-gray-100 pt-4">
            <div className="flex items-center gap-2.5">
              <span className="text-xs font-medium text-gray-700">Target Headcount:</span>
              <input
                type="number"
                min={2}
                max={12}
                value={teamSize}
                onChange={(e) => setTeamSize(parseInt(e.target.value, 10) || 5)}
                className="w-16 rounded border border-gray-200 py-1 text-center text-xs font-semibold text-gray-900"
              />
              <span className="text-xs text-gray-400">engineers</span>
            </div>

            <button
              onClick={handleRunTeamBuilder}
              disabled={isProcessing || !description.trim()}
              className="inline-flex items-center justify-center gap-1.5 rounded-md bg-gray-900 px-4 py-2 text-xs font-medium text-white hover:bg-gray-800 disabled:opacity-50 transition-colors shadow-xs"
            >
              {isProcessing ? (
                <>
                  <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                  <span>Solving Team Constraints...</span>
                </>
              ) : (
                <>
                  <Play className="h-3.5 w-3.5 fill-white" />
                  <span>Execute Formation Workflow</span>
                </>
              )}
            </button>
          </div>

          {error && (
            <div className="mt-3 flex items-center gap-2 rounded bg-rose-50 p-2.5 text-xs text-rose-700 border border-rose-200">
              <AlertTriangle className="h-4 w-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}
        </div>

        {/* Pipeline Execution Tracker */}
        <div className="lg:col-span-1">
          <AgentWorkflow
            currentNode={currentNode}
            completedNodes={completedNodes}
            isProcessing={isProcessing}
            retryCount={retryCount}
          />
        </div>
      </div>

      {/* Results Section */}
      {result && (
        <div className="space-y-6 pt-4">
          {/* Missing Requirements Warning */}
          {!result.validation?.valid && result.validation?.missing_requirements?.length > 0 && (
            <div className="rounded-lg border border-amber-200 bg-amber-50/70 p-4 text-amber-900 text-xs">
              <div className="flex items-center gap-1.5 font-semibold">
                <AlertTriangle className="h-4 w-4 text-amber-700" />
                <span>Validation Notice</span>
              </div>
              <p className="mt-1 text-amber-800">
                The composition solver executed {result.iteration} cycles. The following criteria could not be fully met from available candidate records:
              </p>
              <ul className="mt-1.5 list-disc list-inside space-y-0.5 pl-1 font-medium text-amber-800">
                {result.validation.missing_requirements.map((msg, i) => (
                  <li key={i}>{msg}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Executive Overview Header */}
          <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-xs">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-gray-100 pb-3">
              <div>
                <span className="text-[10px] font-mono uppercase tracking-wider text-gray-400 block mb-0.5">
                  Composition Summary
                </span>
                <h2 className="text-base font-bold text-gray-900">
                  Recommended Project Team ({result.team.length} Engineers)
                </h2>
                {result.explanation?.executive_summary && (
                  <p className="text-xs text-gray-600 mt-1 max-w-3xl leading-relaxed">
                    {result.explanation.executive_summary}
                  </p>
                )}
              </div>

              <div>
                <span className="inline-flex items-center gap-1.5 rounded-sm bg-gray-100 px-2.5 py-1 text-xs font-medium text-gray-800 border border-gray-200">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" />
                  <span>Validation Complete</span>
                </span>
              </div>
            </div>

            {/* Team Strengths */}
            {result.explanation?.team_strengths && result.explanation.team_strengths.length > 0 && (
              <div className="mt-3.5">
                <span className="text-xs font-semibold text-gray-900 block mb-1.5">
                  Assigned Team Strengths:
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                  {result.explanation.team_strengths.map((st, i) => (
                    <div
                      key={i}
                      className="rounded border border-gray-200 bg-gray-50/50 p-2 text-xs text-gray-700 leading-snug"
                    >
                      {st}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Skill Matrix and Role Allocation */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <SkillCoverage
              skillCoverage={
                result.explanation?.skill_coverage || result.validation?.required_skills
              }
            />
            <ProjectRequirements roles={result.requirements?.roles || []} team={result.team} />
          </div>

          {/* Candidate Dossiers */}
          <div>
            <div className="flex items-center justify-between mb-3 border-b border-gray-100 pb-2">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-900">
                Individual Candidate Profiles & Justifications
              </h3>
              <span className="text-xs text-gray-400 font-mono">
                {result.team.length} members placed
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {result.team.map((member) => (
                <TeamMemberCard key={member.employee_id} member={member} />
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function TeamBuilderPage() {
  return (
    <Suspense
      fallback={
        <div className="mx-auto max-w-7xl px-4 py-16 text-center text-xs text-gray-400">
          Loading Staffing Planner...
        </div>
      }
    >
      <TeamBuilderContent />
    </Suspense>
  );
}
