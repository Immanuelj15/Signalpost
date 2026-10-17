import React from "react";
import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Building,
  Activity,
  History,
  Database,
  Settings,
  Radio,
  Zap,
} from "lucide-react";
import { cn } from "../../lib/utils";

interface SidebarProps {
  className?: string;
  onNavigate?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ className, onNavigate }) => {
  const navItems = [
    {
      label: "Overview",
      to: "/",
      icon: LayoutDashboard,
    },
    {
      label: "Company Explorer",
      to: "/companies",
      icon: Building,
    },
    {
      label: "Research Operations",
      to: "/research",
      icon: Activity,
    },
    {
      label: "Changes & Monitoring",
      to: "/changes",
      icon: History,
    },
    {
      label: "Sources & Evidence",
      to: "/sources",
      icon: Database,
    },
    {
      label: "Settings",
      to: "/settings",
      icon: Settings,
    },
  ];

  return (
    <aside
      className={cn(
        "w-64 bg-slate-950/95 border-r border-slate-800/80 flex flex-col h-screen select-none",
        className
      )}
    >
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800/80 flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-sky-500 to-blue-600 flex items-center justify-center text-white shadow-lg shadow-sky-500/20 ring-1 ring-sky-400/30">
          <Radio className="w-5 h-5 text-white animate-pulse" />
        </div>
        <div>
          <div className="flex items-center gap-1.5">
            <span className="font-bold tracking-wider text-sm text-slate-100 font-mono">
              SIGNALPOST
            </span>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-sky-500/10 text-sky-400 border border-sky-500/20 font-mono font-semibold">
              AI
            </span>
          </div>
          <p className="text-[11px] text-slate-400 font-medium">
            Norwegian Intelligence
          </p>
        </div>
      </div>

      {/* Main Nav Items */}
      <div className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <div className="px-3 pb-2 text-[10px] font-semibold tracking-wider text-slate-500 uppercase">
          Intelligence Workspace
        </div>
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            onClick={onNavigate}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-xs font-medium transition-all group",
                isActive
                  ? "bg-sky-500/10 text-sky-400 border border-sky-500/20 font-semibold"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent"
              )
            }
          >
            {({ isActive }) => (
              <>
                <item.icon
                  className={cn(
                    "w-4 h-4 transition-colors",
                    isActive
                      ? "text-sky-400"
                      : "text-slate-400 group-hover:text-slate-200"
                  )}
                />
                <span>{item.label}</span>
              </>
            )}
          </NavLink>
        ))}
      </div>

      {/* Bottom Quota & Zero-Cost Status Card */}
      <div className="p-3 border-t border-slate-800/80 space-y-3">
        {/* Outbound Quota Tracker */}
        <div className="p-3 rounded-lg bg-slate-900/90 border border-slate-800">
          <div className="flex items-center justify-between text-xs mb-1.5">
            <span className="text-slate-400 flex items-center gap-1.5">
              <Zap className="w-3.5 h-3.5 text-sky-400" />
              Request Budget
            </span>
            <span className="font-mono text-slate-200 font-medium text-[11px]">
              12 / 2,000
            </span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div
              className="bg-sky-500 h-1.5 rounded-full"
              style={{ width: "0.6%" }}
            />
          </div>
          <div className="mt-2 flex items-center justify-between text-[11px]">
            <span className="text-slate-500">External API Cost:</span>
            <span className="text-emerald-400 font-mono font-semibold">
              $0.00 (₹0)
            </span>
          </div>
        </div>

        {/* Brønnøysund & NLOD Attribution */}
        <div className="px-2 text-[10px] text-slate-500 text-center leading-relaxed">
          Statutory Registry Sources via NLOD / CC0 Open Data
        </div>
      </div>
    </aside>
  );
};
