import React, { useState } from "react";
import { validateNorwegianOrg } from "../../lib/utils";
import { companyService } from "../../services/companyService";
import {
  X,
  Building2,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  Loader2,
} from "lucide-react";

interface AddCompanyDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onCompanyAdded: (orgNumber: string) => void;
}

export const AddCompanyDialog: React.FC<AddCompanyDialogProps> = ({
  isOpen,
  onClose,
  onCompanyAdded,
}) => {
  const [orgNumber, setOrgNumber] = useState("");
  const [label, setLabel] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const rawClean = orgNumber.replace(/[^\d]/g, "").trim();
  const validation = rawClean.length > 0 ? validateNorwegianOrg(orgNumber) : null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const val = validateNorwegianOrg(orgNumber);
    if (!val.isValid) {
      setError(val.error || "Please enter a valid 9-digit Norwegian organization number.");
      return;
    }

    setIsSubmitting(true);
    try {
      const res = await companyService.addCompany(rawClean, label.trim() || undefined);
      if (!res.success) {
        setError(res.error || "Failed to add company.");
        setIsSubmitting(false);
        return;
      }

      setIsSubmitting(false);
      onCompanyAdded(rawClean);
      setOrgNumber("");
      setLabel("");
      onClose();
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred.");
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-fade-in">
      <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900/90">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-sky-500/10 border border-sky-500/20 text-sky-400">
              <Building2 className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-semibold text-slate-100">
                Register Norwegian Company
              </h3>
              <p className="text-xs text-slate-400">
                Initiate automated registry & evidence intake
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

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-xs flex items-start gap-2.5">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {/* Org Number Input */}
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">
              Organization Number (organisasjonsnummer) *
            </label>
            <div className="relative">
              <input
                type="text"
                value={orgNumber}
                onChange={(e) => {
                  setOrgNumber(e.target.value);
                  setError(null);
                }}
                placeholder="e.g. 923609016 or 984 851 006"
                maxLength={13}
                autoFocus
                className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-700 rounded-lg text-slate-100 text-sm font-mono placeholder:text-slate-500 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500 transition-colors"
              />
              {validation && (
                <div className="absolute right-3 top-3">
                  {validation.isValid ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  ) : (
                    <AlertCircle className="w-4 h-4 text-amber-400" />
                  )}
                </div>
              )}
            </div>

            {/* Validation Feedback */}
            <div className="mt-1.5 text-[11px] text-slate-400 flex items-center justify-between">
              {validation?.isValid ? (
                <span className="text-emerald-400 flex items-center gap-1">
                  ✓ Valid Modulo 11 check digit ({rawClean})
                </span>
              ) : rawClean.length > 0 ? (
                <span className="text-amber-400">{validation?.error}</span>
              ) : (
                <span>Must be exactly 9 numeric digits</span>
              )}
              <span className="text-slate-500">{rawClean.length}/9 digits</span>
            </div>
          </div>

          {/* Optional Label / Nickname */}
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">
              Internal Label or Company Name (Optional)
            </label>
            <input
              type="text"
              value={label}
              onChange={(e) => setLabel(e.target.value)}
              placeholder="e.g. Equinor Exploration AS"
              className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-700 rounded-lg text-slate-100 text-sm placeholder:text-slate-500 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500 transition-colors"
            />
            <p className="mt-1 text-[11px] text-slate-500">
              Used as a fallback tag until official name is verified from Enhetsregisteret.
            </p>
          </div>

          {/* Notice Box */}
          <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800 text-[11px] text-slate-400 flex items-start gap-2 leading-relaxed">
            <HelpCircle className="w-3.5 h-3.5 text-sky-400 shrink-0 mt-0.5" />
            <span>
              Format validation verifies the mathematical Modulo 11 checksum, but does not confirm entity existence until queried against the Brønnøysund registry.
            </span>
          </div>

          {/* Buttons */}
          <div className="pt-2 flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-medium text-slate-300 hover:text-slate-100 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !validation?.isValid}
              className="inline-flex items-center gap-2 px-4 py-2 text-xs font-semibold text-white bg-sky-600 hover:bg-sky-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg shadow-sm transition-colors"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Processing...</span>
                </>
              ) : (
                <span>Register Company</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
