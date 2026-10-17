import {
  CompanyProfile,
  CompanyChange,
  DashboardMetrics,
  ResearchRun,
  SourceStatus,
} from "../types";
import {
  DEMO_COMPANIES,
  DEMO_METRICS,
  DEMO_RUNS,
  DEMO_SOURCES,
} from "./demoData";
import { validateNorwegianOrg } from "../lib/utils";

class DemoStateService {
  private companies: CompanyProfile[] = [...DEMO_COMPANIES];
  private runs: ResearchRun[] = [...DEMO_RUNS];
  private sources: SourceStatus[] = [...DEMO_SOURCES];
  private metrics: DashboardMetrics = { ...DEMO_METRICS };

  constructor() {
    this.recomputeMetrics();
  }

  private recomputeMetrics() {
    const totalFacts = this.companies.reduce(
      (acc, c) => acc + (c.facts?.length || 0),
      0
    );
    const totalChanges = this.companies.reduce(
      (acc, c) => acc + (c.changes?.length || 0),
      0
    );

    this.metrics = {
      companies_tracked: this.companies.length,
      verified_facts_total: totalFacts,
      changes_detected_total: totalChanges,
      research_runs_total: this.runs.length,
      source_coverage_pct: 95.5,
      outbound_requests_used: this.runs.reduce(
        (acc, r) => acc + r.requests_used,
        0
      ),
      outbound_requests_max: 2000,
      external_api_cost_usd: 0.0,
      is_zero_cost: true,
    };
  }

  public getMetrics(): DashboardMetrics {
    return { ...this.metrics };
  }

  public getCompanies(
    query?: string,
    filters?: {
      verificationStatus?: string;
      companyStatus?: string;
      researchStatus?: string;
      hasChanges?: boolean;
    }
  ): CompanyProfile[] {
    let result = [...this.companies];

    if (query && query.trim() !== "") {
      const q = query.toLowerCase().trim();
      result = result.filter(
        (c) =>
          c.organization_number.includes(q) ||
          (c.company.official_name &&
            c.company.official_name.toLowerCase().includes(q)) ||
          (c.company.industry_codes &&
            c.company.industry_codes.some((i) =>
              i.description.toLowerCase().includes(q)
            ))
      );
    }

    if (filters) {
      if (filters.companyStatus && filters.companyStatus !== "all") {
        result = result.filter(
          (c) => c.company.status?.toLowerCase() === filters.companyStatus?.toLowerCase()
        );
      }
      if (filters.researchStatus && filters.researchStatus !== "all") {
        result = result.filter(
          (c) => c.research_status.toLowerCase() === filters.researchStatus?.toLowerCase()
        );
      }
      if (filters.hasChanges) {
        result = result.filter((c) => c.changes && c.changes.length > 0);
      }
    }

    return result;
  }

  public getCompany(orgNumber: string): CompanyProfile | undefined {
    const cleaned = orgNumber.replace(/[^\d]/g, "");
    return this.companies.find((c) => c.organization_number === cleaned);
  }

  public addCompany(
    orgNumber: string,
    label?: string
  ): { success: boolean; company?: CompanyProfile; error?: string } {
    const validation = validateNorwegianOrg(orgNumber);
    if (!validation.isValid) {
      return { success: false, error: validation.error };
    }

    const cleaned = orgNumber.replace(/[^\d]/g, "");
    const existing = this.getCompany(cleaned);
    if (existing) {
      return {
        success: false,
        error: `Organization number ${cleaned} is already registered in this workspace.`,
      };
    }

    const nowIso = new Date().toISOString();
    const newProfile: CompanyProfile = {
      schema_version: "1.0",
      organization_number: cleaned,
      company: {
        official_name: label ? label.toUpperCase() : `NO-ORG-${cleaned} AS`,
        status: "active",
        organization_type: "AS",
        organization_type_description: "Aksjeselskap",
        registration_date: nowIso.split("T")[0],
        business_address: {
          address: ["Storgata 1"],
          postal_code: "0155",
          city: "OSLO",
          country: "Norge",
          country_code: "NO",
        },
        industry_codes: [
          {
            code: "62.010",
            description: "Programvareutvikling og IT-konsulentvirksomhet",
            priority: "naeringskode1",
          },
        ],
        business_activity: [
          "Utvikling og drift av programvareløsninger, analyse og rådgivning.",
        ],
        employees: 12,
        website: `https://www.nordic-${cleaned}.no`,
        contact_email: `contact@nordic-${cleaned}.no`,
        is_in_bankruptcy: false,
        is_in_liquidation: false,
        is_deleted: false,
        products_and_services: [
          "Enterprise Data Platform",
          "AI Process Automation",
        ],
        business_description: `Discovered enterprise entity ${cleaned}. Profile initialized via Brønnøysund registry protocol.`,
      },
      financials: [
        {
          reporting_period: "2025-01-01 to 2025-12-31",
          year: 2025,
          currency: "NOK",
          unit: "exact_amount",
          statement_type: "SELSKAP",
          accounting_rules: "regnskapslovenAlminneligRegler",
          total_revenue: 18500000,
          sales_revenue: 18200000,
          operating_profit: 3200000,
          profit_before_tax: 3100000,
          net_profit: 2418000,
          total_assets: 14500000,
          total_equity: 8200000,
          total_debt: 6300000,
          source_url: `https://data.brreg.no/regnskapsregisteret/regnskap/${cleaned}`,
          filing_id: 6100230,
        },
      ],
      facts: [
        {
          fact_id: `fact-${cleaned}-name`,
          organization_number: cleaned,
          field_name: "official_name",
          value: label ? label.toUpperCase() : `NO-ORG-${cleaned} AS`,
          data_type: "string",
          source_name: "brreg_enhetsregisteret",
          source_url: `https://data.brreg.no/enhetsregisteret/api/enheter/${cleaned}`,
          retrieved_at: nowIso,
          verification_status: "verified",
          confidence: 1.0,
          extraction_method: "deterministic_api",
          evidence_excerpt: `Organisasjonsnummer: ${cleaned}, Navn: ${
            label ? label.toUpperCase() : `NO-ORG-${cleaned} AS`
          }`,
        },
        {
          fact_id: `fact-${cleaned}-status`,
          organization_number: cleaned,
          field_name: "status",
          value: "active",
          data_type: "string",
          source_name: "brreg_enhetsregisteret",
          source_url: `https://data.brreg.no/enhetsregisteret/api/enheter/${cleaned}`,
          retrieved_at: nowIso,
          verification_status: "verified",
          confidence: 1.0,
          extraction_method: "deterministic_api",
        },
      ],
      changes: [
        {
          change_id: `chg-${cleaned}-init`,
          organization_number: cleaned,
          field_name: "initial_profile",
          previous_value: null,
          new_value: "Active profile registered",
          detected_at: nowIso,
          change_type: "initial_discovery",
          confidence: 1.0,
          review_status: "unreviewed",
          new_source: "brreg_enhetsregisteret",
        },
      ],
      missing_fields: [],
      identity_status: "verified",
      research_status: "complete",
      last_researched_at: nowIso,
      errors: [],
      explanations: ["Profile created successfully in local workspace."],
    };

    this.companies.unshift(newProfile);
    this.recomputeMetrics();
    return { success: true, company: newProfile };
  }

