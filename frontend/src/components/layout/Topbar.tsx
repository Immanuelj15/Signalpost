import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { companyService } from "../../services/companyService";
import { isDemoMode } from "../../services/apiClient";
import { CompanyProfile } from "../../types";
import {
  Search,
  Plus,
  UploadCloud,
  Menu,
  ShieldAlert,
  Building,
  Bell,
  Sparkles,
  ExternalLink,
} from "lucide-react";

interface TopbarProps {
  onOpenAddCompany: () => void;
  onOpenImportBatch: () => void;
  onToggleMobileMenu: () => void;
}

export const Topbar: React.FC<TopbarProps> = ({
  onOpenAddCompany,
  onOpenImportBatch,
  onToggleMobileMenu,
}) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<CompanyProfile[]>([]);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [isDemo] = useState(isDemoMode());
  const searchContainerRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      setIsSearchOpen(false);
      return;
    }

    const timer = setTimeout(async () => {
      const results = await companyService.getCompanies(searchQuery);
      setSearchResults(results.slice(0, 5));
      setIsSearchOpen(true);
    }, 150);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Click outside to close search dropdown
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (
        searchContainerRef.current &&
        !searchContainerRef.current.contains(e.target as Node)
      ) {
        setIsSearchOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSelectCompany = (orgNumber: string) => {
    setIsSearchOpen(false);
    setSearchQuery("");
    navigate(`/companies/${orgNumber}`);
  };

  const handleSearchKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && searchResults.length > 0) {
      handleSelectCompany(searchResults[0].organization_number);
    }
  };

  return (
    <header className="h-16 border-b border-slate-800/80 bg-slate-950/60 backdrop-blur-md sticky top-0 z-30 flex items-center justify-between px-4 md:px-6">
      {/* Left side: Mobile Toggle & Global Search */}
      <div className="flex items-center gap-3 flex-1 max-w-lg">
        <button
          onClick={onToggleMobileMenu}
          className="md:hidden p-2 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition-colors"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Global Search Bar */}
        <div ref={searchContainerRef} className="relative w-full">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onFocus={() => {
                if (searchResults.length > 0) setIsSearchOpen(true);
              }}
              onKeyDown={handleSearchKeyDown}
              placeholder="Search company name or organization number..."
              className="w-full pl-9 pr-4 py-2 bg-slate-900/90 border border-slate-800 hover:border-slate-700 focus:border-sky-500 rounded-lg text-xs text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-1 focus:ring-sky-500 transition-colors"
            />
          </div>

          {/* Autocomplete Dropdown */}
          {isSearchOpen && searchResults.length > 0 && (
            <div className="absolute top-full left-0 right-0 mt-1.5 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl overflow-hidden z-50">
              <div className="px-3 py-1.5 text-[10px] font-semibold text-slate-500 uppercase tracking-wider bg-slate-950/80 border-b border-slate-800">
                Matching Norwegian Companies
              </div>
              <div className="divide-y divide-slate-800/60">
                {searchResults.map((c) => (
                  <div
                    key={c.organization_number}
                    onClick={() => handleSelectCompany(c.organization_number)}
                    className="p-3 hover:bg-slate-800/60 cursor-pointer flex items-center justify-between transition-colors group"
                  >
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-slate-800 group-hover:bg-sky-500/10 text-slate-400 group-hover:text-sky-400 transition-colors">
                        <Building className="w-4 h-4" />
                      </div>
                      <div>
                        <div className="text-xs font-semibold text-slate-200 group-hover:text-sky-300 transition-colors">
                          {c.company.official_name || "Unknown Company"}
                        </div>
                        <div className="text-[11px] text-slate-400 font-mono flex items-center gap-2">
                          <span>Org: {c.organization_number}</span>
                          {c.company.organization_type && (
                            <span className="text-slate-500">
                              • {c.company.organization_type}
                            </span>
                          )}
                          {c.company.business_address?.city && (
                            <span className="text-slate-500">
                              • {c.company.business_address.city}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    <span className="text-[11px] font-medium text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                      {c.facts?.length || 0} facts
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Right side: Demo badge & actions */}
      <div className="flex items-center gap-2.5">
        {/* Transparent Demo Mode Badge */}
        {isDemo && (
          <div
            title="Running in local zero-cost demonstration mode. Real registry contracts are fully compatible via VITE_API_BASE_URL."
            className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-amber-500/10 text-amber-300 border border-amber-500/20 shadow-sm"
          >
            <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
            <span>DEMO MODE</span>
          </div>
        )}

        {/* Import Batch Button */}
        <button
          onClick={onOpenImportBatch}
          className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-300 hover:text-slate-100 bg-slate-900 hover:bg-slate-800 border border-slate-700/80 transition-colors"
        >
          <UploadCloud className="w-3.5 h-3.5 text-sky-400" />
          <span>Import CSV</span>
        </button>

        {/* Add Company Button */}
        <button
          onClick={onOpenAddCompany}
          className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold text-white bg-sky-600 hover:bg-sky-500 border border-sky-500/30 shadow-sm shadow-sky-500/10 transition-colors"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Add Company</span>
        </button>
      </div>
    </header>
  );
};
