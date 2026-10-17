# Signalpost Operational Cost Report

## 1. Cost Overview

Signalpost is designed from first principles as an **evidence-first, ₹0 / $0 default architecture**. It does not require any paid LLM APIs, scraping proxies, or commercial database licenses to operate at full capability.

---

## 2. Cost Breakdown by Category

| Category | Description | Cost (USD) | Cost (INR) |
| :--- | :--- | :--- | :--- |
| **Software Licensing** | Python 3.11, SQLite, Pydantic, httpx, Typer, FastAPI, Streamlit (Open Source MIT / BSD / Apache 2.0) | **$0.00** | **₹0.00** |
| **Official Data Registry APIs** | Brønnøysund Enhetsregisteret & Regnskapsregisteret public APIs (NLOD / CC0 Open Government License) | **$0.00** | **₹0.00** |
| **Web Research** | Direct HTTP retrieval of public corporate sites via httpx with SSRF filtering | **$0.00** | **₹0.00** |
| **AI / Model Inference** | Local deterministic parsing; external LLMs are strictly opt-in and disabled by default | **$0.00** | **₹0.00** |
| **Database Storage** | Local SQLite engine with Write-Ahead Logging (WAL) | **$0.00** | **₹0.00** |
| **Local Computation** | Standard CPU computation on host machine (minimal CPU & RAM footprint) | **$0.00** | **₹0.00** |
| **Total Measured Execution Cost** | **Default operational pipeline** | **$0.00** | **₹0.00** |

---

## 3. Actual Measured Test Run Costs

| Run Context | Companies | Outbound Requests | Measured External API Cost | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Unit Test Suite** | 28 test cases | 0 (all mocked / offline) | **$0.0000** (₹0.00) | **PASS** |
| **Live Smoke Test** | 3 companies | 3 HTTP requests | **$0.0000** (₹0.00) | **PASS** |
| **Sample Batch Run** | 10 companies | 5 HTTP requests (with cache) | **$0.0000** (₹0.00) | **PASS** |
| **1,000 Profile Scale Test** | 1,000 profiles | 0 external (synthetic load test) | **$0.0000** (₹0.00) | **PASS** |

---

## 4. Cost Projection for a 1,000-Company Run

### Assumptions:
1. All 1,000 companies are queried against official Brønnøysund Register Centre APIs (`enhetsregisteret` and `regnskapsregisteret`).
2. Approximately 60% of companies have published annual financial accounts filed in `regnskapsregisteret`.
3. Approximately 40% of companies have an official website registered in Enhetsregisteret.
4. Concurrency: 5 worker threads with response caching enabled.
5. External LLM features remain disabled (`ENABLE_OPTIONAL_LLM=false`).

### Projected Costs:
- **External API Fees:** **$0.00 (₹0.00)**. Official Norwegian public register endpoints are free public government services.
- **Outbound HTTP Requests:** ~1,800 to 2,000 requests (well within the challenge's 2,000-request limit).
- **Execution Time:** ~4 to 7 minutes with concurrency of 5 (well within the 45-minute limit).
- **Database Storage:** ~6.5 MB SQLite database file.
- **Estimated Total Cost for 1,000 Companies:** **$0.00 (₹0.00)**.

---

## 5. Optional Cloud Hosting Cost Estimates

If deployed continuously in production:
- **Local / Bare Metal / Developer Workstation:** **$0.00 / month**.
- **Containerized VPS (Hetzner, DigitalOcean, Linode):** ~$4.00 - $6.00 / month (1 vCPU, 2 GB RAM).
- **Serverless Container (Google Cloud Run / AWS ECS Fargate):** ~$0.00 to $2.00 / month within free-tier compute allowances.
