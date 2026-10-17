import React from "react";
import { CompanyFact } from "../../types";
import { formatDate, formatDateTime } from "../../lib/utils";
import {
  X,
  ExternalLink,
  ShieldCheck,
  AlertTriangle,
  Info,
  Clock,
  Database,
  Hash,
} from "lucide-react";

interface EvidenceModalProps {
  fact: CompanyFact | null;
  isOpen: boolean;
  onClose: () => void;
}

export const EvidenceModal: React.FC<EvidenceModalProps> = ({
  fact,
  isOpen,
  onClose,
}) => {
  if (!isOpen || !fact) return null;

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "verified":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <ShieldCheck className="w-3.5 h-3.5" /> Verified Authoritative Fact
          </span>
        );
      case "derived":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-sky-500/10 text-sky-400 border border-sky-500/20">
            <Info className="w-3.5 h-3.5" /> Derived Calculation
          </span>
        );
      case "conflicting":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-red-500/10 text-red-400 border border-red-500/20">
            <AlertTriangle className="w-3.5 h-3.5" /> Conflicting Evidence
          </span>
        );
      case "stale":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <Clock className="w-3.5 h-3.5" /> Stale / Outdated
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-slate-500/10 text-slate-400 border border-slate-500/20">
            <Info className="w-3.5 h-3.5" /> {status}
          </span>
        );
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-fade-in">
      <div className="w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900/80">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-sky-500/10 border border-sky-500/20 text-sky-400">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-semibold text-slate-100">
                Source Evidence & Provenance
              </h3>
              <p className="text-xs text-slate-400">
                Audit trail for field:{" "}
                <span className="font-mono text-sky-300">{fact.field_name}</span>
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-5 text-sm">
          {/* Status & Confidence row */}
          <div className="flex items-center justify-between p-3.5 rounded-lg bg-slate-950/60 border border-slate-800/80">
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-400 font-medium">Verification:</span>
              {getStatusBadge(fact.verification_status)}
            </div>
            <div className="flex items-center gap-2 text-xs">
              <span className="text-slate-400 font-medium">Confidence Score:</span>
              <span className="font-mono font-semibold text-slate-200">
                {(fact.confidence * 100).toFixed(0)}%
              </span>
              <span className="text-[11px] text-slate-500">
                ({fact.extraction_method.replace("_", " ")})
              </span>
            </div>
          </div>

          {/* Current Extracted Value */}
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1.5">
              Extracted Value
            </label>
            <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg text-slate-100 font-mono text-xs overflow-x-auto whitespace-pre-wrap">
              {typeof fact.value === "object"
                ? JSON.stringify(fact.value, null, 2)
                : String(fact.value)}
            </div>
          </div>

          {/* Supporting Raw Evidence Excerpt */}
          {fact.evidence_excerpt && (
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1.5">
                Supporting Evidence Excerpt
              </label>
              <div className="p-3 bg-slate-950/80 border-l-2 border-sky-500 rounded-r-lg text-slate-200 text-xs italic leading-relaxed">
                "{fact.evidence_excerpt}"
              </div>
            </div>
          )}

          {/* Source and Provenance Details */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-3 rounded-lg bg-slate-950/40 border border-slate-800">
              <div className="text-xs text-slate-400 mb-1">Source Name</div>
              <div className="font-medium text-slate-200 text-xs flex items-center gap-1.5">
                <Database className="w-3.5 h-3.5 text-sky-400" />
                {fact.source_name}
              </div>
            </div>
            <div className="p-3 rounded-lg bg-slate-950/40 border border-slate-800">
              <div className="text-xs text-slate-400 mb-1">Retrieved Timestamp</div>
              <div className="font-medium text-slate-200 text-xs flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-slate-400" />
                {formatDateTime(fact.retrieved_at)}
              </div>
            </div>
          </div>

          {/* Source URL with external security link */}
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1.5">
              Authoritative Source URL
            </label>
            <div className="flex items-center justify-between p-3 bg-slate-950/40 border border-slate-800 rounded-lg">
              <span className="font-mono text-xs text-slate-300 truncate max-w-[420px]">
                {fact.source_url}
              </span>
              <a
                href={fact.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-sky-500/10 text-sky-400 hover:bg-sky-500/20 border border-sky-500/30 transition-colors shrink-0"
              >
                <span>Visit Source</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            </div>
          </div>

          {/* Fact ID & Hash Audit info */}
          <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500">
            <span className="flex items-center gap-1">
              <Hash className="w-3 h-3" /> Fact ID: {fact.fact_id}
            </span>
            <span>Zero-Cost Deterministic Retrieval</span>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3.5 bg-slate-950/80 border-t border-slate-800 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-medium text-slate-300 hover:text-slate-100 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
          >
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
};
