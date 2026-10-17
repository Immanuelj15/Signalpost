import { apiFetch, isDemoMode } from "./apiClient";
import { demoService } from "../mocks/demoService";
import { ResearchRun, SourceStatus } from "../types";

export const researchService = {
  async getRuns(): Promise<ResearchRun[]> {
    if (isDemoMode()) {
      return demoService.getRuns();
    }
    const res = await apiFetch<ResearchRun[]>("/research/runs");
    if (res.data) return res.data;
    return demoService.getRuns();
  },

  async triggerResearch(orgNumber: string) {
    if (isDemoMode()) {
      return demoService.triggerResearch(orgNumber);
    }
    const res = await apiFetch<ResearchRun>(`/companies/${orgNumber}/research`, {
      method: "POST",
    });
    if (res.data) return { success: true, run: res.data };
    return demoService.triggerResearch(orgNumber);
  },

  async getSources(): Promise<SourceStatus[]> {
    if (isDemoMode()) {
      return demoService.getSources();
    }
    const res = await apiFetch<SourceStatus[]>("/sources");
    if (res.data) return res.data;
    return demoService.getSources();
  },
};
