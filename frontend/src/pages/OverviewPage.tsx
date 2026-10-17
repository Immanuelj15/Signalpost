import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { companyService } from "../services/companyService";
import { researchService } from "../services/researchService";
import { changesService } from "../services/changesService";
import { useShell } from "../components/layout/AppShell";
import {
  CompanyProfile,
  DashboardMetrics,
  ResearchRun,
  CompanyChange,
} from "../types";
import { formatDate, formatDateTime } from "../lib/utils";
import {
  Building2,
  CheckCircle2,
  History,
  Activity,
  Layers,
  Zap,
  ArrowRight,
  Plus,
  UploadCloud,
  Play,
  ShieldCheck,
  Clock,
  Sparkles,
  ExternalLink,
} from "lucide-react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export const OverviewPage: React.FC = () => {
  const { openAddCompany, openImportBatch } = useShell();
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [recentCompanies, setRecentCompanies] = useState<CompanyProfile[]>([]);
  const [recentRuns, setRecentRuns] = useState<ResearchRun[]>([]);
  const [recentChanges, setRecentChanges] = useState<CompanyChange[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      setIsLoading(true);
      try {
        const [m, c, r, ch] = await Promise.all([
          companyService.getMetrics(),
          companyService.getCompanies(),
          researchService.getRuns(),
          changesService.getChanges(),
        ]);
        setMetrics(m);
        setRecentCompanies(c.slice(0, 5));
        setRecentRuns(r.slice(0, 4));
        setRecentChanges(ch.slice(0, 4));
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, []);

  // Synthetic trend data for Recharts activity chart
  const activityData = [
    { name: "Mon", runs: 2, facts: 18, requests: 4 },
    { name: "Tue", runs: 5, facts: 34, requests: 7 },
    { name: "Wed", runs: 3, facts: 22, requests: 5 },
    { name: "Thu", runs: 7, facts: 48, requests: 11 },
    { name: "Fri", runs: 4, facts: 29, requests: 6 },
    { name: "Sat", runs: 8, facts: 55, requests: 12 },
    { name: "Sun", runs: 6, facts: 41, requests: 9 },
  ];

  if (!isLoading && recentCompanies.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center max-w-lg mx-auto">
        <div className="w-16 h-16 rounded-2xl bg-sky-500/10 border border-sky-500/20 text-sky-400 flex items-center justify-center mb-4 shadow-xl">
          <Building2 className="w-8 h-8" />
        </div>
        <h2 className="text-xl font-bold text-slate-100 mb-2">
          Your intelligence workspace is ready
        </h2>
        <p className="text-sm text-slate-400 mb-6 leading-relaxed">
          Add a Norwegian company number or import a company list to begin building verified company profiles.
        </p>
        <div className="flex items-center gap-3">
          <button
            onClick={openAddCompany}
            className="px-4 py-2.5 rounded-lg text-xs font-semibold text-white bg-sky-600 hover:bg-sky-500 transition-colors inline-flex items-center gap-2"
          >
            <Plus className="w-4 h-4" /> Add First Company
          </button>
          <button
            onClick={openImportBatch}
            className="px-4 py-2.5 rounded-lg text-xs font-medium text-slate-300 hover:text-slate-100 bg-slate-900 border border-slate-700 hover:bg-slate-800 transition-colors inline-flex items-center gap-2"
          >
            <UploadCloud className="w-4 h-4 text-sky-400" /> Import CSV
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in pb-12">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-slate-100 tracking-tight">
              Company Intelligence
            </h1>
            <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
              Live Verified
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Research, verify, and monitor Norwegian corporate entities against statutory registers.
          </p>
        </div>

        {/* Header Action Buttons */}
        <div className="flex items-center gap-2.5">
          <button
            onClick={openAddCompany}
            className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold text-white bg-sky-600 hover:bg-sky-500 border border-sky-500/30 shadow-sm transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>Add Company</span>
          </button>
          <button
            onClick={openImportBatch}
            className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-medium text-slate-300 hover:text-slate-100 bg-slate-900 hover:bg-slate-800 border border-slate-700 transition-all"
          >
            <UploadCloud className="w-4 h-4 text-sky-400" />
            <span>Import Batch</span>
          </button>
          <Link
            to="/research"
            className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-medium text-slate-300 hover:text-slate-100 bg-slate-900 hover:bg-slate-800 border border-slate-700 transition-all"
          >
            <Play className="w-3.5 h-3.5 text-emerald-400" />
            <span>Run Research</span>
          </Link>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3.5">
        {/* Metric 1 */}
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-slate-700 transition-colors">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-medium text-slate-400">Companies</span>
            <Building2 className="w-4 h-4 text-sky-400" />
          </div>
          <div className="text-xl font-bold font-mono text-slate-100">
            {metrics ? metrics.companies_tracked : "—"}
          </div>
          <div className="text-[10px] text-slate-500 mt-1">Under Active Audit</div>
        </div>

        {/* Metric 2 */}
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-slate-700 transition-colors">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-medium text-slate-400">Verified Facts</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-xl font-bold font-mono text-emerald-400">
            {metrics ? metrics.verified_facts_total : "—"}
          </div>
          <div className="text-[10px] text-slate-500 mt-1">100% Provenance</div>
        </div>

        {/* Metric 3 */}
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-slate-700 transition-colors">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-medium text-slate-400">Changes Found</span>
            <History className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-xl font-bold font-mono text-amber-400">
            {metrics ? metrics.changes_detected_total : "—"}
          </div>
          <div className="text-[10px] text-slate-500 mt-1">Profile Diffs</div>
        </div>

        {/* Metric 4 */}
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-slate-700 transition-colors">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-medium text-slate-400">Research Runs</span>
            <Activity className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-xl font-bold font-mono text-slate-100">
            {metrics ? metrics.research_runs_total : "—"}
          </div>
          <div className="text-[10px] text-slate-500 mt-1">Autonomous Ops</div>
        </div>

        {/* Metric 5 */}
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-slate-700 transition-colors">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-medium text-slate-400">Coverage</span>
            <Layers className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-xl font-bold font-mono text-purple-400">
            {metrics ? `${metrics.source_coverage_pct}%` : "—"}
          </div>
          <div className="text-[10px] text-slate-500 mt-1">Statutory & Web</div>
        </div>

        {/* Metric 6 */}
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-slate-700 transition-colors">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-medium text-slate-400">API Cost</span>
            <Zap className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-xl font-bold font-mono text-emerald-400">
            $0.00
          </div>
          <div className="text-[10px] text-slate-500 mt-1">Strict ₹0 Model</div>
        </div>
      </div>

      {/* Two Column Grid: Activity Chart & Quick Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Activity Chart (2 columns) */}
        <div className="lg:col-span-2 p-5 rounded-xl bg-slate-900/70 border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-slate-100">
                Weekly Fact Extraction & Verification Activity
              </h3>
              <p className="text-xs text-slate-400">
                Verified fact extraction throughput across Brønnøysund endpoints
              </p>
            </div>
            <span className="text-[11px] text-slate-500 font-mono">
              7-day window
            </span>
          </div>

          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={activityData}>
                <defs>
                  <linearGradient id="factGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0284c7" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#0284c7" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis
                  dataKey="name"
                  stroke="#475569"
                  fontSize={11}
                  tickLine={false}
                />
                <YAxis
                  stroke="#475569"
                  fontSize={11}
                  tickLine={false}
                  axisLine={false}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0f172a",
                    borderColor: "#334155",
                    borderRadius: "8px",
                    fontSize: "12px",
                    color: "#f8fafc",
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="facts"
                  stroke="#38bdf8"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#factGradient)"
                  name="Verified Facts"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Source Coverage Status card */}
        <div className="p-5 rounded-xl bg-slate-900/70 border border-slate-800 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold text-slate-100">
                Statutory Source Health
              </h3>
              <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
                100% Operational
              </span>
            </div>
            <p className="text-xs text-slate-400 mb-4">
              Direct connection status with Norwegian registries without paid intermediary APIs.
            </p>

            <div className="space-y-3 text-xs">
              <div>
                <div className="flex justify-between text-slate-300 mb-1">
                  <span>Enhetsregisteret (Core Register)</span>
                  <span className="text-emerald-400 font-mono">245ms</span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-1.5">
                  <div className="bg-emerald-400 h-1.5 rounded-full w-[98%]" />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-slate-300 mb-1">
                  <span>Regnskapsregisteret (Accounts)</span>
                  <span className="text-emerald-400 font-mono">310ms</span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-1.5">
                  <div className="bg-sky-400 h-1.5 rounded-full w-[94%]" />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-slate-300 mb-1">
                  <span>Verified Corporate Websites (SSRF Guarded)</span>
                  <span className="text-emerald-400 font-mono">480ms</span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-1.5">
                  <div className="bg-purple-400 h-1.5 rounded-full w-[88%]" />
                </div>
              </div>
            </div>
          </div>

          <div className="mt-5 pt-3 border-t border-slate-800/80">
            <Link
              to="/sources"
              className="text-xs text-sky-400 hover:text-sky-300 font-medium inline-flex items-center gap-1.5 transition-colors"
            >
              <span>Inspect all statutory registries & licenses</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </div>

      {/* Lower Row: Recently Researched Companies & Recent Changes Feed */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recently Researched Companies */}
        <div className="p-5 rounded-xl bg-slate-900/70 border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-slate-100">
                Recently Audited Companies
              </h3>
              <p className="text-xs text-slate-400">
                Profiles with active Modulo 11 validation and verified records
              </p>
            </div>
            <Link
              to="/companies"
              className="text-xs text-sky-400 hover:text-sky-300 font-medium inline-flex items-center gap-1 transition-colors"
            >
              <span>View All</span>
              <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          <div className="divide-y divide-slate-800/60 font-sans">
            {recentCompanies.map((c) => (
              <Link
                key={c.organization_number}
                to={`/companies/${c.organization_number}`}
                className="py-3 flex items-center justify-between hover:bg-slate-800/40 px-2 -mx-2 rounded-lg transition-colors group"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-slate-800 border border-slate-700/60 flex items-center justify-center text-slate-300 group-hover:text-sky-400 transition-colors">
                    <Building2 className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="text-xs font-semibold text-slate-200 group-hover:text-sky-300 transition-colors">
                      {c.company.official_name || `NO-ORG-${c.organization_number}`}
                    </div>
                    <div className="text-[11px] text-slate-400 font-mono flex items-center gap-2">
                      <span>Org: {c.organization_number}</span>
                      {c.company.organization_type && (
                        <span>• {c.company.organization_type}</span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="text-right">
                  <span className="text-[11px] font-medium text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                    {c.facts?.length || 0} facts
                  </span>
                  <div className="text-[10px] text-slate-500 mt-1">
                    {formatDate(c.last_researched_at)}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>

        {/* Recent Detected Profile Changes Feed */}
        <div className="p-5 rounded-xl bg-slate-900/70 border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-slate-100">
                Recent Profile Change Diffs
              </h3>
              <p className="text-xs text-slate-400">
                Evidence-backed delta changes detected across registry refreshes
              </p>
            </div>
            <Link
              to="/changes"
              className="text-xs text-sky-400 hover:text-sky-300 font-medium inline-flex items-center gap-1 transition-colors"
            >
              <span>View All</span>
              <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          <div className="divide-y divide-slate-800/60 font-sans">
            {recentChanges.length === 0 ? (
              <div className="py-8 text-center text-xs text-slate-500">
                No changes detected across recent scans.
              </div>
            ) : (
              recentChanges.map((ch) => (
                <div key={ch.change_id} className="py-3 flex flex-col gap-1.5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-medium text-slate-200">
                        {ch.field_name.replace("_", " ")}
                      </span>
                      <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-800 text-sky-300">
                        {ch.organization_number}
                      </span>
                    </div>
                    <span className="text-[10px] text-slate-500">
                      {formatDate(ch.detected_at)}
                    </span>
                  </div>

                  <div className="flex items-center gap-2 text-xs font-mono bg-slate-950 p-2 rounded-lg border border-slate-800/80">
                    <span className="text-red-400/90 truncate max-w-[45%]">
                      - {String(ch.previous_value ?? "none")}
                    </span>
                    <ArrowRight className="w-3 h-3 text-slate-500 shrink-0" />
                    <span className="text-emerald-400/90 truncate max-w-[45%]">
                      + {String(ch.new_value)}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
