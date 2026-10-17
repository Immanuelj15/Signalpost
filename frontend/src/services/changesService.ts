import { apiFetch, isDemoMode } from "./apiClient";
import { demoService } from "../mocks/demoService";
import { CompanyChange } from "../types";

export const changesService = {
  async getChanges(): Promise<CompanyChange[]> {
    if (isDemoMode()) {
      return demoService.getAllChanges();
    }
    const res = await apiFetch<CompanyChange[]>("/changes");
    if (res.data) return res.data;
    return demoService.getAllChanges();
  },
};
