// types/team.ts
export interface ProjectRoleRequirement {
  role: string;
  count: number;
}

export interface ProjectRequirement {
  team_size: number;
  roles: ProjectRoleRequirement[];
  required_skills: string[];
  preferred_skills: string[];
  domain: string;
}

export interface CandidateItem {
  employee_id: number;
  name: string;
  role: string;
  years_experience: number;
  department?: string;
  skills: string[];
  evidence: string[];
  relevance_score?: number;
}

export interface CandidateEvaluation {
  employee_id: number;
  name: string;
  role: string;
  role_fit: number;
  skill_fit: number;
  experience_fit: number;
  domain_fit: number;
  overall_fit: number;
  strengths: string[];
  gaps: string[];
  evidence: string[];
}

export interface TeamMember {
  employee_id: number;
  name: string;
  role: string;
  assigned_role: string;
  project_fit: number;
  skills: string[];
  why_selected: string;
  strengths: string[];
  gaps: string[];
  evidence: string[];
}

export interface TeamValidation {
  valid: boolean;
  team_size_valid: boolean;
  roles_valid: boolean;
  required_skills: Record<string, boolean>;
  missing_requirements: string[];
  iteration?: number;
}

export interface TeamExplanation {
  team_strengths: string[];
  skill_coverage: Record<string, boolean>;
  role_coverage: Record<string, string>;
  executive_summary?: string;
}

export interface TeamResult {
  requirements: ProjectRequirement;
  candidates: CandidateItem[];
  evaluations: CandidateEvaluation[];
  team: TeamMember[];
  validation: TeamValidation;
  explanation: TeamExplanation;
  iteration: number;
  feasible: boolean;
}

export interface WorkflowStageEvent {
  event: "start" | "node_start" | "node_complete" | "node_retry" | "complete" | "error";
  node?: string;
  message?: string;
  summary?: string;
  data?: any;
  final_state?: any;
}
