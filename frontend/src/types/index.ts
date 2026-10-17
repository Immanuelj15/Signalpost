export type VerificationStatus =
  | "verified"
  | "derived"
  | "unverified"
  | "unavailable"
  | "stale"
  | "conflicting";

export type ExtractionMethod =
  | "deterministic_api"
  | "rule_based_html"
  | "derived"
  | "optional_llm";

export type IdentityStatus = "verified" | "mismatch" | "unverified" | "invalid";

export type ResearchStatus = "complete" | "partial" | "failed" | "not_found";

export type ChangeType =
  | "genuine_company_change"
  | "extraction_correction"
  | "source_correction"
  | "initial_discovery";

export type RunStatus =
  | "queued"
  | "running"
  | "completed"
  | "partial"
  | "failed"
  | "cancelled";

export interface Address {
  address: string[];
  postal_code?: string;
  city?: string;
  municipality?: string;
  municipality_number?: string;
  country?: string;
  country_code?: string;
}

export interface IndustryCode {
  code: string;
  description: string;
  priority?: string;
}

export interface CompanyFact {
  fact_id: string;
  organization_number: string;
  field_name: string;
  value: any;
  data_type: string;
  source_name: string;
  source_url: string;
  retrieved_at: string;
  published_at?: string;
  reporting_period?: string;
  evidence_excerpt?: string;
  verification_status: VerificationStatus;
  confidence: number;
  extraction_method: ExtractionMethod;
  content_hash?: string;
}

export interface FinancialStatement {
  reporting_period: string;
  year: number;
  currency: string;
  unit: string;
  statement_type: "SELSKAP" | "KONSERN" | string;
  accounting_rules?: string;
  total_revenue?: number;
  sales_revenue?: number;
  operating_profit?: number;
  profit_before_tax?: number;
  net_profit?: number;
  total_assets?: number;
  total_equity?: number;
  total_debt?: number;
  source_url: string;
  filing_id?: number;
  journal_number?: string;
}

export interface CompanyCoreData {
  official_name?: string;
  status?: string;
  organization_type?: string;
  organization_type_description?: string;
  registration_date?: string;
  incorporation_date?: string;
  business_address?: Address;
  postal_address?: Address;
  industry_codes: IndustryCode[];
  business_activity: string[];
  employees?: number;
  website?: string;
  contact_email?: string;
  contact_phone?: string;
  parent_organization?: string;
  is_in_liquidation: boolean;
  is_in_bankruptcy: boolean;
  is_deleted: boolean;
  deleted_date?: string;
  products_and_services: string[];
  business_description?: string;
}

export interface CompanyChange {
  change_id: string;
  organization_number: string;
  field_name: string;
  previous_value: any;
  new_value: any;
  previous_source?: string;
  new_source?: string;
  detected_at: string;
  previous_snapshot_id?: string;
  current_snapshot_id?: string;
  evidence_reference?: string;
  change_type: ChangeType;
  confidence: number;
  review_status: string;
}

export interface CompanySnapshot {
  snapshot_id: string;
  organization_number: string;
  created_at: string;
  normalized_profile_json: string;
  profile_hash: string;
}

export interface CompanyProfile {
  schema_version: string;
  organization_number: string;
  company: CompanyCoreData;
  financials: FinancialStatement[];
  facts: CompanyFact[];
  changes: CompanyChange[];
  missing_fields: string[];
  identity_status: IdentityStatus;
  research_status: ResearchStatus;
  last_researched_at?: string;
  errors: string[];
  explanations: string[];
}

export interface ResearchRun {
  run_id: string;
  started_at: string;
  finished_at?: string;
  companies_requested: number;
  companies_completed: number;
  requests_used: number;
  external_api_cost_usd: number;
  run_status: RunStatus;
  errors_summary: Record<string, number>;
  batch_name?: string;
  run_type?: "single" | "batch" | "refresh";
}

export interface SourceStatus {
  source_name: string;
  display_name: string;
  source_type: "api" | "html" | "filing";
  base_url: string;
  is_active: boolean;
  facts_count: number;
  last_retrieval_at: string;
  latency_ms: number;
  licensing: string;
  description: string;
  limitations: string;
}

export interface DashboardMetrics {
  companies_tracked: number;
  verified_facts_total: number;
  changes_detected_total: number;
  research_runs_total: number;
  source_coverage_pct: number;
  outbound_requests_used: number;
  outbound_requests_max: number;
  external_api_cost_usd: number;
  is_zero_cost: boolean;
}
