# Signalpost Architecture Document

## 1. System Overview

**Signalpost** is an autonomous, evidence-first company intelligence agent tailored for Norwegian businesses. It accepts Norwegian organization numbers (*organisasjonsnummer*), resolves official corporate identities, extracts attributable facts from open public data registries, stores historical snapshots in SQLite, and performs deterministic change detection over time.

Signalpost operates under a **free-first execution model (₹0 / $0)**, relying on official Norwegian open government APIs and deterministic extraction rather than paid LLMs.

```
                      ┌────────────────────────────┐
                      │    Input & Batch Manager   │
                      │   (CLI, CSV, JSON, JSONL)  │
                      └─────────────┬──────────────┘
                                    │
                                    ▼
                      ┌────────────────────────────┐
                      │  Company Identity Resolver │
                      │  (Modulo 11 Checksum Auth) │
                      └─────────────┬──────────────┘
                                    │
                                    ▼
                      ┌────────────────────────────┐
                      │      Research Planner      │
                      │  (Lightweight & Bounded)   │
                      └─────────────┬──────────────┘
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         │                          │                          │
         ▼                          ▼                          ▼
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│ Source Adapter A │      │ Source Adapter B │      │ Source Adapter C │
│ Enhetsregisteret │      │ Regnskapsregister│      │ Verified Website │
│ (Official Brreg) │      │  (Financials)    │      │  (SSRF Guarded)  │
└────────┬─────────┘      └────────┬─────────┘      └────────┬─────────┘
         │                          │                          │
         └──────────────────────────┼──────────────────────────┘
                                    │
                                    ▼
                      ┌────────────────────────────┐
                      │    Fact Extraction &       │
                      │    Evidence Validator      │
                      └─────────────┬──────────────┘
                                    │
                                    ▼
                      ┌────────────────────────────┐
                      │  Profile Builder & Snapshots│
                      └─────────────┬──────────────┘
                                    │
                                    ▼
                      ┌────────────────────────────┐
                      │  Change Detection Engine   │
                      │   (Idempotent Diffing)     │
                      └─────────────┬──────────────┘
                                    │
                                    ▼
                      ┌────────────────────────────┐
                      │   Explanation Generator &  │
                      │      Output Adapters       │
                      │   (JSON, JSONL, CSV, UI)   │
                      └────────────────────────────┘
```

---

## 2. Core Components

### Component 1: Input and Batch Manager (`signalpost.export`)
- Accepts input via CLI arguments, CSV, JSON, JSONL, or REST API.
- Normalizes organization numbers, stripping punctuation, spaces, and prefixes (e.g., `NO-923.609.016 MVA` -> `923609016`).
- Deduplicates inputs while strictly preserving the original input order.
- Guarantees the **1-result-per-input invariant**: every submitted organization number yields exactly one terminal result, including syntactically invalid numbers.

### Component 2: Company Identity Resolver (`signalpost.identity`)
- Enforces official Norwegian 9-digit Modulo 11 check digit verification with weights `[3, 2, 7, 6, 5, 4, 3, 2]`.
- Enforces rule that Norwegian organization numbers cannot start with `0`.
- Validates the returned registry record against the requested organization number.
- **Identity Safety Rule:** Never merges two entities based on name similarity or shared address. The 9-digit organization number is the sole primary key.

### Component 3: Research Planner (`signalpost.planner`)
- Inspects existing database profile to prevent redundant outbound HTTP queries.
- Determines whether registry data, financial statements, or website analysis is required.
- Supports forced refreshes for temporal change auditing.

### Component 4: Source Retrieval Engine (`signalpost.sources.base`)
- Safe HTTP retrieval using `httpx`.
- Configurable timeouts (default 15s) and exponential backoff with jitter on HTTP 429 and 5xx.
- Respects upstream `Retry-After` headers.
- **Server-Side Request Forgery (SSRF) Guard:**
  - Evaluates URL destination before making connections.
  - Rejects loopback (`127.0.0.1`, `::1`, `localhost`), RFC 1918 private subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), link-local (`169.254.0.0/16`), multicast, and cloud metadata endpoints (`169.254.169.254`).
  - Re-evaluates redirect destinations.
- Enforces response size caps (5 MB maximum) to guard against resource exhaustion.
- Enforces operational budget limits via `RequestBudgetManager`.

### Component 5: Fact Extraction Engine (`signalpost.sources.*`)
- Converts raw responses into standardized, atomic `Fact` objects.
- Each fact records:
  - `field_name`
  - `value`
  - `data_type`
  - `source_name`
  - `source_url`
  - `retrieved_at` (UTC ISO 8601)
  - `published_at`
  - `reporting_period` (mandatory for financial figures)
  - `evidence_excerpt`
  - `verification_status` (`verified`, `derived`, `unverified`, `unavailable`)
  - `confidence` (0.0 to 1.0)
  - `extraction_method` (`deterministic_api`, `rule_based_html`, `derived`)
  - `content_hash` (SHA-256)

### Component 6: Evidence & Identity Validator (`signalpost.validation`)
- Confirms organization number match.
- Enforces presence of source URLs and non-empty evidence excerpts.
- Validates currencies, units, and date formats (`YYYY-MM-DD`).
- Detects and flags contradictory claims across sources.

### Component 7: Profile Builder (`signalpost.profile_builder`)
- Constructs normalized `CompanyProfile` complying with the challenge's versioned schema.
- Gracefully handles partial data: missing fields are populated as explicit `null`/empty and summarized in `missing_fields`.

### Component 8: Snapshot Manager & Change Detection (`signalpost.snapshots`, `signalpost.change_detection`)
- Serializes normalized profile to deterministic JSON and generates SHA-256 hash.
- Compares new profile with the previous snapshot:
  - Detects name, address, status, employee count, website, industry code, and financial statement additions or restatements.
  - Classifies change events (`genuine_company_change`, `source_correction`, `extraction_correction`).
  - **Idempotency Guarantee:** Re-running against unchanged data yields zero duplicate change records.
  - **Fault Tolerance:** If a research run fails due to temporary network issues, previous factual claims are preserved and never marked as removed.

### Component 9: Grounded Explanation Generator (`signalpost.explanations`)
- Generates human-readable, verifiable explanations directly linked to recorded facts and source URLs.

### Component 10: Export & User Interfaces (`signalpost.export`, `signalpost.cli`, `signalpost.ui`, `signalpost.api`)
- Multi-format exporters: JSON, JSON Lines, flattened CSV.
- Rich terminal tables.
- Interactive Streamlit dashboard.
- FastAPI REST service.

---

## 3. Database Schema (SQLite)

Signalpost uses SQLite with **Write-Ahead Logging (WAL)** and foreign keys enabled:

1. **`companies`**: Primary registry of entities (`organization_number` PRIMARY KEY, name, status, website, dates, full profile JSON).
2. **`sources`**: Audit log of external HTTP requests (`source_id` PRIMARY KEY, URL, HTTP status, content hash, retrieval time).
3. **`facts`**: Atomic claims (`fact_id` PRIMARY KEY, orgnr, field_name, value_json, source_url, evidence_excerpt, timestamps).
4. **`snapshots`**: Versioned historical profile states (`snapshot_id` PRIMARY KEY, orgnr, created_at, profile_json, profile_hash).
5. **`changes`**: Granular detected changes (`change_id` PRIMARY KEY, orgnr, field_name, previous_value, new_value, timestamps).
6. **`research_runs`**: Operational execution ledger (`run_id` PRIMARY KEY, counts, requests used, API cost, status).
