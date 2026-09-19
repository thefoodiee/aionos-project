// services/teamBuilderService.ts
import api, { getBaseURL } from "@/lib/axios";
import { TeamResult, ProjectRequirement, WorkflowStageEvent } from "@/types/team";

export const teamBuilderService = {
  async analyze(description: string, teamSize?: number): Promise<ProjectRequirement> {
    const res = await api.post<ProjectRequirement>("/team-builder/analyze", {
      project_description: description,
      team_size: teamSize,
    });
    return res.data;
  },

  async runSync(description: string, teamSize?: number): Promise<TeamResult> {
    const res = await api.post<TeamResult>("/team-builder/run", {
      project_description: description,
      team_size: teamSize,
    });
    return res.data;
  },

  async runStream(
    description: string,
    teamSize: number | undefined,
    onEvent: (event: WorkflowStageEvent) => void
  ): Promise<void> {
    const baseUrl = (api.defaults.baseURL || getBaseURL()).replace(/\/$/, "");
    const response = await fetch(`${baseUrl}/team-builder/stream-run`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        project_description: description,
        team_size: teamSize,
      }),
    });

    if (!response.ok) {
      throw new Error(`Streaming failed: HTTP ${response.status} ${response.statusText}`);
    }

    if (!response.body) {
      throw new Error("No response body received for streaming");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n\n");
      buffer = lines.pop() || "";

      for (const block of lines) {
        const trimmed = block.trim();
        if (trimmed.startsWith("data:")) {
          const jsonStr = trimmed.replace(/^data:\s*/, "");
          try {
            const eventData = JSON.parse(jsonStr) as WorkflowStageEvent;
            onEvent(eventData);
          } catch (err) {
            console.error("Error parsing SSE block:", err, jsonStr);
          }
        }
      }
    }
  },
};