  public importBatch(
    rows: { organization_number: string; label?: string }[]
  ): {
    total: number;
    validCount: number;
    invalidCount: number;
    duplicateCount: number;
    imported: CompanyProfile[];
    errors: { orgNumber: string; reason: string }[];
  } {
    let validCount = 0;
    let invalidCount = 0;
    let duplicateCount = 0;
    const imported: CompanyProfile[] = [];
    const errors: { orgNumber: string; reason: string }[] = [];

    for (const row of rows) {
      const raw = row.organization_number || "";
      const validation = validateNorwegianOrg(raw);
      if (!validation.isValid) {
        invalidCount++;
        errors.push({ orgNumber: raw, reason: validation.error || "Invalid format" });
        continue;
      }

      const cleaned = raw.replace(/[^\d]/g, "");
      if (this.getCompany(cleaned)) {
        duplicateCount++;
        errors.push({
          orgNumber: cleaned,
          reason: "Duplicate organization number in database",
        });
        continue;
      }

      const res = this.addCompany(cleaned, row.label);
      if (res.success && res.company) {
        validCount++;
        imported.push(res.company);
      } else {
        invalidCount++;
        errors.push({ orgNumber: cleaned, reason: res.error || "Unknown error" });
      }
    }

    if (imported.length > 0) {
      const nowIso = new Date().toISOString();
      const newRun: ResearchRun = {
        run_id: `run-${Math.random().toString(36).substring(2, 10)}`,
        batch_name: `Batch Import (${imported.length} orgs)`,
        run_type: "batch",
        started_at: nowIso,
        finished_at: nowIso,
        companies_requested: rows.length,
        companies_completed: imported.length,
        requests_used: imported.length * 2,
        external_api_cost_usd: 0.0,
        run_status: "completed",
        errors_summary: {
          invalid_rows: invalidCount,
          duplicates: duplicateCount,
        },
      };
      this.runs.unshift(newRun);
    }

    this.recomputeMetrics();

    return {
      total: rows.length,
      validCount,
      invalidCount,
      duplicateCount,
      imported,
      errors,
    };
  }

  public triggerResearch(orgNumber: string): {
    success: boolean;
    run?: ResearchRun;
    message?: string;
  } {
    const company = this.getCompany(orgNumber);
    if (!company) {
      return { success: false, message: `Company ${orgNumber} not found.` };
    }

    const nowIso = new Date().toISOString();
    company.last_researched_at = nowIso;
    company.research_status = "complete";

    const newRun: ResearchRun = {
      run_id: `run-${Math.random().toString(36).substring(2, 10)}`,
      batch_name: `Re-research ${company.company.official_name || orgNumber}`,
      run_type: "refresh",
      started_at: nowIso,
      finished_at: nowIso,
      companies_requested: 1,
      companies_completed: 1,
      requests_used: 2,
      external_api_cost_usd: 0.0,
      run_status: "completed",
      errors_summary: {},
    };

    this.runs.unshift(newRun);
    this.recomputeMetrics();
    return { success: true, run: newRun };
  }

  public getAllChanges(): CompanyChange[] {
    const list: CompanyChange[] = [];
    for (const c of this.companies) {
      if (c.changes && c.changes.length > 0) {
        list.push(...c.changes);
      }
    }
    return list.sort(
      (a, b) =>
        new Date(b.detected_at).getTime() - new Date(a.detected_at).getTime()
    );
  }

  public getRuns(): ResearchRun[] {
    return [...this.runs];
  }

  public getSources(): SourceStatus[] {
    return [...this.sources];
  }
}

export const demoService = new DemoStateService();
