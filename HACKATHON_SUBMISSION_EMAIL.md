# Hackathon Submission Email: Signalpost

**To:** submit@builderr.ai  
**Subject:** Signalpost Hackathon Submission – Company Research Agent  
**Participant Name:** Immanuel A  
**Date:** October 17, 2026  

---

Dear Builderr.ai Hackathon Evaluation Team,

I am pleased to submit my entry for the **Signalpost: Build An Agent That Finds Company Information** hackathon. 

Below is the comprehensive submission dossier for **Signalpost — Evidence-First Norwegian Company Intelligence Agent & Intelligence Dashboard**, including the verified GitHub repository, commit hash, exact reproduction commands, architectural breakdown, and evaluation benchmark results.

---

### 1. Project Overview & Problem Solved

**Project Title:** Signalpost — Evidence-First Norwegian Company Intelligence Agent  
**Core Principle:** *Every fact should have provenance. Every change should have evidence. Every unknown should remain unknown.*

Traditional web research agents and LLM scrapers suffer from hallucinations, unverifiable claims, silent data staleness, and uncontrollable API costs. In high-stakes financial, compliance, and corporate research, an unverified assertion is worse than an explicit unknown.

**Signalpost** solves this challenge by implementing an autonomous, deterministic, evidence-grounded research pipeline paired with a modern dark-first React intelligence dashboard:
- Resolves and verifies Norwegian organization numbers via strict **Modulo 11 check digit verification**.
- Queries authoritative statutory public registers (**Brønnøysund Enhetsregisteret** and **Regnskapsregisteret**) alongside SSRF-guarded corporate website analysis.
- Attaches an immutable cryptographic audit trail (source URL, retrieval timestamp, extraction method, and supporting excerpt) to every single fact.
- Computes deterministic SHA-256 snapshot hashes to detect genuine corporate changes across time with zero false positives on unchanged records.
- Operates at **100% ₹0 ($0.00) external API cost** by default.

---

### 2. Verified Repository & Commit Information

- **GitHub Repository URL:** https://github.com/Immanuelj15/Signalpost.git
- **Git Commit Hash:** `307d846e32ba313a8ee5fcdd10bc3a46d6fe7ebc`
- **Branch:** `main`

---

### 3. Setup and Execution Instructions

#### A. Backend & CLI Installation (Clean Python 3.10+ Environment)
```bash
# Clone the repository
git clone https://github.com/Immanuelj15/Signalpost.git
cd Signalpost

# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the full test suite (28/28 tests passing)
python -m pytest -v
```

#### B. Running Batch Research via CLI
```bash
# Execute batch research across input organization numbers
python -m signalpost.cli batch --input data/input/companies.csv --output data/output/results.jsonl --concurrency 3

# Inspect a single Norwegian company (e.g., Equinor ASA)
python -m signalpost.cli research 923609016
```

#### C. Running the React Intelligence Dashboard
```bash
cd frontend
npm install
npm run dev
```
Open **`http://localhost:5173`** in your browser to interact with the full dark-first intelligence workspace, Modulo 11 validators, CSV preview importer, evidence inspector, and Recharts financial trends.

---

### 4. AI Models, APIs, and External Services

- **Paid LLMs Used:** **None ($0.00 / ₹0.00)**. The core pipeline relies strictly on deterministic, reproducible parsers and statutory APIs. An optional LLM adapter interface is implemented for future opt-in synthesis (`ENABLE_OPTIONAL_LLM=false` by default).
- **Statutory Data Sources:**
  1. **Brønnøysund Enhetsregisteret:** `https://data.brreg.no/enhetsregisteret/api/enheter/{orgnr}` (Official public register under NLOD / CC0).
  2. **Brønnøysund Regnskapsregisteret:** `https://data.brreg.no/regnskapsregisteret/regnskap/{orgnr}` (Statutory annual accounts).
  3. **Verified Corporate Websites:** SSRF-guarded HTTP client blocking private IP ranges (RFC 1918) with strict timeouts and response limits.
- **External API Costs:** **$0.00 (₹0.00)**. All statutory registers are accessed via free public government endpoints.

---

### 5. Verified Profile Capacity & Scalability

- **Profile Capacity:** **1,000+ distinct company profiles supported and verified**.
- **Benchmark Results (`docs/evaluation.md`):**
  - **1,000 distinct profiles** ingested and indexed in SQLite (WAL mode).
  - **Total Ingestion Time:** 67.34 seconds (14.8 profiles/second).
  - **Average Latency:** 67.34 ms per profile.
  - **Database Footprint:** 6.34 MB total (~6.50 KB per complete profile).
  - **1-Per-Input Invariant:** Exactly 1 terminal structured result generated per input organization number.

---

### 6. Architectural Guarantees & Hackathon Criteria

| Requirement | Implementation Summary |
|---|---|
| **Identity Matching** | Validates Norwegian 9-digit format using Modulo 11 arithmetic (`[3, 2, 7, 6, 5, 4, 3, 2]`). Enforces organization number as immutable primary key; never conflates distinct legal entities sharing similar trade names. |
| **Reliable Retrieval** | Multi-tier adapter architecture: primary statutory registry -> financial statement registry -> verified corporate domain. Non-commercial entities exempt from financial filing are explicitly categorized rather than marked as broken. |
| **Evidence & Citations** | Every fact row contains `source_name`, authoritative `source_url`, `retrieved_at` timestamp, and `evidence_excerpt` containing the exact raw excerpt. |
| **Information Freshness** | All extractions preserve ISO 8601 UTC retrieval timestamps. Stored snapshots maintain point-in-time state. |
| **Change Detection** | Computes SHA-256 hashes of normalized profile snapshots. Repeated executions on unchanged data yield **0 false changes** (100% idempotent). Temporary upstream outages never cause existing facts to be deleted. |
| **Hallucination Prevention** | Strictly closed-world: fields without authoritative documentary proof are recorded as `unavailable` in the `missing_fields` ledger. No placeholder or synthetic claims are ever attributed to live entities. |
| **Budget Enforcement** | Central `RequestBudgetManager` enforces the 2,000-request limit and 45-minute timeout window with thread-safe counters. |

---

### 7. Testing & Quality Assurance Summary

- **Unit Test Suite:** 28 passing tests across identity resolution, validation, snapshot hashing, change detection, budget tracking, SSRF guardrails, and batch invariants (`tests/`).
- **Live Smoke Test:** Verified against live Brønnøysund production endpoints (`scripts/smoke_test.py`).
- **Frontend Build Status:** Vite production bundle passes with zero TypeScript errors (`npm run build`).

---

Thank you for organizing the Signalpost challenge and for the opportunity to demonstrate an evidence-first approach to autonomous company intelligence. I look forward to your review and feedback.

Sincerely,  
**Immanuel A**  
*Signalpost Project Author*  
GitHub: [https://github.com/Immanuelj15](https://github.com/Immanuelj15)  
Repository: [https://github.com/Immanuelj15/Signalpost.git](https://github.com/Immanuelj15/Signalpost.git)
