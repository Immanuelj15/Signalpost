"""Brønnøysund Register Centre (Enhetsregisteret) official API adapter."""

import json
import hashlib
import logging
from typing import Any, Dict, List, Optional, Tuple

from signalpost.models import (
    Fact,
    SourceRecord,
    VerificationStatus,
    ExtractionMethod,
    utc_now_iso,
)
from signalpost.sources.base import BaseSourceAdapter

logger = logging.getLogger(__name__)

BASE_ENHETER_URL = "https://data.brreg.no/enhetsregisteret/api/enheter"


def make_fact(
    org_nr: str,
    field_name: str,
    value: Any,
    data_type: str,
    source_url: str,
    evidence_excerpt: str,
    retrieved_at: str,
    published_at: Optional[str] = None,
) -> Fact:
    """Helper to construct verified fact with content hash."""
    val_str = json.dumps(value, sort_keys=True) if isinstance(value, (dict, list)) else str(value)
    content_hash = hashlib.sha256(f"{org_nr}:{field_name}:{val_str}".encode("utf-8")).hexdigest()
    return Fact(
        organization_number=org_nr,
        field_name=field_name,
        value=value,
        data_type=data_type,
        source_name="brreg_enhetsregisteret",
        source_url=source_url,
        retrieved_at=retrieved_at,
        published_at=published_at,
        evidence_excerpt=evidence_excerpt[:500],
        verification_status=VerificationStatus.VERIFIED,
        confidence=1.0,
        extraction_method=ExtractionMethod.DETERMINISTIC_API,
        content_hash=content_hash,
    )


