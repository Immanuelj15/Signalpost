import React, { useState, useEffect } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { companyService } from "../services/companyService";
import { researchService } from "../services/researchService";
import { exportService } from "../services/exportService";
import { useShell } from "../components/layout/AppShell";
import { CompanyProfile, CompanyFact } from "../types";
import {
  formatDate,
  formatDateTime,
  formatCurrency,
  formatNumber,
} from "../lib/utils";
import {
  Building2,
  ShieldCheck,
  Globe,
  Mail,
  Phone,
  MapPin,
  Calendar,
  Layers,
  ArrowLeft,
  RefreshCw,
  Download,
  ExternalLink,
  CheckCircle2,
  AlertTriangle,
  Clock,
  History,
  TrendingUp,
  FileText,
  DollarSign,
  ChevronRight,
  Info,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

export const CompanyProfilePage: React.FC = () => {
  const { orgNumber } = useParams<{ orgNumber: string }>();
  const navigate = useNavigate();
  const { openEvidence } = useShell();

  const [company, setCompany] = useState<CompanyProfile | null>(null);
  const [activeTab, setActiveTab] = useState<
    "overview" | "facts" | "financials" | "activity" | "history"
  >("overview");
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    async function load() {
      if (!orgNumber) return;
      setIsLoading(true);
      try {
        const data = await companyService.getCompanyByOrg(orgNumber);
        setCompany(data || null);
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, [orgNumber]);

  const handleRefresh = async () => {
    if (!orgNumber) return;
    setIsRefreshing(true);
    try {
      await researchService.triggerResearch(orgNumber);
      const updated = await companyService.getCompanyByOrg(orgNumber);
      setCompany(updated || null);
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleExport = () => {
    if (!company) return;
    exportService.exportCompaniesToJson(
      [company],
      `company_${company.organization_number}.json`
    );
  };

  if (isLoading) {
    return (
      <div className="py-20 text-center text-slate-500 text-sm">
        Loading authoritative profile for {orgNumber}...
      </div>
    );
  }

  if (!company) {
    return (
      <div className="py-20 text-center space-y-4">
        <Building2 className="w-12 h-12 text-slate-600 mx-auto" />
        <h2 className="text-xl font-bold text-slate-200">
          Company Not Found
        </h2>
        <p className="text-xs text-slate-400 max-w-sm mx-auto">
          No profile for organization number {orgNumber} exists in the local workspace.
        </p>
        <Link
          to="/companies"
          className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-medium text-slate-300 hover:text-white bg-slate-800"
        >
          <ArrowLeft className="w-3.5 h-3.5" /> Back to Company Explorer
        </Link>
      </div>
    );
  }

  const primaryIndustry = company.company.industry_codes?.[0];
  const chartFinancials = (company.financials || [])
    .slice()
    .reverse()
    .map((f) => ({
      year: f.year,
      revenue: f.total_revenue ? Math.round(f.total_revenue / 1000000) : 0,
      operatingProfit: f.operating_profit
        ? Math.round(f.operating_profit / 1000000)
        : 0,
      currency: f.currency,
    }));

  return (
    <div className="space-y-6 animate-fade-in pb-16">
      {/* Back button & Breadcrumbs */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <Link
          to="/companies"
          className="hover:text-slate-200 flex items-center gap-1 transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Company Explorer</span>
        </Link>
        <ChevronRight className="w-3 h-3 text-slate-600" />
        <span className="text-slate-200 font-medium">
          {company.company.official_name || company.organization_number}
        </span>
      </div>

      {/* Main Profile Header Banner */}
      <div className="p-6 rounded-xl bg-slate-900/90 border border-slate-800 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="flex flex-wrap items-center gap-2.5">
            <h1 className="text-2xl font-bold text-slate-100 tracking-tight">
              {company.company.official_name}
            </h1>
            <span className="px-2.5 py-0.5 rounded text-xs font-mono font-medium bg-slate-800 text-sky-400 border border-slate-700">
              {company.company.organization_type || "Entity"}
            </span>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Identity Verified</span>
            </span>
          </div>

          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-400">
            <span className="font-mono text-sky-300">
              Org Nr: {company.organization_number}
            </span>
            {primaryIndustry && (
              <span>
                • {primaryIndustry.code} ({primaryIndustry.description})
              </span>
            )}
            {company.company.business_address?.city && (
              <span>• {company.company.business_address.city}, Norway</span>
            )}
            <span className="text-slate-500">
              • Researched {formatDate(company.last_researched_at)}
            </span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2.5 shrink-0">
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-medium text-slate-300 hover:text-slate-100 bg-slate-800 hover:bg-slate-700 border border-slate-700 transition-colors disabled:opacity-50"
          >
            <RefreshCw
              className={`w-3.5 h-3.5 text-sky-400 ${
                isRefreshing ? "animate-spin" : ""
              }`}
            />
            <span>Refresh Research</span>
          </button>
          <button
            onClick={handleExport}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-medium text-slate-300 hover:text-slate-100 bg-slate-800 hover:bg-slate-700 border border-slate-700 transition-colors"
          >
            <Download className="w-3.5 h-3.5 text-emerald-400" />
            <span>Export Profile</span>
          </button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b border-slate-800 flex items-center gap-2 overflow-x-auto text-xs">
        {[
          { id: "overview", label: "Overview", icon: Building2 },
          {
            id: "facts",
            label: `Facts & Evidence (${company.facts?.length || 0})`,
            icon: ShieldCheck,
          },
          {
            id: "financials",
            label: `Financials (${company.financials?.length || 0})`,
            icon: DollarSign,
          },
          {
            id: "activity",
            label: "Activity & Web",
            icon: Globe,
          },
          {
            id: "history",
            label: `Audit History (${company.changes?.length || 0})`,
            icon: History,
          },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex items-center gap-2 px-4 py-3 font-medium border-b-2 transition-colors whitespace-nowrap ${
              activeTab === tab.id
                ? "border-sky-500 text-sky-400 bg-sky-500/5 font-semibold"
                : "border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/50"
            }`}
          >
            <tab.icon className="w-4 h-4" />
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* TAB 1: OVERVIEW */}
      {activeTab === "overview" && (
        <div className="space-y-6">
          {/* Business Description / Summary Card */}
          {company.company.business_description && (
            <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                Entity Summary
              </h3>
              <p className="text-xs text-slate-200 leading-relaxed">
                {company.company.business_description}
              </p>
            </div>
          )}

          {/* Quick Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Registration Card */}
            <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
              <div className="flex items-center justify-between text-xs text-slate-400 border-b border-slate-800/80 pb-2">
                <span className="font-semibold text-slate-300">Registration Details</span>
                <span className="text-emerald-400 text-[11px] font-mono">Enhetsregisteret</span>
              </div>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-slate-400">Org Form:</span>
                  <span className="text-slate-200 font-medium">
                    {company.company.organization_type_description ||
                      company.company.organization_type}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Registration Date:</span>
                  <span className="text-slate-200 font-mono">
                    {formatDate(company.company.registration_date)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Incorporation Date:</span>
                  <span className="text-slate-200 font-mono">
                    {formatDate(company.company.incorporation_date)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Registered Employees:</span>
                  <span className="text-slate-200 font-mono">
                    {formatNumber(company.company.employees)}
                  </span>
                </div>
              </div>
            </div>

            {/* Address & Location Card */}
            <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
              <div className="flex items-center justify-between text-xs text-slate-400 border-b border-slate-800/80 pb-2">
                <span className="font-semibold text-slate-300">Registered Address</span>
                <MapPin className="w-3.5 h-3.5 text-sky-400" />
              </div>
              <div className="text-xs text-slate-300 space-y-1">
                {company.company.business_address?.address?.map((line, i) => (
                  <div key={i}>{line}</div>
                ))}
                <div>
                  {company.company.business_address?.postal_code}{" "}
                  {company.company.business_address?.city}
                </div>
                <div>{company.company.business_address?.country}</div>
              </div>
            </div>

            {/* Public Contact Card */}
            <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
              <div className="flex items-center justify-between text-xs text-slate-400 border-b border-slate-800/80 pb-2">
                <span className="font-semibold text-slate-300">Official Web & Contact</span>
                <Globe className="w-3.5 h-3.5 text-sky-400" />
              </div>
              <div className="space-y-2 text-xs">
                {company.company.website ? (
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Website:</span>
                    <a
                      href={company.company.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sky-400 hover:text-sky-300 inline-flex items-center gap-1 font-mono"
                    >
                      <span>{company.company.website.replace("https://", "")}</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                ) : (
                  <div className="text-slate-500 italic">No website verified</div>
                )}
                {company.company.contact_email && (
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Email:</span>
                    <span className="text-slate-200 font-mono">
                      {company.company.contact_email}
                    </span>
                  </div>
                )}
                {company.company.contact_phone && (
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Phone:</span>
                    <span className="text-slate-200 font-mono">
                      {company.company.contact_phone}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Business Activity & Products */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Statutory Business Activity */}
            <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3">
                Statutory Business Activity (vedtektsfestet formål)
              </h3>
              <ul className="space-y-2 text-xs text-slate-300 list-disc list-inside">
                {company.company.business_activity?.map((act, idx) => (
                  <li key={idx} className="leading-relaxed">
                    {act}
                  </li>
                ))}
              </ul>
            </div>

            {/* Discovered Products & Services */}
            <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3">
                Products & Services Discovered
              </h3>
              {company.company.products_and_services?.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {company.company.products_and_services.map((p, i) => (
                    <span
                      key={i}
                      className="px-2.5 py-1 rounded-lg text-xs bg-slate-800 border border-slate-700 text-slate-200"
                    >
                      {p}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-500 italic">
                  No verified products or services catalogued.
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: FACTS & EVIDENCE */}
      {activeTab === "facts" && (
        <div className="border border-slate-800 rounded-xl overflow-hidden bg-slate-900/60 shadow-xl">
          <div className="p-4 bg-slate-950/80 border-b border-slate-800 flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-slate-100">
                Authoritative Fact Ledger & Provenance
              </h3>
              <p className="text-xs text-slate-400">
                Every claim links directly to its timestamped statutory or web evidence excerpt
              </p>
            </div>
            <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded border border-emerald-500/20">
              {company.facts?.length || 0} Audited Facts
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950/60 text-[11px] font-semibold text-slate-400 uppercase tracking-wider border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Field Name</th>
                  <th className="py-3 px-4">Extracted Value</th>
                  <th className="py-3 px-4">Verification</th>
                  <th className="py-3 px-4">Source</th>
                  <th className="py-3 px-4">Retrieved</th>
                  <th className="py-3 px-4 text-right">Audit</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-sans">
                {company.facts?.map((fact) => (
                  <tr
                    key={fact.fact_id}
                    className="hover:bg-slate-800/40 transition-colors"
                  >
                    <td className="py-3 px-4 font-mono text-sky-300 font-medium">
                      {fact.field_name}
                    </td>
                    <td className="py-3 px-4 max-w-xs truncate text-slate-200">
                      {typeof fact.value === "object"
                        ? JSON.stringify(fact.value)
                        : String(fact.value)}
                    </td>
                    <td className="py-3 px-4">
                      <span className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                        <CheckCircle2 className="w-3 h-3" />
                        <span>Verified</span>
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-400">
                      {fact.source_name}
                    </td>
                    <td className="py-3 px-4 text-slate-500 font-mono text-[11px]">
                      {formatDate(fact.retrieved_at)}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => openEvidence(fact)}
                        className="inline-flex items-center gap-1 px-2.5 py-1 rounded text-[11px] font-medium bg-sky-500/10 text-sky-400 hover:bg-sky-500/20 border border-sky-500/30 transition-colors"
                      >
                        <span>View Evidence</span>
                        <ExternalLink className="w-3 h-3" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 3: FINANCIALS */}
      {activeTab === "financials" && (
        <div className="space-y-6">
          {(!company.financials || company.financials.length === 0) ? (
            <div className="p-8 rounded-xl bg-slate-900/60 border border-slate-800 text-center">
              <Info className="w-8 h-8 text-sky-400 mx-auto mb-2" />
              <h3 className="text-sm font-semibold text-slate-200">
                No verified commercial financial statements available
              </h3>
              <p className="text-xs text-slate-400 max-w-md mx-auto mt-1">
                Non-commercial entities, public administrative bodies, and entities exempt under the Norwegian Accounting Act do not file annual statements with Regnskapsregisteret.
              </p>
            </div>
          ) : (
            <>
              {/* Financial Chart */}
              {chartFinancials.length > 0 && (
                <div className="p-5 rounded-xl bg-slate-900/70 border border-slate-800">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="text-sm font-semibold text-slate-100">
                        Financial Performance Trend (Annual Filings)
                      </h3>
                      <p className="text-xs text-slate-400">
                        Total Revenue vs Operating Profit (millions in reporting currency)
                      </p>
                    </div>
                    <span className="text-xs font-mono text-slate-400">
                      {company.financials[0]?.currency} Millions
                    </span>
                  </div>

                  <div className="h-64 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={chartFinancials}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                        <XAxis dataKey="year" stroke="#475569" fontSize={11} />
                        <YAxis stroke="#475569" fontSize={11} />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: "#0f172a",
                            borderColor: "#334155",
                            borderRadius: "8px",
                            fontSize: "12px",
                            color: "#f8fafc",
                          }}
                        />
                        <Bar
                          dataKey="revenue"
                          name="Total Revenue (M)"
                          fill="#38bdf8"
                          radius={[4, 4, 0, 0]}
                        />
                        <Bar
                          dataKey="operatingProfit"
                          name="Operating Profit (M)"
                          fill="#10b981"
                          radius={[4, 4, 0, 0]}
                        />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}

              {/* Financials Table */}
              <div className="border border-slate-800 rounded-xl overflow-hidden bg-slate-900/60 shadow-xl">
                <div className="p-4 bg-slate-950/80 border-b border-slate-800 flex justify-between items-center">
                  <h3 className="text-sm font-semibold text-slate-100">
                    Regnskapsregisteret Statutory Statements
                  </h3>
                  <span className="text-[11px] font-mono text-slate-400">
                    IFRS / Norwegian Accounting Act Compliant
                  </span>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs text-slate-300">
                    <thead className="bg-slate-950/60 text-[11px] font-semibold text-slate-400 uppercase tracking-wider border-b border-slate-800">
                      <tr>
                        <th className="py-3 px-4">Financial Year</th>
                        <th className="py-3 px-4">Scope</th>
                        <th className="py-3 px-4 text-right">Total Revenue</th>
                        <th className="py-3 px-4 text-right">Operating Profit (EBIT)</th>
                        <th className="py-3 px-4 text-right">Net Profit</th>
                        <th className="py-3 px-4 text-right">Total Assets</th>
                        <th className="py-3 px-4 text-right">Total Equity</th>
                        <th className="py-3 px-4 text-right">Source</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 font-mono">
                      {company.financials.map((f, idx) => (
                        <tr key={idx} className="hover:bg-slate-800/40">
                          <td className="py-3 px-4 font-bold text-slate-100">
                            {f.year}
                          </td>
                          <td className="py-3 px-4 font-sans text-slate-400">
                            {f.statement_type} ({f.accounting_rules || "Statutory"})
                          </td>
                          <td className="py-3 px-4 text-right text-sky-300">
                            {formatCurrency(f.total_revenue, f.currency)}
                          </td>
                          <td className="py-3 px-4 text-right text-emerald-400">
                            {formatCurrency(f.operating_profit, f.currency)}
                          </td>
                          <td className="py-3 px-4 text-right text-slate-200">
                            {formatCurrency(f.net_profit, f.currency)}
                          </td>
                          <td className="py-3 px-4 text-right text-slate-300">
                            {formatCurrency(f.total_assets, f.currency)}
                          </td>
                          <td className="py-3 px-4 text-right text-slate-300">
                            {formatCurrency(f.total_equity, f.currency)}
                          </td>
                          <td className="py-3 px-4 text-right font-sans">
                            <a
                              href={f.source_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-sky-400 hover:text-sky-300 inline-flex items-center gap-1 text-[11px]"
                            >
                              <span>Brreg</span>
                              <ExternalLink className="w-3 h-3" />
                            </a>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* TAB 4: ACTIVITY & WEB */}
      {activeTab === "activity" && (
        <div className="space-y-4">
          <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800">
            <h3 className="text-sm font-semibold text-slate-100 mb-1">
              Public Disclosures & Website Discoveries
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Discovered corporate updates extracted with strict SSRF-safe HTTP fetching.
            </p>

            <div className="space-y-3 font-sans text-xs">
              <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 flex items-start justify-between">
                <div>
                  <div className="font-semibold text-slate-200">
                    Official Web Domain Verification
                  </div>
                  <p className="text-slate-400 text-[11px] mt-0.5">
                    Domain {company.company.website || "primary site"} matched against registrar records.
                  </p>
                </div>
                <span className="text-[11px] font-mono text-emerald-400">
                  {formatDate(company.last_researched_at)}
                </span>
              </div>

              <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 flex items-start justify-between">
                <div>
                  <div className="font-semibold text-slate-200">
                    Statutory Executive Registration
                  </div>
                  <p className="text-slate-400 text-[11px] mt-0.5">
                    Public role confirmation recorded under Brønnøysund Enhetsregisteret.
                  </p>
                </div>
                <span className="text-[11px] font-mono text-slate-400">
                  {formatDate(company.company.registration_date)}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 5: AUDIT HISTORY */}
      {activeTab === "history" && (
        <div className="space-y-4">
          <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-semibold text-slate-100">
                  Change Audit Log & Profile Evolution
                </h3>
                <p className="text-xs text-slate-400">
                  Every change is tracked with before-and-after values and evidence provenance
                </p>
              </div>
              <span className="text-xs font-mono text-amber-400 bg-amber-500/10 px-2.5 py-1 rounded border border-amber-500/20">
                {company.changes?.length || 0} Recorded Changes
              </span>
            </div>

            {(!company.changes || company.changes.length === 0) ? (
              <p className="text-xs text-slate-500 italic py-6 text-center">
                No subsequent field modifications detected since baseline intake.
              </p>
            ) : (
              <div className="divide-y divide-slate-800/80">
                {company.changes.map((ch) => (
                  <div key={ch.change_id} className="py-4 space-y-2">
                    <div className="flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-slate-200">
                          {ch.field_name.replace("_", " ")}
                        </span>
                        <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-sky-300 font-mono">
                          {ch.change_type.replace("_", " ")}
                        </span>
                      </div>
                      <span className="text-slate-500 text-[11px] font-mono">
                        {formatDateTime(ch.detected_at)}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-3 text-xs font-mono">
                      <div className="p-2.5 rounded bg-red-950/20 border border-red-900/40 text-red-300">
                        <div className="text-[10px] text-red-400 uppercase font-sans mb-0.5">
                          Previous Value
                        </div>
                        <div className="truncate">
                          {String(ch.previous_value ?? "none")}
                        </div>
                      </div>
                      <div className="p-2.5 rounded bg-emerald-950/20 border border-emerald-900/40 text-emerald-300">
                        <div className="text-[10px] text-emerald-400 uppercase font-sans mb-0.5">
                          New Value
                        </div>
                        <div className="truncate">
                          {String(ch.new_value)}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
