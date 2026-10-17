import React, { useState, useEffect } from "react";
import { researchService } from "../services/researchService";
import { SourceStatus } from "../types";
import { formatDateTime } from "../lib/utils";
import {
  Database,
  ExternalLink,
  ShieldCheck,
  CheckCircle2,
  Clock,
  Layers,
  Info,
  Server,
  Lock,
} from "lucide-react";

export const SourcesPage: React.FC = () => {
  const [sources, setSources] = useState<SourceStatus[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setIsLoading(true);
      try {
        const data = await researchService.getSources();
        setSources(data);
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="space-y-6 animate-fade-in pb-16">
      {/* Header */}
      <div className="border-b border-slate-800/80 pb-5">
        <h1 className="text-2xl font-bold text-slate-100 tracking-tight">
          Sources & Provenance Registry
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Statutory Norwegian government databases and SSRF-guarded corporate web sources used for evidence extraction.
        </p>
      </div>

      {/* Grid of Source Cards */}
      <div className="grid grid-cols-1 gap-6">
        {sources.map((src) => (
          <div
            key={src.source_name}
            className="p-6 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-slate-700 transition-colors shadow-lg space-y-4"
          >
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800/80 pb-4">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-sky-500/10 border border-sky-500/20 text-sky-400">
                  <Database className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-100">
                    {src.display_name}
                  </h3>
                  <div className="flex items-center gap-2 text-xs font-mono text-slate-400 mt-0.5">
                    <span>Key: {src.source_name}</span>
                    <span>•</span>
                    <span className="capitalize">{src.source_type} protocol</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>100% Operational</span>
                </span>
              </div>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed">
              {src.description}
            </p>

            {/* Metrics & Metadata Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 text-xs">
              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                <div className="text-slate-400 text-[11px] mb-1">
                  Supported Facts
                </div>
                <div className="font-mono text-sm font-semibold text-emerald-400">
                  {src.facts_count} Verified Facts
                </div>
              </div>

              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                <div className="text-slate-400 text-[11px] mb-1">
                  Average Latency
                </div>
                <div className="font-mono text-sm font-semibold text-sky-400">
                  {src.latency_ms} ms
                </div>
              </div>

              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                <div className="text-slate-400 text-[11px] mb-1">
                  Cost per Request
                </div>
                <div className="font-mono text-sm font-semibold text-emerald-400">
                  $0.00 (Public NLOD)
                </div>
              </div>

              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                <div className="text-slate-400 text-[11px] mb-1">
                  Last Validated
                </div>
                <div className="font-mono text-[11px] text-slate-300">
                  {formatDateTime(src.last_retrieval_at)}
                </div>
              </div>
            </div>

            {/* Base Endpoint URL */}
            <div className="p-3 bg-slate-950 rounded-lg border border-slate-800/80 flex items-center justify-between text-xs">
              <div className="flex items-center gap-2 text-slate-300 truncate">
                <Server className="w-4 h-4 text-slate-500 shrink-0" />
                <span className="text-slate-400 font-mono text-[11px]">Base Endpoint:</span>
                <span className="font-mono text-slate-200 truncate">{src.base_url}</span>
              </div>
              {src.base_url.startsWith("http") && (
                <a
                  href={src.base_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sky-400 hover:text-sky-300 inline-flex items-center gap-1 font-medium transition-colors shrink-0 ml-2"
                >
                  <span>Doc</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              )}
            </div>

            {/* Statutory Licensing & Limitations Notice */}
            <div className="p-3 rounded-lg bg-slate-950/40 border border-slate-800 space-y-1.5 text-xs">
              <div className="flex items-center gap-1.5 text-slate-300 font-medium">
                <Lock className="w-3.5 h-3.5 text-sky-400" />
                <span>Statutory Licensing & Known Limitations:</span>
              </div>
              <p className="text-[11px] text-slate-400 leading-relaxed">
                <strong className="text-slate-300">Licensing:</strong> {src.licensing}
              </p>
              <p className="text-[11px] text-slate-400 leading-relaxed">
                <strong className="text-slate-300">Limitations:</strong> {src.limitations}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