class BrregEnhetsregisterAdapter(BaseSourceAdapter):
    """Adapter for official Enhetsregisteret API."""

    source_name = "brreg_enhetsregisteret"
    source_type = "api"

    def fetch_and_extract(self, org_nr: str) -> Tuple[List[Fact], Optional[SourceRecord]]:
        """Query official Brreg Enhetsregisteret API for an organization number."""
        url = f"{BASE_ENHETER_URL}/{org_nr}"
        now = utc_now_iso()

        resp, error_cat, status_code = self.safe_get(
            url,
            headers={"Accept": "application/json"},
            check_ssrf=True
        )

        source_rec = SourceRecord(
            source_name=self.source_name,
            source_url=url,
            source_type=self.source_type,
            retrieved_at=now,
            http_status=status_code,
            extraction_status="success" if resp and resp.status_code == 200 else (error_cat or "failed"),
            error_category=error_cat,
        )

        if not resp or resp.status_code != 200:
            return [], source_rec

        try:
            data = resp.json()
            source_rec.content_hash = hashlib.sha256(resp.content).hexdigest()
        except Exception as e:
            source_rec.extraction_status = f"json_decode_error: {e}"
            return [], source_rec

        # Verify returned org number
        returned_org = str(data.get("organisasjonsnummer", ""))
        if returned_org != org_nr:
            source_rec.extraction_status = f"org_mismatch_{returned_org}"
            return [], source_rec

        facts: List[Fact] = []

        # 1. Official Name
        name = data.get("navn")
        if name:
            facts.append(make_fact(
                org_nr, "official_name", name, "string", url,
                f"navn: {name}", now
            ))

        # 2. Organization Form
        org_form = data.get("organisasjonsform")
        if isinstance(org_form, dict):
            code = org_form.get("kode")
            desc = org_form.get("beskrivelse")
            if code:
                facts.append(make_fact(
                    org_nr, "organization_type", code, "string", url,
                    f"organisasjonsform.kode: {code} ({desc})", now
                ))
            if desc:
                facts.append(make_fact(
                    org_nr, "organization_type_description", desc, "string", url,
                    f"organisasjonsform.beskrivelse: {desc}", now
                ))

        # 3. Registration & Incorporation Dates
        reg_date = data.get("registreringsdatoEnhetsregisteret")
        if reg_date:
            facts.append(make_fact(
                org_nr, "registration_date", reg_date, "date", url,
                f"registreringsdatoEnhetsregisteret: {reg_date}", now, published_at=reg_date
            ))

        inc_date = data.get("stiftelsesdato")
        if inc_date:
            facts.append(make_fact(
                org_nr, "incorporation_date", inc_date, "date", url,
                f"stiftelsesdato: {inc_date}", now, published_at=inc_date
            ))

        # 4. Business Address (forretningsadresse)
        b_addr = data.get("forretningsadresse")
        if isinstance(b_addr, dict):
            addr_dict = {
                "address": b_addr.get("adresse", []),
                "postal_code": b_addr.get("postnummer"),
                "city": b_addr.get("poststed"),
                "municipality": b_addr.get("kommune"),
                "municipality_number": b_addr.get("kommunenummer"),
                "country": b_addr.get("land", "Norge"),
                "country_code": b_addr.get("landkode", "NO"),
            }
            facts.append(make_fact(
                org_nr, "business_address", addr_dict, "address", url,
                f"forretningsadresse: {json.dumps(addr_dict)}", now
            ))

        # 5. Postal Address (postadresse)
        p_addr = data.get("postadresse")
        if isinstance(p_addr, dict):
            p_addr_dict = {
                "address": p_addr.get("adresse", []),
                "postal_code": p_addr.get("postnummer"),
                "city": p_addr.get("poststed"),
                "municipality": p_addr.get("kommune"),
                "municipality_number": p_addr.get("kommunenummer"),
                "country": p_addr.get("land", "Norge"),
                "country_code": p_addr.get("landkode", "NO"),
            }
            facts.append(make_fact(
                org_nr, "postal_address", p_addr_dict, "address", url,
                f"postadresse: {json.dumps(p_addr_dict)}", now
            ))

        # 6. Industry codes (NACE)
        industry_codes = []
        for key in ["naeringskode1", "naeringskode2", "naeringskode3"]:
            nk = data.get(key)
            if isinstance(nk, dict) and nk.get("kode"):
                industry_codes.append({
                    "code": nk.get("kode"),
                    "description": nk.get("beskrivelse", ""),
                    "priority": key
                })
        if industry_codes:
            facts.append(make_fact(
                org_nr, "industry_codes", industry_codes, "list", url,
                f"industry_codes: {json.dumps(industry_codes)}", now
            ))

        # 7. Business activity description
        activity = data.get("aktivitet", [])
        if activity:
            if isinstance(activity, str):
                activity = [activity]
            facts.append(make_fact(
                org_nr, "business_activity", activity, "list", url,
                f"aktivitet: {' '.join(activity)[:200]}", now
            ))

        # 8. Employee count
        employees = data.get("antallAnsatte")
        if employees is not None:
            facts.append(make_fact(
                org_nr, "employees", int(employees), "integer", url,
                f"antallAnsatte: {employees}", now
            ))

        # 9. Canonical Website
        hjemmeside = data.get("hjemmeside")
        if hjemmeside:
            # normalize URL scheme if missing
            ws = str(hjemmeside).strip()
            if ws and not ws.startswith(("http://", "https://")):
                ws = f"https://{ws}"
            facts.append(make_fact(
                org_nr, "website", ws, "url", url,
                f"hjemmeside: {hjemmeside}", now
            ))

        # 10. Parent Organization
        overordnet = data.get("overordnetEnhet")
        if overordnet:
            facts.append(make_fact(
                org_nr, "parent_organization", str(overordnet), "string", url,
                f"overordnetEnhet: {overordnet}", now
            ))

        # 11. Company Status (bankruptcy, liquidation, deletion)
        konkurs = bool(data.get("konkurs", False))
        facts.append(make_fact(
            org_nr, "is_in_bankruptcy", konkurs, "boolean", url,
            f"konkurs: {konkurs}", now
        ))

        avvikling = bool(
            data.get("underAvvikling", False)
            or data.get("underTvangsavviklingEllerTvangsopplosning", False)
        )
        facts.append(make_fact(
            org_nr, "is_in_liquidation", avvikling, "boolean", url,
            f"underAvvikling: {avvikling}", now
        ))

        slettedato = data.get("slettedato")
        is_deleted = bool(slettedato)
        facts.append(make_fact(
            org_nr, "is_deleted", is_deleted, "boolean", url,
            f"slettedato: {slettedato}", now
        ))
        if slettedato:
            facts.append(make_fact(
                org_nr, "deleted_date", slettedato, "date", url,
                f"slettedato: {slettedato}", now, published_at=slettedato
            ))

        # Determine overall company status
        if is_deleted:
            overall_status = "dissolved"
        elif konkurs:
            overall_status = "bankruptcy"
        elif avvikling:
            overall_status = "in_liquidation"
        else:
            overall_status = "active"

        facts.append(make_fact(
            org_nr, "status", overall_status, "string", url,
            f"derived_status: {overall_status}", now
        ))

        return facts, source_rec
