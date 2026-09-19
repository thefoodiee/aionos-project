// types/employee.ts
export interface SkillItem {
  id?: number;
  name: string;
  proficiency: string;
  years?: number;
  years_experience?: number;
}

export interface ProjectItem {
  id?: number;
  name: string;
  domain?: string;
  description?: string;
  role?: string;
  technologies?: string[];
}

export interface Employee {
  id: number;
  name: string;
  email?: string;
  role: string;
  department?: string;
  years_experience: number;
  skills: SkillItem[];
  projects: ProjectItem[];
  resume_filename?: string;
  resume_text?: string;
  created_at?: string;
}

export interface ResumeExtraction {
  name: string;
  role: string;
  years_experience: number;
  department?: string;
  skills: SkillItem[];
  projects: ProjectItem[];
  certifications?: string[];
  education?: string[];
  raw_text: string;
  filename: string;
}
