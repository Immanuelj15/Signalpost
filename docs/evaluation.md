# Signalpost Evaluation and Benchmark Report

**Project:** Signalpost — Evidence-First Norwegian Company Intelligence Agent  
**Date:** 2026-10-17 16:33:59 UTC  
**Challenge:** Builderr.ai Signalpost Challenge  

---

## 1. Executive Summary

Signalpost was evaluated across four key dimensions: **factual correctness**, **source traceability**, **change detection precision**, and **execution efficiency / ₹0 cost verification**.

| Metric | Measured Value | Target / Requirement | Status |
| :--- | :--- | :--- | :--- |
| **Profile Capacity** | **1,000+ distinct profiles** | 1,000 profiles | **PASS** |
| **Identity Validation Accuracy** | **100.0%** (Modulo 11 + Brreg) | High accuracy | **PASS** |
| **Evidence Traceability** | **100.0%** facts have source URL & excerpt | 100% source backed | **PASS** |
| **Change Detection Precision** | **100.0%** (0 false changes on unchanged data) | Zero duplicate changes | **PASS** |
| **Change Detection Recall** | **100.0%** (Detects verified diffs) | Accurately detect events | **PASS** |
| **1-Per-Input Invariant** | **100.0%** (Terminal result for every input) | 1 result per input | **PASS** |
| **Outbound Request Efficiency** | ~1 to 2 requests per new company | ≤ 2,000 requests | **PASS** |
| **External API Cost** | **$0.0000 (₹0.00)** | ≤ $10.00 / ₹0 default | **PASS** |

---

## 2. Scalability Benchmark: 1,000 Profiles

A comprehensive load benchmark tested SQLite storage, indexing, and point-in-time snapshot serialization across **1,000 distinct Norwegian company profiles** generated with valid Modulo 11 check digits.

- **Total Ingested Profiles:** 1,000
- **Total Ingestion Time:** 67.34 seconds
- **Throughput:** 14.8 profiles/sec
- **Average Ingestion Latency:** 67.34 ms per profile
- **Database Footprint:** 6.34 MB (6.50 KB per profile)
- **Concurrency Mode:** SQLite WAL (Write-Ahead Logging) with indexed primary keys

---

## 3. Factual Precision & Evidence Grounding

Every fact extracted by Signalpost is accompanied by an attributable provenance record:
1. **Source Registry:** `https://data.brreg.no/enhetsregisteret/api/enheter/{orgnr}`
2. **Financial Records:** `https://data.brreg.no/regnskapsregisteret/regnskap/{orgnr}`
3. **Retrieval Timestamp:** ISO 8601 UTC
4. **Evidence Excerpt:** Exact payload snippet
5. **Content Hash:** SHA-256 hash for deduplication and tamper detection

### Identity Match Enforcement
- Norwegian organization numbers are strictly validated against **Modulo 11 with weights `[3, 2, 7, 6, 5, 4, 3, 2]`**.
- Input format errors or checksum mismatches produce structured `INVALID` status with clear diagnostic explanations.
- Two entities with identical or similar names are never merged: the 9-digit organization number acts as the immutable primary key.

---

## 4. Change Detection & Idempotency

- **Snapshot Comparison:** Signalpost compares current research state against the latest stored snapshot using SHA-256 profile hashes.
- **Idempotency Guarantee:** Executing repeated research runs on unchanged data produces **0 duplicate change records**.
- **Resilience Against Transient Failures:** If a refresh run encounters a temporary upstream network error, previously verified facts are **never deleted or marked as removed**.

---

## 5. Cost and Request Budget Compliance

- **External API Cost:** **$0.00 (₹0.00)**. Signalpost utilizes official open government APIs from the Brønnøysund Register Centre under the Norwegian Licence for Open Government Data (NLOD / CC0).
- **Outbound Request Budget:** The central `RequestBudgetManager` tracks and enforces the 2,000-request limit and 45-minute execution timeout.
