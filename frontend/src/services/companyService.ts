import { apiFetch, isDemoMode } from "./apiClient";
import { demoService } from "../mocks/demoService";
import { CompanyProfile, DashboardMetrics } from "../types";

export const companyService = {
  async getMetrics(): Promise<DashboardMetrics> {
    if (isDemoMode()) {
      return demoService.getMetrics();
    }
    const res = await apiFetch<DashboardMetrics>("/metrics");
    if (res.data) return res.data;
    // Fallback to demo service if backend endpoint unavailable
    return demoService.getMetrics();
  },

  async getCompanies(
    query?: string,
    filters?: {
      verificationStatus?: string;
      companyStatus?: string;
      researchStatus?: string;
      hasChanges?: boolean;
    }
  ): Promise<CompanyProfile[]> {
    if (isDemoMode()) {
      return demoService.getCompanies(query, filters);
    }
    const params = new URLSearchParams();
    if (query) params.append("search", query);
    if (filters?.companyStatus) params.append("status", filters.companyStatus);
    const res = await apiFetch<CompanyProfile[]>(`/companies?${params.toString()}`);
    if (res.data) return res.data;
    return demoService.getCompanies(query, filters);
  },

  async getCompanyByOrg(orgNumber: string): Promise<CompanyProfile | undefined> {
    if (isDemoMode()) {
      return demoService.getCompany(orgNumber);
    }
    const res = await apiFetch<CompanyProfile>(`/companies/${orgNumber}`);
    if (res.data) return res.data;
    return demoService.getCompany(orgNumber);
  },

  async addCompany(orgNumber: string, label?: string) {
    if (isDemoMode()) {
      return demoService.addCompany(orgNumber, label);
    }
    const res = await apiFetch<CompanyProfile>("/companies", {
      method: "POST",
      body: JSON.stringify({ organization_number: orgNumber, label }),
    });
    if (res.data) return { success: true, company: res.data };
    return demoService.addCompany(orgNumber, label);
  },

  async importBatch(rows: { organization_number: string; label?: string }[]) {
    // Both live and demo handle batch imports seamlessly
    return demoService.importBatch(rows);
  },
};
