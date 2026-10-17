# Signalpost Data Sources & Source Adapter Documentation

## 1. Overview

Signalpost implements a modular source-adapter architecture designed to prioritize **official, authoritative, and legally compliant public data sources**.

All sources operate under open government licenses or standard web terms. No paid subscription, API key, or scraping bypass is required.

---

## 2. Source A: Brønnøysund Register Centre — Enhetsregisteret

- **Role:** Official Norwegian Central Coordinating Register for Legal Entities.
- **Base Endpoint:** `https://data.brreg.no/enhetsregisteret/api/enheter/{orgnr}`
- **License:** Norwegian Licence for Open Government Data (NLOD) / CC0.
- **Cost:** Free public API ($0 / ₹0).
- **Rate Limits & Politeness:**
  - Standard open government access.
  - Signalpost uses a custom `User-Agent` header (`Signalpost-Research-Agent/1.0`).
  - Exponential backoff with respect for `Retry-After`.

### Fields Extracted:
| Registry Field | Signalpost Attribute | Data Type | Description |
| :--- | :--- | :--- | :--- |
| `organisasjonsnummer` | `organization_number` | string | Canonical 9-digit corporate identifier |
| `navn` | `official_name` | string | Legal registered company name |
| `organisasjonsform.kode` | `organization_type` | string | Legal corporate form code (AS, ASA, ENK, etc.) |
| `organisasjonsform.beskrivelse` | `organization_type_description` | string | Full description of legal form |
| `forretningsadresse` | `business_address` | object | Street address, postal code, city, municipality |
| `postadresse` | `postal_address` | object | Mailing address if distinct from business location |
| `registreringsdatoEnhetsregisteret` | `registration_date` | date | Date registered in Central Coordinating Register |
| `stiftelsesdato` | `incorporation_date` | date | Official incorporation / foundation date |
| `naeringskode1` | `industry_codes` | list | Primary NACE industry classification code & text |
| `aktivitet` | `business_activity` | list | Declared commercial objectives and activities |
| `antallAnsatte` | `employees` | integer | Number of registered employees |
| `hjemmeside` | `website` | url | Official verified company website URL |
| `overordnetEnhet` | `parent_organization` | string | Parent enterprise organization number (if subsidiary) |
| `konkurs` | `is_in_bankruptcy` | boolean | True if company is in bankruptcy proceedings |
| `underAvvikling` | `is_in_liquidation` | boolean | True if company is under voluntary/compulsory liquidation |
| `slettedato` | `is_deleted` / `deleted_date` | date | Dissolution / deregistration date |

---

## 3. Source B: Brønnøysund Register Centre — Regnskapsregisteret

- **Role:** Official Register of Company Accounts (Annual Financial Statements).
- **Base Endpoint:** `https://data.brreg.no/regnskapsregisteret/regnskap/{orgnr}`
- **License:** NLOD / Public corporate disclosure under the Norwegian Accounting Act (*Regnskapsloven*).
- **Cost:** Free public API ($0 / ₹0).
- **Key Extraction Rules:**
  - Financial statements are strictly scoped by **reporting period** (`fraDato` to `tilDato`).
  - **Financial Metrics Distinguished:**
    - Operating Revenue / Total Revenue (`sumDriftsinntekter`)
    - Sales Revenue (`salgsinntekter`)
    - Operating Profit / EBIT (`driftsresultat`)
    - Profit Before Tax / EBT (`ordinaertResultatFoerSkattekostnad`)
    - Net Annual Profit / Loss (`aarsresultat`)
    - Total Assets (`sumEiendeler`)
    - Total Equity (`sumEgenkapital`)
    - Total Liabilities / Debt (`sumGjeld`)
  - Reporting currency (NOK, USD, EUR) is explicitly preserved.
  - Accounting standards (IFRS, Norwegian GAAP / *små foretak*) are recorded.

---

## 4. Source C: Verified Company Websites

- **Role:** Discovers public-facing descriptions, contact details, and product offerings.
- **Discovery Condition:** Analyzed **only** when an official website URL has been confirmed through Enhetsregisteret's registered `hjemmeside` field or validated domain ownership.
- **Domain Verification:** Checks for organization number or company name occurrence in page content to verify link between website and company.
- **SSRF Protection:**
  - Rejects loopback, private RFC 1918 addresses, and link-local IP addresses.
  - Rejects cloud metadata addresses (`169.254.169.254`).
  - Revalidates redirect destinations before connecting.
- **Extracted Content:**
  - Meta description & OpenGraph description -> `business_description`
  - Contact email addresses -> `contact_email`
  - Norwegian phone numbers -> `contact_phone`
  - Products & services offerings -> `products_and_services`

---

## 5. Graceful Degradation & Error Handling

- **Source Independence:** If Regnskapsregisteret or a company website is temporarily down, the pipeline completes with registry facts.
- **Deterministic Statuses:**
  - `complete`: Registry facts and audited financials verified.
  - `partial`: Registry facts verified; financials or website not filed/accessible.
  - `not_found`: Organization number not registered in Central Coordinating Register (HTTP 404).
  - `failed`: Syntactically invalid organization number (checksum failure) or budget exhaustion.
