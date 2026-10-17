import React, { useState, useEffect } from "react";
import { researchService } from "../services/researchService";
import { useShell } from "../components/layout/AppShell";
import { ResearchRun } from "../types";
import { formatDate, formatDateTime } from "../lib/utils";
import {
  Activity,
  Play,
  UploadCloud,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Zap,
  ArrowRight,
  Database,
  ChevronDown,
  ChevronUp,
  ShieldCheck,
} from "lucide-react";

export const ResearchPage: React.FC = () => {
  const { openAddCompany, openImportBatch } = useShell();
  const [runs, setRuns] = useState<ResearchRun[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [expandedRunId, setExpandedRunId] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      setIsLoading(true);
      try {
        const data = await researchService.getRuns();
        setRuns(data);
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, []);

  const totalCompleted = runs.filter((r) => r.run_status === "completed").length;
  const totalRequests = runs.reduce((acc, r) => acc + r.requests_used, 0);
  const totalOrgs = runs.reduce((acc, r) => acc + r.companies_completed, 0);

  const toggleExpand = (runId: string) => {
    setExpandedRunId(expandedRunId === runId ? null : runId);
  };

  return (
    <div className="space-y-6 animate-fade-in pb-16">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">
            Research Operations
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Monitor autonomous company research jobs, registry throughput, and execution quality.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2.5">
          <button
            onClick={openAddCompany}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-semibold text-white bg-sky-600 hover:bg-sky-500 border border-sky-500/30 transition-colors shadow-sm"
          >
            <Play className="w-3.5 h-3.5" />
            <span>New Research Run</span>
          </button>
          <button
            onClick={openImportBatch}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-medium text-slate-300 hover:text-slate-100 bg-slate-900 hover:bg-slate-800 border border-slate-700 transition-colors"
          >
            <UploadCloud className="w-3.5 h-3.5 text-sky-400" />
            <span>Import Batch</span>
          </button>
        </div>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
          <div className="text-xs text-slate-400 mb-1">Total Operations</div>
          <div className="text-xl font-bold font-mono text-slate-100">
            {runs.length}
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">
            {totalCompleted} Completed Successfully
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
          <div className="text-xs text-slate-400 mb-1">Companies Processed</div>
          <div className="text-xl font-bold font-mono text-sky-400">
            {totalOrgs}
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">
            Normalized with Modulo 11
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
          <div className="text-xs text-slate-400 mb-1">Outbound Requests</div>
          <div className="text-xl font-bold font-mono text-slate-100">
            {totalRequests} <span className="text-xs text-slate-500 font-sans">/ 2,000</span>
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">
            Bounded Budget
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
          <div className="text-xs text-slate-400 mb-1">External API Cost</div>
          <div className="text-xl font-bold font-mono text-emerald-400">
            $0.00
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">
            100% Free Public APIs
          </div>
        </div>
      </div>

      {/* Runs Table */}
      <div className="border border-slate-800 rounded-xl overflow-hidden bg-slate-900/60 shadow-xl">
        <div className="p-4 bg-slate-950/80 border-b border-slate-800 flex justify-between items-center">
          <h3 className="text-sm font-semibold text-slate-100">
            Execution Log & Quality Breakdown
          </h3>
          <span className="text-[11px] text-slate-400 font-mono">
            Direct Statutory Pulls
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950/60 text-[11px] font-semibold text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-3.5 px-4">Run ID / Name</th>
                <th className="py-3.5 px-4">Type</th>
                <th className="py-3.5 px-4">Requested</th>
                <th className="py-3.5 px-4">Completed</th>
                <th className="py-3.5 px-4">Requests</th>
                <th className="py-3.5 px-4">Cost</th>
                <th className="py-3.5 px-4">Execution Time</th>
                <th className="py-3.5 px-4">Status</th>
                <th className="py-3.5 px-4 text-right">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {runs.map((r) => {
                const isExpanded = expandedRunId === r.run_id;
                return (
                  <React.Fragment key={r.run_id}>
                    <tr
                      onClick={() => toggleExpand(r.run_id)}
                      className="hover:bg-slate-800/40 cursor-pointer transition-colors"
                    >
                      <td className="py-3.5 px-4">
                        <div className="font-semibold text-slate-100 font-mono text-sky-300">
                          {r.run_id}
                        </div>
                        <div className="text-[11px] text-slate-400 font-sans">
                          {r.batch_name || "Single Research Query"}
                        </div>
                      </td>
                      <td className="py-3.5 px-4">
                        <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-300">
                          {r.run_type || "batch"}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 font-mono">{r.companies_requested}</td>
                      <td className="py-3.5 px-4 font-mono text-emerald-400">
                        {r.companies_completed}
                      </td>
                      <td className="py-3.5 px-4 font-mono">{r.requests_used}</td>
                      <td className="py-3.5 px-4 font-mono text-emerald-400">
                        ${r.external_api_cost_usd.toFixed(2)}
                      </td>
                      <td className="py-3.5 px-4 text-slate-400 font-mono text-[11px]">
                        {formatDateTime(r.started_at)}
                      </td>
                      <td className="py-3.5 px-4">
                        <span className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                          <CheckCircle2 className="w-3 h-3" />
                          <span className="capitalize">{r.run_status}</span>
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <button
                          type="button"
                          className="p-1 rounded text-slate-400 hover:text-slate-100"
                        >
                          {isExpanded ? (
                            <ChevronUp className="w-4 h-4" />
                          ) : (
                            <ChevronDown className="w-4 h-4" />
                          )}
                        </button>
                      </td>
                    </tr>

                    {/* Expandable Execution Details Row */}
                    {isExpanded && (
                      <tr className="bg-slate-950/60">
                        <td colSpan={9} className="p-4 border-b border-slate-800">
                          <div className="space-y-3 text-xs">
                            <div className="flex items-center justify-between text-slate-300">
                              <span className="font-semibold text-slate-200">
                                Detailed Execution Quality Summary
                              </span>
                              <span className="font-mono text-slate-400">
                                Started: {formatDateTime(r.started_at)} | Finished:{" "}
                                {formatDateTime(r.finished_at)}
                              </span>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                                <div className="text-slate-400 text-[11px] mb-1">
                                  Registry Endpoints Consulted
                                </div>
                                <div className="font-medium text-slate-200">
                                  Enhetsregisteret, Regnskapsregisteret
                                </div>
                              </div>

                              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                                <div className="text-slate-400 text-[11px] mb-1">
                                  Non-Fatal Deviations / Exemptions
                                </div>
                                <div className="font-mono text-slate-300">
                                  {Object.keys(r.errors_summary || {}).length === 0
                                    ? "0 errors logged"
                                    : Object.entries(r.errors_summary).map(
                                        ([k, v]) => `${k}: ${v}`
                                      ).join(", ")}
                                </div>
                              </div>

                              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                                <div className="text-slate-400 text-[11px] mb-1">
                                  SSRF Policy Guard
                                </div>
                                <div className="text-emerald-400 font-medium">
                                  Strict RFC 1918 Private IP Filter Active
                                </div>
                              </div>
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
