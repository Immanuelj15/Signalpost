# Signalpost AI Company Intelligence — Premium React Dashboard

Autonomous Norwegian Company Intelligence Dashboard built with **React 18**, **Vite**, **TypeScript**, **Tailwind CSS**, and **Recharts**.

Designed specifically for the **Builderr.ai Signalpost Challenge**, this application provides a dark-first SaaS research platform for auditing, verifying, and monitoring Norwegian companies with strict evidence provenance and zero required paid API dependencies.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Run the Development Server
```bash
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

### 3. Production Build & Preview
```bash
npm run build
npm run preview
```

---

## 🎨 Visual Design System

- **Palette:** Dark-first SaaS theme. Deep midnight navy background (`#090D16`), slate/charcoal surfaces (`#0F172A`, `#1E293B`), electric blue/cyan accents (`#38BDF8`), emerald indicators (`#10B981`) for verified statutory facts, amber (`#F59E0B`) for deltas, and red (`#EF4444`) for errors.
- **Typography:** Plus Jakarta Sans for UI hierarchy, JetBrains Mono for Norwegian 9-digit organization numbers, financial statement amounts, and hash checksums.
- **Micro-interactions:** Interactive hover states, Recharts responsive visualizations, before-and-after change diffs, and accessible modal overlays.

---

## 📑 Required Pages Implemented

| Route | Page | Purpose & Features |
|---|---|---|
| `/` | **Overview Dashboard** | Workspace KPIs, weekly fact throughput Area chart, recent audit table, change diff feed, statutory source health bars, quick intake action buttons. |
| `/companies` | **Company Explorer** | Searchable & filterable table of Norwegian companies, Modulo 11 check digit verification, status badges, CSV and JSON export, quick re-research triggers. |
| `/companies/:orgNumber` | **Company Profile** | Comprehensive profile header with 5 tabs: **Overview** (statutory details, addresses, NACE industry codes, business activity), **Facts & Evidence** (fact ledger with modal inspector), **Financials** (Recharts revenue/EBIT trends and statutory filing tables), **Activity & Web** (SSRF-guarded web discoveries), and **Audit History** (side-by-side snapshot diffs). |
| `/research` | **Research Operations** | Operational execution log, run status, company throughput, request quota tracker, and execution quality breakdown. |
| `/changes` | **Changes & Monitoring** | Audit feed of verified delta modifications across snapshots with side-by-side before/after value comparisons. |
| `/sources` | **Sources & Provenance** | Authoritative registry status cards (Enhetsregisteret, Regnskapsregisteret, SSRF-guarded web scraper) with latency, NLOD licensing terms, and limitations. |
| `/settings` | **Settings** | Request budget limits (2,000 requests, 45-min timeout), batch concurrency, masked API credentials, and FastAPI backend endpoint configuration. |

---

## 🛡️ Key Features & Architectural Highlights

### 1. Real-time Modulo 11 Check Digit Verification
Norwegian organization numbers are strictly 9 digits with Modulo 11 weights `[3, 2, 7, 6, 5, 4, 3, 2]`. The dialog dynamically validates the checksum on keystroke, providing instant visual feedback.

### 2. Evidence Modal & Provenance Inspector
Every factual claim links directly to its timestamped source:
- Authoritative statutory URL link (e.g. Brønnøysund Enhetsregisteret / Regnskapsregisteret).
- Retrieval timestamp and extraction method (deterministic API vs SSRF-guarded HTML parser).
- Supporting raw evidence excerpt snippet.
- Confidence score and verification status badge.

### 3. Batch CSV Import with Interactive Preview
Upload CSV files containing `organization_number` and optional `label`:
- Validates each row using Modulo 11 checksum.
- Detects duplicate records.
- Previews valid and invalid rows with error explanations before importing.
- Never silently drops invalid entries.

### 4. Dual-Mode Service Architecture
- **Demo Mode (Default):** Runs immediately in zero-cost standalone mode populated with real statutory entities (Equinor ASA, DNB Bank ASA, Posten Bring, Telenor ASA, Yara, Brønnøysundregistrene).
- **Live Backend Mode:** Connects to the Python FastAPI backend by setting `VITE_API_BASE_URL=http://localhost:8000`.

---

## 📦 Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── App.tsx             # Root application provider
│   │   └── router.tsx          # React Router route definitions
│   ├── components/
│   │   ├── layout/
│   │   │   ├── AppShell.tsx    # Responsive shell with sidebar, topbar, modals
│   │   │   ├── Sidebar.tsx     # Navigation & request quota status
│   │   │   └── Topbar.tsx      # Global search & quick action triggers
│   │   └── dialogs/
│   │       ├── AddCompanyDialog.tsx   # Modulo 11 verified company registration
│   │       ├── ImportBatchDialog.tsx  # CSV upload, preview, and validation
│   │       └── EvidenceModal.tsx      # Source provenance inspector
│   ├── pages/
│   │   ├── OverviewPage.tsx        # KPI metrics & Recharts activity
│   │   ├── CompaniesPage.tsx       # Searchable, filterable company catalog
│   │   ├── CompanyProfilePage.tsx  # 5-tab audited profile & financials
│   │   ├── ResearchPage.tsx        # Execution log & research operations
│   │   ├── ChangesPage.tsx         # Side-by-side delta diff viewer
│   │   ├── SourcesPage.tsx         # Statutory registry health & licensing
│   │   └── SettingsPage.tsx        # Budget, timeouts, and backend integration
│   ├── services/
│   │   ├── apiClient.ts            # Centralized API fetcher & demo switcher
│   │   ├── companyService.ts       # Company query & registration contracts
│   │   ├── researchService.ts      # Research execution service
│   │   ├── changesService.ts       # Profile diff service
│   │   └── exportService.ts        # JSON & CSV file download generation
│   ├── mocks/
│   │   ├── demoData.ts             # Source-backed statutory records
│   │   └── demoService.ts          # Stateful mock engine
│   ├── types/
│   │   └── index.ts                # TypeScript domain models
│   ├── lib/
│   │   └── utils.ts                # Modulo 11 validator, date & currency formatters
│   └── styles/
│       └── globals.css             # Tailwind base & dark theme tokens
├── index.html
├── package.json
├── tailwind.config.js
├── tsconfig.app.json
└── vite.config.ts
```
