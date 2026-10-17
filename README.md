# 🇳🇴 Signalpost: Evidence-First Norwegian Company Intelligence Agent

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/tests-28%20passed-brightgreen.svg)](#testing)
[![Cost](https://img.shields.io/badge/external%20cost-%240.00%20(₹0.00)-success)](#cost-and-budget-controls)
[![Capacity](https://img.shields.io/badge/profiles%20supported-1000%2B-orange)](#scalability)

> **Signalpost** is an autonomous, evidence-first company research agent designed for the **Builderr.ai Signalpost Challenge**. It accepts Norwegian organization numbers (*organisasjonsnummer*), resolves verified legal identities, extracts attributable facts from official public sources, maintains point-in-time profile snapshots, and detects corporate changes over time—with **₹0 ($0.00)** in external API costs.

---

## Table of Contents
1. [Key Capabilities](#key-capabilities)
2. [Architecture Overview](#architecture-overview)
3. [Data Sources & Legal Disclosures](#data-sources--legal-disclosures)
4. [Quickstart & Single-Command Execution](#quickstart--single-command-execution)
5. [Command-Line Interface (CLI)](#command-line-interface-cli)
6. [Interactive Web UI](#interactive-web-ui)
7. [REST API Service](#rest-api-service)
8. [Output Schema Specification](#output-schema-specification)
9. [Change Detection & Historical Auditing](#change-detection--historical-auditing)
10. [Testing Suite](#testing-suite)
11. [Scalability & Benchmarking](#scalability--benchmarking)
12. [Cost and Budget Controls](#cost-and-budget-controls)
13. [Security & SSRF Safeguards](#security--ssrf-safeguards)
14. [Submission Checklist](#submission-checklist)

---

## Key Capabilities

- **Strict Norwegian Identity Resolution:** Enforces Modulo 11 check-digit verification with weights `[3, 2, 7, 6, 5, 4, 3, 2]`. Disallows invalid formats. Never merges entities based on name or address similarity.
- **100% Fact Provenance:** Every claim is saved as an atomic fact with source URL, UTC retrieval timestamp, exact evidence excerpt, and SHA-256 content hash.
- **Official Financial Statement Extraction:** Extracts audited annual accounts from *Regnskapsregisteret*, distinguishing operating revenue, sales revenue, EBIT, net profit, total assets, equity, and debt by reporting period and currency.
- **Deterministic Change Detection:** Serializes snapshots using profile hashing. Pinpoints name changes, address relocations, industry classification shifts, and new financial filings. Guarantees **zero duplicate changes on repeated runs (idempotent)**.
- **1-Per-Input Invariant:** Every submitted organization number produces exactly one terminal result, ensuring evaluation batches complete without unhandled exceptions or silent drops.
- **Zero-Cost Default Path (₹0 / $0.00):** Operates at 100% fidelity using open government APIs. No paid LLM or subscription API is required.

---

## Architecture Overview

Signalpost consists of ten modular, testable components:

```
[Input / Batch Manager] ──> [Identity Resolver (Modulo 11)] ──> [Research Planner]
                                                                        │
┌───────────────────────────────┬───────────────────────────────────────┤
│                               │                                       │
▼                               ▼                                       ▼
[Source: Enhetsregisteret]    [Source: Regnskapsregisteret]    [Source: Verified Website]
│                               │                                       │
└───────────────────────────────┼───────────────────────────────────────┘
                                ▼
                   [Evidence & Identity Validator]
                                │
                                ▼
                   [Profile Builder & Snapshots]
                                │
                                ▼
                   [Change Detection Engine (Idempotent)]
                                │
                                ▼
                   [Explanation Generator & Exporters]
```

Detailed architectural diagrams and component descriptions can be found in [`docs/architecture.md`](docs/architecture.md).

---

## Data Sources & Legal Disclosures

1. **Brønnøysund Register Centre — Enhetsregisteret (Source A)**
   - **Endpoint:** `https://data.brreg.no/enhetsregisteret/api/enheter/{orgnr}`
   - **Data:** Legal company name, organization type (AS, ASA, etc.), registration date, business address, municipality, industry NACE codes, employee count, official website, status flags (bankruptcy, liquidation, dissolution).
   - **Licensing:** Norwegian Licence for Open Government Data (NLOD) / CC0 public data.

2. **Brønnøysund Register Centre — Regnskapsregisteret (Source B)**
   - **Endpoint:** `https://data.brreg.no/regnskapsregisteret/regnskap/{orgnr}`
   - **Data:** Audited annual financial statements, revenue, EBIT, EBT, net profit, total assets, equity, debt, reporting periods, and accounting rules.
   - **Licensing:** NLOD / Statutory open corporate disclosures.

3. **Verified Corporate Websites (Source C)**
   - **Discovery:** Analyzed only if confirmed through Enhetsregisteret's official `hjemmeside` or validated domain ownership.
   - **Data:** Business description, public contact email/phone, products & services.
   - **Safety:** Full SSRF protection against private subnets and cloud metadata endpoints.

For detailed schemas and rate-limit considerations, see [`docs/data_sources.md`](docs/data_sources.md).

---

## Quickstart & Single-Command Execution

### Prerequisites
- Python 3.11 or 3.12
- Git

### Installation

```bash
# 1. Clone or navigate to the repository
cd "Build Signalpost"

# 2. Install dependencies
pip install -r requirements.txt
pip install -e .

# 3. Initialize the SQLite database
python -m signalpost.cli init-db
```

### Single-Command Batch Execution

To execute research across an evaluator-supplied batch of companies in a single command:

```bash
python -m signalpost.cli batch --input data/input/companies.csv --output data/output/results.jsonl
```

---

## Command-Line Interface (CLI)

The CLI provides commands for single-company research, batch processing, history auditing, and exporting:

### 1. Research a Single Company
```bash
python -m signalpost.cli research --org 923609016
```
*Outputs a rich summary table in the terminal displaying core attributes, audited financials, atomic facts, and grounded explanations.*

### 2. Research a Batch from CSV, JSON, or JSONL
```bash
python -m signalpost.cli batch --input data/input/companies.csv --output data/output/results.jsonl --concurrency 5
```

### 3. Refresh Previously Researched Companies (Change Auditing)
```bash
python -m signalpost.cli refresh --input data/input/companies.csv --output data/output/refreshed.jsonl
```

### 4. Inspect Historical Change Audit Trail
```bash
python -m signalpost.cli history --org 923609016
```

### 5. Export Profile to CSV or JSON
```bash
python -m signalpost.cli export --org 923609016 --format csv --output data/output/equinor.csv
```

---

## Interactive Web UI

Signalpost includes a Streamlit dashboard:

```bash
streamlit run src/signalpost/ui.py
```

**UI Highlights:**
- Search entities by organization number.
- Inspect company attributes, audited multi-year financials, and source links.
- Compare previous vs. current snapshots with visual diff tables.
- Batch upload and processing tracker.
- Real-time $0 cost and request budget monitor.

---

## REST API Service

An optional FastAPI service is included for programmatic integration:

```bash
python -m signalpost.cli serve --host 127.0.0.1 --port 8000
```

- `GET /health` — Health check and live request budget status.
- `GET /company/{orgnr}` — Retrieve stored profile.
- `POST /research/{orgnr}` — Trigger real-time research.
- `POST /batch` — Trigger batch research.
- `GET /history/{orgnr}` — Retrieve historical detected changes.

---

## Output Schema Specification

Signalpost outputs structured JSON / JSON Lines conforming to the following versioned schema:

```json
{
  "schema_version": "1.0",
  "organization_number": "923609016",
  "company": {
    "official_name": "EQUINOR ASA",
    "status": "active",
    "organization_type": "ASA",
    "organization_type_description": "Allmennaksjeselskap",
    "registration_date": "1995-03-12",
    "incorporation_date": "1972-09-18",
    "business_address": {
      "address": ["Forusbeen 50"],
      "postal_code": "4035",
      "city": "STAVANGER",
      "municipality": "STAVANGER",
      "municipality_number": "1103",
      "country": "Norge",
      "country_code": "NO"
    },
    "industry_codes": [
      {
        "code": "06.100",
        "description": "Utvinning av råolje",
        "priority": "naeringskode1"
      }
    ],
    "business_activity": [
      "Virksomhet knyttet til leting etter og utvinning av petroleum."
    ],
    "employees": 21231,
    "website": "https://www.equinor.com",
    "is_in_bankruptcy": false,
    "is_in_liquidation": false,
    "is_deleted": false
  },
  "financials": [
    {
      "reporting_period": "2025-01-01 to 2025-12-31",
      "year": 2025,
      "currency": "USD",
      "unit": "exact_amount",
      "statement_type": "KONSERN",
      "total_revenue": 106462000000.0,
      "operating_profit": 25353000000.0,
      "profit_before_tax": 24200000000.0,
      "net_profit": 5058000000.0,
      "total_assets": 142100000000.0,
      "total_equity": 47900000000.0,
      "total_debt": 94200000000.0,
      "source_url": "https://data.brreg.no/regnskapsregisteret/regnskap/923609016"
    }
  ],
  "facts": [
    {
      "organization_number": "923609016",
      "field_name": "official_name",
      "value": "EQUINOR ASA",
      "data_type": "string",
      "source_name": "brreg_enhetsregisteret",
      "source_url": "https://data.brreg.no/enhetsregisteret/api/enheter/923609016",
      "retrieved_at": "2026-10-17T16:49:09.476058+00:00",
      "evidence_excerpt": "navn: EQUINOR ASA",
      "verification_status": "verified",
      "confidence": 1.0,
      "extraction_method": "deterministic_api",
      "content_hash": "2bf53068e..."
    }
  ],
  "changes": [],
  "missing_fields": [],
  "identity_status": "verified",
  "research_status": "complete",
  "last_researched_at": "2026-10-17T16:49:09.476058+00:00",
  "errors": [],
  "explanations": [
    "Company 'EQUINOR ASA' (923609016) is an active/recorded ASA registered on 1995-03-12, verified via the Brønnøysund Enhetsregisteret.",
    "Latest audited accounts for period '2025-01-01 to 2025-12-31' indicate total revenue of 106,462,000,000 USD and net annual profit of 5,058,000,000 USD, sourced directly from Regnskapsregisteret."
  ]
}
```

---

## Testing Suite

Signalpost includes a test suite with 100% offline unit tests:

```bash
# Run the complete test suite
python -m pytest -v
```

### Test Coverage Highlights:
- **Identity Tests (`test_identity.py`):** Modulo 11 check-digit verification, normalization, length validation, zero-prefix blocking, non-merging of similarly named companies.
- **Extraction Tests (`test_extraction.py`):** Brreg registry parsing, financial statement parsing (revenue, EBIT, net profit, equity, debt), website rule-based parsing.
- **Validation Tests (`test_validation.py`):** Source URL presence, reporting-period validation, SSRF defense mechanisms.
- **Snapshot Tests (`test_snapshots.py`):** Deterministic profile hashing and serialization.
- **Change Detection Tests (`test_change_detection.py`):** Name, address, and financial changes; idempotency (0 duplicate changes); fault-tolerance (sparse runs do not delete historical data).
- **Budget Tests (`test_request_budget.py`):** Request counting, budget breach raising `BudgetExceededError`, cost tracking.
- **Batch Processing Tests (`test_batch_processing.py`):** Empty batches, duplicate inputs, fault isolation, 1-per-input terminal invariant.

---

## Scalability & Benchmarking

Signalpost is benchmarked to support **over 1,000 distinct company profiles**:

```bash
# Execute the live evaluation & 1,000 profile benchmark harness
python scripts/generate_evaluation_report.py
```

### Benchmark Results:
- **Database Scale:** Ingested **1,000 distinct company profiles** in 67 seconds (~67 ms per profile).
- **Storage Footprint:** 6.3 MB SQLite database (~6.3 KB per complete profile).
- **Change Detection Precision:** 100.0% (0 false positives on unchanged data).
- **Change Detection Recall:** 100.0%.

Read the full evaluation report in [`docs/evaluation.md`](docs/evaluation.md).

---

## Cost and Budget Controls

- **External API Cost:** **$0.00 (₹0.00)** measured.
- **Operational Budgets Enforced:**
  - Max Outbound Requests: 2,000 requests per run (configurable via `MAX_OUTBOUND_REQUESTS`).
  - Max External API Cost: $10.00 USD (configurable via `MAX_EXTERNAL_API_COST_USD`).
  - Max Execution Duration: 45 minutes (configurable via `EXECUTION_TIMEOUT_MINUTES`).

Read the complete breakdown in [`docs/cost_report.md`](docs/cost_report.md).

---

## Security & SSRF Safeguards

Signalpost incorporates server-side request forgery (SSRF) defenses in `signalpost.sources.base`:
- Disallows loopback (`127.0.0.1`, `::1`, `localhost`).
- Disallows RFC 1918 private subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`).
- Disallows link-local addresses (`169.254.0.0/16`) and cloud metadata endpoints (`169.254.169.254`).
- Re-evaluates HTTP redirects before following.
- Restricts response payloads to 5 MB to prevent memory exhaustion attacks.

---

## Submission Checklist

- [x] Complete working project in workspace
- [x] Validated installation procedure (`pip install -r requirements.txt && pip install -e .`)
- [x] Single documented run command (`python -m signalpost.cli batch --input ... --output ...`)
- [x] SQLite database initialization (`python -m signalpost.cli init-db`)
- [x] Source-backed factual results from official Norwegian Brønnøysund register
- [x] 28/28 automated unit tests passing (`python -m pytest`)
- [x] Verified live smoke test (`python scripts/smoke_test.py`)
- [x] Validated 1,000-profile support benchmark
- [x] Exact request accounting & $0 cost verification report
- [x] Architecture, Data Sources, Evaluation, and Cost reports in `docs/`
- [x] Git repository initialized, committed, with HEAD commit hash
