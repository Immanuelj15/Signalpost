import React, { useState, createContext, useContext } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";
import { AddCompanyDialog } from "../dialogs/AddCompanyDialog";
import { ImportBatchDialog } from "../dialogs/ImportBatchDialog";
import { EvidenceModal } from "../dialogs/EvidenceModal";
import { CompanyFact } from "../../types";

interface ShellContextType {
  openAddCompany: () => void;
  openImportBatch: () => void;
  openEvidence: (fact: CompanyFact) => void;
}

const ShellContext = createContext<ShellContextType>({
  openAddCompany: () => {},
  openImportBatch: () => {},
  openEvidence: () => {},
});

export const useShell = () => useContext(ShellContext);

export const AppShell: React.FC = () => {
  const [isAddCompanyOpen, setIsAddCompanyOpen] = useState(false);
  const [isImportBatchOpen, setIsImportBatchOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [selectedFact, setSelectedFact] = useState<CompanyFact | null>(null);
  const navigate = useNavigate();

  const handleCompanyAdded = (orgNumber: string) => {
    navigate(`/companies/${orgNumber}`);
  };

  const handleBatchImported = (count: number) => {
    navigate("/companies");
  };

  return (
    <ShellContext.Provider
      value={{
        openAddCompany: () => setIsAddCompanyOpen(true),
        openImportBatch: () => setIsImportBatchOpen(true),
        openEvidence: (fact: CompanyFact) => setSelectedFact(fact),
      }}
    >
      <div className="flex h-screen bg-[#090D16] text-slate-100 overflow-hidden font-sans antialiased">
        {/* Desktop Sidebar */}
        <Sidebar className="hidden md:flex shrink-0" />

        {/* Mobile Navigation Drawer Overlay */}
        {mobileMenuOpen && (
          <div className="fixed inset-0 z-50 flex md:hidden">
            <div
              className="fixed inset-0 bg-black/75 backdrop-blur-sm"
              onClick={() => setMobileMenuOpen(false)}
            />
            <div className="relative z-10 w-72 h-full bg-slate-950 flex flex-col shadow-2xl animate-slide-in">
              <Sidebar onNavigate={() => setMobileMenuOpen(false)} />
            </div>
          </div>
        )}

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
          <Topbar
            onOpenAddCompany={() => setIsAddCompanyOpen(true)}
            onOpenImportBatch={() => setIsImportBatchOpen(true)}
            onToggleMobileMenu={() => setMobileMenuOpen(!mobileMenuOpen)}
          />

          {/* Dynamic Scrollable Page Outlet */}
          <main className="flex-1 overflow-y-auto px-4 md:px-8 py-6 max-w-7xl w-full mx-auto">
            <Outlet />
          </main>
        </div>

        {/* Modals */}
        <AddCompanyDialog
          isOpen={isAddCompanyOpen}
          onClose={() => setIsAddCompanyOpen(false)}
          onCompanyAdded={handleCompanyAdded}
        />

        <ImportBatchDialog
          isOpen={isImportBatchOpen}
          onClose={() => setIsImportBatchOpen(false)}
          onBatchImported={handleBatchImported}
        />

        <EvidenceModal
          isOpen={!!selectedFact}
          fact={selectedFact}
          onClose={() => setSelectedFact(null)}
        />
      </div>
    </ShellContext.Provider>
  );
};
