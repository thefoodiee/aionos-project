// services/employeeService.ts
import api from "@/lib/axios";
import { Employee, ResumeExtraction } from "@/types/employee";

export const employeeService = {
  async getAll(search?: string, role?: string): Promise<Employee[]> {
    const params: Record<string, string> = {};
    if (search) params.search = search;
    if (role) params.role = role;
    const res = await api.get<Employee[]>("/employees", { params });
    return res.data;
  },

  async getById(id: number): Promise<Employee> {
    const res = await api.get<Employee>(`/employees/${id}`);
    return res.data;
  },

  async uploadResume(file: File): Promise<ResumeExtraction> {
    const formData = new FormData();
    formData.append("file", file);
    const res = await api.post<ResumeExtraction>("/employees/upload-resume", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return res.data;
  },

  async createEmployee(data: any): Promise<Employee> {
    const res = await api.post<Employee>("/employees", data);
    return res.data;
  },

  async seedTestData(force: boolean = false): Promise<{ status: string; count: number; message: string }> {
    const res = await api.post<{ status: string; count: number; message: string }>(
      `/employees/seed${force ? "?force=true" : ""}`
    );
    return res.data;
  },
};
