import React, { useState, useRef } from "react";
import { validateNorwegianOrg } from "../../lib/utils";
import { companyService } from "../../services/companyService";
import {
  X,
  UploadCloud,
  FileSpreadsheet,
  CheckCircle2,
  AlertTriangle,
  Loader2,
  Info,
  Download,
} from "lucide-react";

interface ImportBatchDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onBatchImported: (count: number) => void;
}

interface ParsedRow {
  rawOrg: string;
  cleanedOrg: string;
  label?: string;
  isValid: boolean;
  error?: string;
  isDuplicate?: boolean;
}

export const ImportBatchDialog: React.FC<ImportBatchDialogProps> = ({
  isOpen,
  onClose,
  onBatchImported,
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [parsedRows, setParsedRows] = useState<ParsedRow[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isImporting, setIsImporting] = useState(false);
  const [importResult, setImportResult] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) {
      processCsvFile(selected);
    }
  };

  const processCsvFile = (selectedFile: File) => {
    setFile(selectedFile);
    setIsProcessing(true);
    setImportResult(null);

    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result as string;
      const lines = text.split(/\r?\n/).filter((l) => l.trim().length > 0);

      if (lines.length === 0) {
        setParsedRows([]);
        setIsProcessing(false);
        return;
      }

      // Check if line 0 is a header
      const firstLineLower = lines[0].toLowerCase();
      const hasHeader =
        firstLineLower.includes("org") ||
        firstLineLower.includes("number") ||
        firstLineLower.includes("organisasjonsnummer");

      const dataLines = hasHeader ? lines.slice(1) : lines;
      const seenOrgs = new Set<string>();
      const results: ParsedRow[] = [];

      for (const line of dataLines) {
        // Support comma or semicolon separation
        const parts = line.split(/[,;\t]/).map((p) => p.trim().replace(/^["']|["']$/g, ""));
        const rawOrg = parts[0] || "";
        const label = parts[1] || undefined;
        const cleaned = rawOrg.replace(/[^\d]/g, "");

        if (!rawOrg) continue;

        const val = validateNorwegianOrg(rawOrg);
        const isDuplicate = seenOrgs.has(cleaned);
        if (cleaned) seenOrgs.add(cleaned);

        results.push({
          rawOrg,
          cleanedOrg: cleaned,
          label,
          isValid: val.isValid && !isDuplicate,
          error: isDuplicate ? "Duplicate in current file" : val.error,
          isDuplicate,
        });
      }

      setParsedRows(results);
      setIsProcessing(false);
    };

    reader.readAsText(selectedFile);
  };

  const validRows = parsedRows.filter((r) => r.isValid);
  const invalidRows = parsedRows.filter((r) => !r.isValid);

  const handleImport = async () => {
    if (validRows.length === 0) return;
    setIsImporting(true);

    try {
      const payload = validRows.map((r) => ({
        organization_number: r.cleanedOrg,
        label: r.label,
      }));

      const res = await companyService.importBatch(payload);
      setIsImporting(false);
      setImportResult(
        `Successfully imported ${res.validCount} companies (${res.invalidCount} failed, ${res.duplicateCount} duplicates skipped).`
      );
      onBatchImported(res.validCount);

      setTimeout(() => {
        onClose();
        setFile(null);
        setParsedRows([]);
        setImportResult(null);
      }, 1500);
    } catch (err: any) {
      setIsImporting(false);
      setImportResult(`Error: ${err.message || "Failed to process batch."}`);
    }
  };

  const downloadSampleCsv = () => {
    const sample = `organization_number,label
923609016,EQUINOR ASA
984851006,DNB BANK ASA
915000578,POSTEN BRING AS
998848316,TELENOR ASA
986228608,YARA INTERNATIONAL ASA`;
    const blob = new Blob([sample], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "sample_norwegian_companies.csv";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-fade-in">
      <div className="w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900/90">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-sky-500/10 border border-sky-500/20 text-sky-400">
              <UploadCloud className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-semibold text-slate-100">
                Batch Company Import (CSV)
              </h3>
              <p className="text-xs text-slate-400">
                Upload a structured file containing Norwegian organization numbers
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
          {/* Dropzone */}
          <div
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-slate-700 hover:border-sky-500 rounded-xl p-6 text-center cursor-pointer transition-colors bg-slate-950/40 hover:bg-slate-950/80"
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept=".csv,.txt"
              className="hidden"
            />
            <FileSpreadsheet className="w-10 h-10 text-sky-400 mx-auto mb-2" />
            <div className="text-sm font-medium text-slate-200">
              {file ? file.name : "Click or drag CSV file to upload"}
            </div>
            <div className="text-xs text-slate-400 mt-1">
              Supports CSV with <code className="text-sky-300">organization_number</code> and optional <code className="text-sky-300">label</code>
            </div>
          </div>

          <div className="flex items-center justify-between text-xs">
            <button
              onClick={downloadSampleCsv}
              type="button"
              className="text-sky-400 hover:text-sky-300 inline-flex items-center gap-1.5 font-medium transition-colors"
            >
              <Download className="w-3.5 h-3.5" /> Download Sample CSV Template
            </button>
            <span className="text-slate-500">Strict Modulo 11 check digit verification applied</span>
          </div>

          {/* Parsing status / summary stats */}
          {parsedRows.length > 0 && (
            <div className="grid grid-cols-3 gap-3">
              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-center">
                <div className="text-xs text-slate-400">Total Rows</div>
                <div className="text-lg font-bold text-slate-100 font-mono">
                  {parsedRows.length}
                </div>
              </div>
              <div className="p-3 rounded-lg bg-emerald-500/5 border border-emerald-500/20 text-center">
                <div className="text-xs text-emerald-400">Valid Rows</div>
                <div className="text-lg font-bold text-emerald-400 font-mono">
                  {validRows.length}
                </div>
              </div>
              <div className="p-3 rounded-lg bg-red-500/5 border border-red-500/20 text-center">
                <div className="text-xs text-red-400">Invalid / Duplicates</div>
                <div className="text-lg font-bold text-red-400 font-mono">
                  {invalidRows.length}
                </div>
              </div>
            </div>
          )}

          {/* Preview Table */}
          {parsedRows.length > 0 && (
            <div className="border border-slate-800 rounded-lg overflow-hidden">
              <div className="px-3 py-2 bg-slate-950 text-xs font-medium text-slate-400 border-b border-slate-800 flex justify-between items-center">
                <span>Row Validation Preview</span>
                <span>Showing first {Math.min(parsedRows.length, 6)} rows</span>
              </div>
              <div className="max-h-48 overflow-y-auto divide-y divide-slate-800/80 font-mono text-xs">
                {parsedRows.slice(0, 8).map((row, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-2.5 hover:bg-slate-900/60 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      {row.isValid ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                      ) : (
                        <AlertTriangle className="w-4 h-4 text-red-400 shrink-0" />
                      )}
                      <span className="text-slate-200">{row.rawOrg}</span>
                      {row.label && (
                        <span className="text-slate-400 font-sans text-[11px]">
                          ({row.label})
                        </span>
                      )}
                    </div>
                    <div>
                      {row.isValid ? (
                        <span className="text-emerald-400 text-[11px] font-sans">
                          Valid Modulo 11
                        </span>
                      ) : (
                        <span className="text-red-400 text-[11px] font-sans">
                          {row.error}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {importResult && (
            <div className="p-3 rounded-lg bg-sky-500/10 border border-sky-500/20 text-sky-300 text-xs flex items-center gap-2">
              <Info className="w-4 h-4 shrink-0" />
              <span>{importResult}</span>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3.5 bg-slate-950/80 border-t border-slate-800 flex items-center justify-between">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-xs font-medium text-slate-300 hover:text-slate-100 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleImport}
            disabled={validRows.length === 0 || isImporting || isProcessing}
            className="inline-flex items-center gap-2 px-4 py-2 text-xs font-semibold text-white bg-sky-600 hover:bg-sky-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg shadow-sm transition-colors"
          >
            {isImporting ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Importing...</span>
              </>
            ) : (
              <span>Import {validRows.length} Valid Companies</span>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
