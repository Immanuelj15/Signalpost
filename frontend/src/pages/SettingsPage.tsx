import React, { useState } from "react";
import { isDemoMode } from "../services/apiClient";
import {
  Settings,
  Shield,
  Zap,
  Server,
  Lock,
  Download,
  Database,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
} from "lucide-react";

export const SettingsPage: React.FC = () => {
  const [apiBaseUrl, setApiBaseUrl] = useState(
    import.meta.env.VITE_API_BASE_URL || ""
  );
  const [concurrency, setConcurrency] = useState(3);
  const [requestBudget, setRequestBudget] = useState(2000);
  const [timeoutMinutes, setTimeoutMinutes] = useState(45);
  const [maskApiKey, setMaskApiKey] = useState("••••••••••••••••••••••••••");
  const [savedFeedback, setSavedFeedback] = useState<string | null>(null);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSavedFeedback(
      "Configuration settings saved to local runtime memory. Note: Backend API credentials are handled exclusively server-side via .env for security."
    );
    setTimeout(() => setSavedFeedback(null), 4000);
  };

  const isDemo = isDemoMode();

  return (
    <div className="space-y-6 animate-fade-in max-w-4xl pb-16">
      {/* Header */}
      <div className="border-b border-slate-800/80 pb-5">
        <h1 className="text-2xl font-bold text-slate-100 tracking-tight">
          System & Workspace Settings
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Configure research budgets, statutory API timeouts, backend endpoints, and audit rules.
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {savedFeedback && (
          <div className="p-3.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            <span>{savedFeedback}</span>
          </div>
        )}

        {/* Section 1: Backend Integration Status */}
        <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-4">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-sky-500/10 text-sky-400">
              <Server className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-100">
                Backend API Connection
              </h3>
              <p className="text-xs text-slate-400">
                Configure connection to the Signalpost Python FastAPI research engine
              </p>
            </div>
          </div>

          <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between text-xs">
            <div>
              <span className="text-slate-400">Connection Mode: </span>
              {isDemo ? (
                <span className="font-semibold text-amber-400 font-mono">
                  Autonomous Demo Mode (Local Zero-Cost Mock Engine)
                </span>
              ) : (
                <span className="font-semibold text-emerald-400 font-mono">
                  Live FastAPI Client Active
                </span>
              )}
            </div>
            <span className="text-[11px] font-mono text-slate-500">
              VITE_API_BASE_URL: {apiBaseUrl || "not set (demo fallback)"}
            </span>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">
              API Base URL
            </label>
            <input
              type="text"
              value={apiBaseUrl}
              onChange={(e) => setApiBaseUrl(e.target.value)}
              placeholder="e.g. http://localhost:8000"
              className="w-full px-3.5 py-2 bg-slate-950 border border-slate-700/80 rounded-lg text-xs text-slate-100 font-mono placeholder:text-slate-500 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
            />
            <p className="mt-1 text-[11px] text-slate-500">
              Leave blank to run with built-in zero-cost demo data and Modulo 11 validation.
            </p>
          </div>
        </div>

        {/* Section 2: Research Limits & Budget */}
        <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-4">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-sky-500/10 text-sky-400">
              <Zap className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-100">
                Execution Limits & Budget Guards
              </h3>
              <p className="text-xs text-slate-400">
                Enforce evaluation rules: Maximum 2,000 outbound requests and 45-minute timeout
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Maximum Outbound Requests
              </label>
              <input
                type="number"
                value={requestBudget}
                onChange={(e) => setRequestBudget(Number(e.target.value))}
                min={100}
                max={5000}
                className="w-full px-3.5 py-2 bg-slate-950 border border-slate-700/80 rounded-lg text-xs text-slate-100 font-mono"
              />
              <p className="mt-1 text-[11px] text-slate-500">
                Default: 2,000 statutory calls
              </p>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Batch Concurrency
              </label>
              <input
                type="number"
                value={concurrency}
                onChange={(e) => setConcurrency(Number(e.target.value))}
                min={1}
                max={10}
                className="w-full px-3.5 py-2 bg-slate-950 border border-slate-700/80 rounded-lg text-xs text-slate-100 font-mono"
              />
              <p className="mt-1 text-[11px] text-slate-500">
                Default: 3 concurrent workers
              </p>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Execution Timeout (Minutes)
              </label>
              <input
                type="number"
                value={timeoutMinutes}
                onChange={(e) => setTimeoutMinutes(Number(e.target.value))}
                min={5}
                max={120}
                className="w-full px-3.5 py-2 bg-slate-950 border border-slate-700/80 rounded-lg text-xs text-slate-100 font-mono"
              />
              <p className="mt-1 text-[11px] text-slate-500">
                Default: 45 minutes hard limit
              </p>
            </div>
          </div>
        </div>

        {/* Section 3: AI Model & Security Guardrails */}
        <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-4">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <Shield className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-100">
                AI Model & Security Credentials
              </h3>
              <p className="text-xs text-slate-400">
                Zero-Cost statutory extraction operates deterministically without paid LLM API keys
              </p>
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">
              LLM Provider API Key (Optional)
            </label>
            <div className="relative">
              <input
                type="password"
                value={maskApiKey}
                disabled
                className="w-full px-3.5 py-2 bg-slate-950 border border-slate-700/80 rounded-lg text-xs text-slate-400 font-mono cursor-not-allowed opacity-60"
              />
              <Lock className="w-4 h-4 text-slate-500 absolute right-3 top-2.5" />
            </div>
            <p className="mt-1 text-[11px] text-slate-500">
              API credentials are never exposed in browser code or stored in localStorage. Configure in backend <code className="text-sky-300 font-mono">.env</code>.
            </p>
          </div>
        </div>

        {/* Section 4: About & System Info */}
        <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between text-xs">
          <div>
            <div className="font-semibold text-slate-200">
              Signalpost AI Intelligence Platform v1.0.0
            </div>
            <div className="text-slate-500 text-[11px] mt-0.5">
              Developed for the Builderr.ai Signalpost Norwegian Company Research Challenge
            </div>
          </div>
          <span className="font-mono text-emerald-400 font-semibold bg-emerald-500/10 px-2.5 py-1 rounded border border-emerald-500/20 text-xs">
            Production Build
          </span>
        </div>

        {/* Submit */}
        <div className="flex justify-end pt-2">
          <button
            type="submit"
            className="px-5 py-2 text-xs font-semibold text-white bg-sky-600 hover:bg-sky-500 rounded-lg shadow-sm transition-colors"
          >
            Save Preferences
          </button>
        </div>
      </form>
    </div>
  );
};
