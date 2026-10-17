"""Official financial accounts adapter via Brønnøysund Regnskapsregisteret."""

import json
import hashlib
import logging
from typing import Any, Dict, List, Optional, Tuple

from signalpost.models import (
    Fact,
    SourceRecord,
    FinancialStatement,
    VerificationStatus,
    ExtractionMethod,
    utc_now_iso,
)
from signalpost.sources.base import BaseSourceAdapter

logger = logging.getLogger(__name__)

BASE_REGNSKAP_URL = "https://data.brreg.no/regnskapsregisteret/regnskap"


def make_financial_fact(
    org_nr: str,
    field_name: str,
    value: Any,
    currency: str,
    reporting_period: str,
    source_url: str,
    evidence_excerpt: str,
    retrieved_at: str,
    published_at: Optional[str] = None,
) -> Fact:
    """Helper to construct verified financial fact with reporting period and currency."""
    content_hash = hashlib.sha256(
        f"{org_nr}:{field_name}:{reporting_period}:{value}:{currency}".encode("utf-8")
    ).hexdigest()

    return Fact(
        organization_number=org_nr,
        field_name=field_name,
        value=value,
        data_type="currency_amount",
        source_name="brreg_regnskapsregisteret",
        source_url=source_url,
        retrieved_at=retrieved_at,
        published_at=published_at,
        reporting_period=reporting_period,
        evidence_excerpt=evidence_excerpt[:500],
        verification_status=VerificationStatus.VERIFIED,
        confidence=1.0,
        extraction_method=ExtractionMethod.DETERMINISTIC_API,
        content_hash=content_hash,
    )


class BrregRegnskapAdapter(BaseSourceAdapter):
    """Adapter for official annual accounts from Regnskapsregisteret."""

    source_name = "brreg_regnskapsregisteret"
    source_type = "api"

    def fetch_and_extract_statements(
        self, org_nr: str
    ) -> Tuple[List[FinancialStatement], List[Fact], Optional[SourceRecord]]:
        """
        Fetch official annual accounts and return both structured statements and atomic facts.
        """
        url = f"{BASE_REGNSKAP_URL}/{org_nr}"
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
            return [], [], source_rec

        try:
            raw_list = resp.json()
            source_rec.content_hash = hashlib.sha256(resp.content).hexdigest()
        except Exception as e:
            source_rec.extraction_status = f"json_decode_error: {e}"
            return [], [], source_rec

        if not isinstance(raw_list, list):
            source_rec.extraction_status = "unexpected_schema_not_a_list"
            return [], [], source_rec

        statements: List[FinancialStatement] = []
        facts: List[Fact] = []

        # Process each filing, latest first
        for item in raw_list:
            if not isinstance(item, dict):
                continue

            period_info = item.get("regnskapsperiode", {})
            fra_dato = period_info.get("fraDato")
            til_dato = period_info.get("tilDato")
            if not til_dato:
                continue

            period_str = f"{fra_dato or 'unknown'} to {til_dato}"
            try:
                year = int(til_dato.split("-")[0])
            except (ValueError, IndexError):
                year = 0

            currency = item.get("valuta", "NOK")
            statement_type = item.get("regnskapstype", "SELSKAP")
            journalnr = item.get("journalnr")
            filing_id = item.get("id")

            rules_info = item.get("regnkapsprinsipper", {})
            rules_str = rules_info.get("regnskapsregler")

            # Extract metrics
            drifts = item.get("resultatregnskapResultat", {}).get("driftsresultat", {})
            driftsinntekter = drifts.get("driftsinntekter", {})
            total_rev = driftsinntekter.get("sumDriftsinntekter")
            sales_rev = driftsinntekter.get("salgsinntekter")
            operating_profit = drifts.get("driftsresultat")

            resultat = item.get("resultatregnskapResultat", {})
            ebt = resultat.get("ordinaertResultatFoerSkattekostnad")
            net_profit = resultat.get("aarsresultat")

            eiendeler = item.get("eiendeler", {})
            total_assets = eiendeler.get("sumEiendeler")

            eq_debt = item.get("egenkapitalGjeld", {})
            eq_info = eq_debt.get("egenkapital", {})
            total_equity = eq_info.get("sumEgenkapital")

            debt_info = eq_debt.get("gjeldOversikt", {})
            total_debt = debt_info.get("sumGjeld")

            statement = FinancialStatement(
                reporting_period=period_str,
                year=year,
                currency=currency,
                unit="exact_amount",
                statement_type=statement_type,
                accounting_rules=rules_str,
                total_revenue=float(total_rev) if total_rev is not None else None,
                sales_revenue=float(sales_rev) if sales_rev is not None else None,
                operating_profit=float(operating_profit) if operating_profit is not None else None,
                profit_before_tax=float(ebt) if ebt is not None else None,
                net_profit=float(net_profit) if net_profit is not None else None,
                total_assets=float(total_assets) if total_assets is not None else None,
                total_equity=float(total_equity) if total_equity is not None else None,
                total_debt=float(total_debt) if total_debt is not None else None,
                source_url=url,
                filing_id=filing_id,
                journal_number=journalnr,
            )
            statements.append(statement)

            # Create individual attributable facts
            metric_map = [
                ("total_revenue", total_rev, "driftsinntekter.sumDriftsinntekter"),
                ("sales_revenue", sales_rev, "driftsinntekter.salgsinntekter"),
                ("operating_profit", operating_profit, "driftsresultat"),
                ("profit_before_tax", ebt, "ordinaertResultatFoerSkattekostnad"),
                ("net_profit", net_profit, "aarsresultat"),
                ("total_assets", total_assets, "eiendeler.sumEiendeler"),
                ("total_equity", total_equity, "egenkapital.sumEgenkapital"),
                ("total_debt", total_debt, "gjeldOversikt.sumGjeld"),
            ]

            for field_name, metric_val, raw_key in metric_map:
                if metric_val is not None:
                    excerpt = (
                        f"Financial filing {filing_id} ({period_str}) {statement_type} "
                        f"{raw_key}: {metric_val} {currency}"
                    )
                    facts.append(make_financial_fact(
                        org_nr=org_nr,
                        field_name=f"{field_name}_{year}",
                        value=float(metric_val),
                        currency=currency,
                        reporting_period=period_str,
                        source_url=url,
                        evidence_excerpt=excerpt,
                        retrieved_at=now,
                        published_at=til_dato,
                    ))

        # Sort statements by year descending
        statements.sort(key=lambda s: s.year, reverse=True)
        return statements, facts, source_rec

    def fetch_and_extract(self, org_nr: str) -> Tuple[List[Fact], Optional[SourceRecord]]:
        """Satisfy BaseSourceAdapter interface."""
        _, facts, source_rec = self.fetch_and_extract_statements(org_nr)
        return facts, source_rec
