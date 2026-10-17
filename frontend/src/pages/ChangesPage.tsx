import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { changesService } from "../services/changesService";
import { CompanyChange } from "../types";
import { formatDate, formatDateTime } from "../lib/utils";
import {
  History,
  Search,
  Filter,
  ArrowRight,
  ExternalLink,
  ShieldCheck,
  Building,
  CheckCircle2,
  AlertTriangle,
  Info,
} from "lucide-react";

export const ChangesPage: React.FC = () => {
  const [changes, setChanges] = useState<CompanyChange[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setIsLoading(true);
      try {
        const data = await changesService.getChanges();
        setChanges(data);
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, []);

  const filteredChanges = changes.filter((ch) => {
    const matchesSearch =
      !searchQuery ||
      ch.organization_number.includes(searchQuery) ||
      ch.field_name.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesType =
      typeFilter === "all" || ch.change_type === typeFilter;

    return matchesSearch && matchesType;
  });

  const getChangeTypeBadge = (type: string) => {
    switch (type) {
      case "genuine_company_change":
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            Genuine Registry Change
          </span>
        );
      case "extraction_correction":
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-sky-500/10 text-sky-400 border border-sky-500/20">
            Extraction Update
          </span>
        );
      case "source_correction":
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">
            Source Correction
          </span>
        );
      case "initial_discovery":
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-800 text-slate-300 border border-slate-700">
            Baseline Discovery
          </span>
        );
      default:
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-800 text-slate-300">
            {type}
          </span>
        );
    }
  };

  return (
    <div className="space-y-6 animate-fade-in pb-16">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">
            Changes & Monitoring
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Review verified changes and state transitions across Norwegian corporate profiles with side-by-side diffs.
          </p>
        </div>
      </div>

      {/* Search & Filter Bar */}
      <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex flex-col md:flex-row items-center gap-3">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by field name or organization number..."
            className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-700/80 rounded-lg text-xs text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500 transition-colors"
          />
        </div>

        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="px-3 py-2 bg-slate-950 border border-slate-700/80 rounded-lg text-xs text-slate-300 focus:outline-none focus:border-sky-500 w-full md:w-auto"
        >
          <option value="all">All Change Classifications</option>
          <option value="genuine_company_change">Genuine Registry Change</option>
          <option value="extraction_correction">Extraction Update</option>
          <option value="source_correction">Source Correction</option>
          <option value="initial_discovery">Baseline Discovery</option>
        </select>
      </div>

      {/* Changes Feed List */}
      <div className="space-y-4">
        {isLoading ? (
          <div className="py-16 text-center text-xs text-slate-500">
            Loading change history...
          </div>
        ) : filteredChanges.length === 0 ? (
          <div className="p-12 rounded-xl bg-slate-900/60 border border-slate-800 text-center space-y-2">
            <History className="w-8 h-8 text-slate-600 mx-auto" />
            <h3 className="text-sm font-semibold text-slate-200">
              No change records match filter
            </h3>
            <p className="text-xs text-slate-400">
              Delta changes are generated whenever fresh registry snapshots differ from previous profiles.
            </p>
          </div>
        ) : (
          filteredChanges.map((ch) => (
            <div
              key={ch.change_id}
              className="p-5 rounded-xl bg-slate-900/70 border border-slate-800 hover:border-slate-700 transition-colors shadow-sm space-y-3"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/80 pb-3">
                <div className="flex items-center gap-2.5">
                  <div className="p-2 rounded-lg bg-slate-800 text-sky-400">
                    <Building className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <Link
                        to={`/companies/${ch.organization_number}`}
                        className="text-xs font-semibold text-slate-100 hover:text-sky-300 font-mono transition-colors"
                      >
                        Org {ch.organization_number}
                      </Link>
                      <span className="text-slate-500">•</span>
                      <span className="text-xs font-medium text-slate-200">
                        Field: <span className="text-sky-400 font-mono">{ch.field_name}</span>
                      </span>
                    </div>
                    <div className="text-[11px] text-slate-500">
                      Detected {formatDateTime(ch.detected_at)} via {ch.new_source || "brreg_enhetsregisteret"}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {getChangeTypeBadge(ch.change_type)}
                  <Link
                    to={`/companies/${ch.organization_number}`}
                    className="p-1.5 text-slate-400 hover:text-slate-100 rounded-lg hover:bg-slate-800 transition-colors"
                    title="Open company profile"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>

              {/* Side-by-side Before/After diff */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs font-mono">
                <div className="p-3 rounded-lg bg-red-950/20 border border-red-900/40 text-red-300">
                  <div className="text-[10px] text-red-400 uppercase font-sans mb-1 flex items-center justify-between">
                    <span>Previous Value</span>
                    <span>Snapshot A</span>
                  </div>
                  <div className="whitespace-pre-wrap break-all">
                    {ch.previous_value !== null && ch.previous_value !== undefined
                      ? String(ch.previous_value)
                      : "<null / not present>"}
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-emerald-950/20 border border-emerald-900/40 text-emerald-300">
                  <div className="text-[10px] text-emerald-400 uppercase font-sans mb-1 flex items-center justify-between">
                    <span>New Value</span>
                    <span>Snapshot B (Current)</span>
                  </div>
                  <div className="whitespace-pre-wrap break-all">
                    {String(ch.new_value)}
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
