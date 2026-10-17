import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { companyService } from "../services/companyService";
import { exportService } from "../services/exportService";
import { researchService } from "../services/researchService";
import { useShell } from "../components/layout/AppShell";
import { CompanyProfile } from "../types";
import { formatDate } from "../lib/utils";
import {
  Building2,
  Search,
  Filter,
  Plus,
  UploadCloud,
  Download,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  ShieldCheck,
  AlertTriangle,
  RefreshCw,
  MoreVertical,
  CheckCircle2,
  Clock,
} from "lucide-react";

export const CompaniesPage: React.FC = () => {
  const { openAddCompany, openImportBatch } = useShell();
  const navigate = useNavigate();

  const [companies, setCompanies] = useState<CompanyProfile[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [researchFilter, setResearchFilter] = useState("all");
  const [hasChangesFilter, setHasChangesFilter] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [page, setPage] = useState(1);
  const pageSize = 8;
  const [activeMenuOrg, setActiveMenuOrg] = useState<string | null>(null);

  const loadCompanies = async () => {
    setIsLoading(true);
    try {
      const data = await companyService.getCompanies(searchQuery, {
        companyStatus: statusFilter,
        researchStatus: researchFilter,
        hasChanges: hasChangesFilter,
      });
      setCompanies(data);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadCompanies();
  }, [searchQuery, statusFilter, researchFilter, hasChangesFilter]);

  const handleExportJson = () => {
    exportService.exportCompaniesToJson(companies);
  };

  const handleExportCsv = () => {
    exportService.exportCompaniesToCsv(companies);
  };

  const handleRefreshResearch = async (e: React.MouseEvent, orgNumber: string) => {
    e.stopPropagation();
    await researchService.triggerResearch(orgNumber);
    loadCompanies();
    setActiveMenuOrg(null);
  };

  // Pagination
  const totalPages = Math.max(1, Math.ceil(companies.length / pageSize));
  const displayedCompanies = companies.slice(
    (page - 1) * pageSize,
    page * pageSize
  );

  return (
    <div className="space-y-6 animate-fade-in pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">
            Company Explorer
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Browse and manage researched Norwegian corporate entities and their verified public records.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2.5">
          <button
            onClick={openAddCompany}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-semibold text-white bg-sky-600 hover:bg-sky-500 border border-sky-500/30 transition-colors shadow-sm"
          >
            <Plus className="w-4 h-4" />
            <span>Add Company</span>
          </button>
          <button
            onClick={openImportBatch}
            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium text-slate-300 hover:text-slate-100 bg-slate-900 hover:bg-slate-800 border border-slate-700 transition-colors"
          >
            <UploadCloud className="w-4 h-4 text-sky-400" />
            <span>Import CSV</span>
          </button>
          <div className="relative inline-block text-left">
            <button
              onClick={handleExportCsv}
              title="Export filtered companies to CSV"
              className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium text-slate-300 hover:text-slate-100 bg-slate-900 hover:bg-slate-800 border border-slate-700 transition-colors"
            >
              <Download className="w-4 h-4 text-emerald-400" />
              <span>Export CSV</span>
            </button>
          </div>
          <button
            onClick={handleExportJson}
            title="Export filtered companies to JSON"
            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium text-slate-300 hover:text-slate-100 bg-slate-900 hover:bg-slate-800 border border-slate-700 transition-colors"
          >
            <span>JSON</span>
          </button>
        </div>
      </div>

      {/* Search & Filter Bar */}
      <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex flex-col md:flex-row items-center gap-3">
        {/* Search Input */}
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setPage(1);
            }}
            placeholder="Search company name or organization number..."
            className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-700/80 rounded-lg text-xs text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500 transition-colors"
          />
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-2.5 w-full md:w-auto">
          {/* Company Status */}
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(1);
            }}
            className="px-3 py-2 bg-slate-950 border border-slate-700/80 rounded-lg text-xs text-slate-300 focus:outline-none focus:border-sky-500"
          >
            <option value="all">All Corporate Statuses</option>
            <option value="active">Active</option>
            <option value="deleted">Deleted / Inactive</option>
          </select>

          {/* Research Status */}
          <select
            value={researchFilter}
            onChange={(e) => {
              setResearchFilter(e.target.value);
              setPage(1);
            }}
            className="px-3 py-2 bg-slate-950 border border-slate-700/80 rounded-lg text-xs text-slate-300 focus:outline-none focus:border-sky-500"
          >
            <option value="all">All Research Statuses</option>
            <option value="complete">Complete</option>
            <option value="partial">Partial</option>
            <option value="failed">Failed</option>
          </select>

          {/* Has Changes Checkbox */}
          <label className="flex items-center gap-2 px-3 py-2 bg-slate-950 border border-slate-700/80 rounded-lg text-xs text-slate-300 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={hasChangesFilter}
              onChange={(e) => {
                setHasChangesFilter(e.target.checked);
                setPage(1);
              }}
              className="rounded bg-slate-900 border-slate-700 text-sky-500 focus:ring-0"
            />
            <span>Has Detected Changes</span>
          </label>
        </div>
      </div>

      {/* Data Table */}
      <div className="border border-slate-800 rounded-xl overflow-hidden bg-slate-900/60 shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950/80 text-[11px] font-semibold text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-3.5 px-4">Company Name</th>
                <th className="py-3.5 px-4">Org Number</th>
                <th className="py-3.5 px-4">Industry Classification</th>
                <th className="py-3.5 px-4">Status</th>
                <th className="py-3.5 px-4 text-center">Verified Facts</th>
                <th className="py-3.5 px-4">Last Researched</th>
                <th className="py-3.5 px-4">Research Quality</th>
                <th className="py-3.5 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {isLoading ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-500">
                    Loading verified company records...
                  </td>
                </tr>
              ) : displayedCompanies.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center">
                    <Building2 className="w-8 h-8 text-slate-600 mx-auto mb-2" />
                    <div className="text-slate-300 font-medium">No companies found</div>
                    <div className="text-slate-500 text-[11px] mt-0.5">
                      Try adjusting your search criteria or register a new company number.
                    </div>
                  </td>
                </tr>
              ) : (
                displayedCompanies.map((c) => {
                  const primaryIndustry = c.company.industry_codes?.[0];
                  return (
                    <tr
                      key={c.organization_number}
                      onClick={() => navigate(`/companies/${c.organization_number}`)}
                      className="hover:bg-slate-800/40 cursor-pointer transition-colors group"
                    >
                      {/* Name */}
                      <td className="py-3.5 px-4 font-semibold text-slate-100 group-hover:text-sky-400 transition-colors">
                        <div className="flex items-center gap-2">
                          <span>{c.company.official_name || "—"}</span>
                          {c.company.organization_type && (
                            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                              {c.company.organization_type}
                            </span>
                          )}
                        </div>
                      </td>

                      {/* Org Number */}
                      <td className="py-3.5 px-4 font-mono text-sky-300">
                        {c.organization_number}
                      </td>

                      {/* Industry */}
                      <td className="py-3.5 px-4 max-w-[200px] truncate text-slate-400">
                        {primaryIndustry
                          ? `${primaryIndustry.code} - ${primaryIndustry.description}`
                          : "—"}
                      </td>

                      {/* Status */}
                      <td className="py-3.5 px-4">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium ${
                            c.company.status === "active"
                              ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                              : "bg-red-500/10 text-red-400 border border-red-500/20"
                          }`}
                        >
                          {c.company.status || "active"}
                        </span>
                      </td>

                      {/* Facts Count */}
                      <td className="py-3.5 px-4 text-center">
                        <span className="inline-flex items-center gap-1 font-mono text-emerald-400 font-semibold bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                          <ShieldCheck className="w-3 h-3" />
                          {c.facts?.length || 0}
                        </span>
                      </td>

                      {/* Last Researched */}
                      <td className="py-3.5 px-4 text-slate-400 font-mono text-[11px]">
                        {formatDate(c.last_researched_at)}
                      </td>

                      {/* Research Quality */}
                      <td className="py-3.5 px-4">
                        <span
                          className={`inline-flex items-center gap-1 text-[11px] font-medium ${
                            c.research_status === "complete"
                              ? "text-emerald-400"
                              : c.research_status === "partial"
                              ? "text-amber-400"
                              : "text-red-400"
                          }`}
                        >
                          {c.research_status === "complete" ? (
                            <CheckCircle2 className="w-3.5 h-3.5" />
                          ) : (
                            <Clock className="w-3.5 h-3.5" />
                          )}
                          <span className="capitalize">{c.research_status}</span>
                        </span>
                      </td>

                      {/* Actions */}
                      <td className="py-3.5 px-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            type="button"
                            onClick={(e) => handleRefreshResearch(e, c.organization_number)}
                            title="Trigger re-research"
                            className="p-1 rounded text-slate-400 hover:text-sky-400 hover:bg-slate-800 transition-colors"
                          >
                            <RefreshCw className="w-3.5 h-3.5" />
                          </button>
                          <Link
                            to={`/companies/${c.organization_number}`}
                            onClick={(e) => e.stopPropagation()}
                            className="p-1 rounded text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition-colors"
                          >
                            <ExternalLink className="w-3.5 h-3.5" />
                          </Link>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        <div className="px-4 py-3 bg-slate-950/80 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
          <div>
            Showing {(page - 1) * pageSize + 1} to{" "}
            {Math.min(page * pageSize, companies.length)} of {companies.length} companies
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="p-1.5 rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="font-mono text-slate-200">
              Page {page} of {totalPages}
            </span>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="p-1.5 rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
