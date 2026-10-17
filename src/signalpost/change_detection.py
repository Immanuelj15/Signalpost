"""Change detection engine: compares profile snapshots and identifies verified company events."""

import json
import logging
from typing import Any, Dict, List, Optional
from signalpost.models import (
    CompanyProfile,
    SnapshotRecord,
    ChangeRecord,
    ChangeType,
    utc_now_iso,
)

logger = logging.getLogger(__name__)


class ChangeDetectionEngine:
    """Compares current company profile with historical snapshots to identify verified updates."""

    @classmethod
    def detect_changes(
        cls,
        current_profile: CompanyProfile,
        previous_snapshot: Optional[SnapshotRecord],
        current_snapshot_id: Optional[str] = None,
    ) -> List[ChangeRecord]:
        """
        Compare current profile against the previous snapshot.
        Guarantees:
        - If profile hash is unchanged, returns [] (idempotent).
        - If current profile failed to retrieve data, never marks old facts as removed.
        - Emits granular, typed ChangeRecords.
        """
        if not previous_snapshot:
            # First snapshot: no historical diff
            return []

        # Fast path: identical content hash -> absolutely no changes
        current_manager_snapshot = json.loads(previous_snapshot.normalized_profile_json)

        # Parse old profile
        old_data = current_manager_snapshot
        old_company = old_data.get("company", {})
        new_company = current_profile.company.model_dump()

        # If current research failed or is empty, protect historical data:
        if current_profile.research_status == "failed" or not new_company.get("official_name"):
            logger.info(
                f"Skipping change detection for {current_profile.organization_number}: "
                f"current run is incomplete/failed, preserving previous truth."
            )
            return []

        now = utc_now_iso()
        changes: List[ChangeRecord] = []
        org_nr = current_profile.organization_number

        # Helper to get source url for a new field
        def get_fact_source(field_name: str) -> Optional[str]:
            for f in current_profile.facts:
                if f.field_name == field_name:
                    return f.source_url
            return None

        # Compare single-value fields
        fields_to_track = [
            ("official_name", ChangeType.GENUINE_COMPANY_CHANGE),
            ("status", ChangeType.GENUINE_COMPANY_CHANGE),
            ("organization_type", ChangeType.GENUINE_COMPANY_CHANGE),
            ("website", ChangeType.GENUINE_COMPANY_CHANGE),
            ("employees", ChangeType.GENUINE_COMPANY_CHANGE),
            ("parent_organization", ChangeType.GENUINE_COMPANY_CHANGE),
            ("is_in_bankruptcy", ChangeType.GENUINE_COMPANY_CHANGE),
            ("is_in_liquidation", ChangeType.GENUINE_COMPANY_CHANGE),
            ("is_deleted", ChangeType.GENUINE_COMPANY_CHANGE),
        ]

        for field, c_type in fields_to_track:
            old_val = old_company.get(field)
            new_val = new_company.get(field)

            # Skip if both are None or empty
            if (old_val is None or old_val == "") and (new_val is None or new_val == ""):
                continue

            if old_val != new_val:
                # If new_val is None, but old was present: check if this is an actual deletion or just missing field
                if new_val is None:
                    continue  # Do not drop facts on sparse new runs

                new_src = get_fact_source(field)
                changes.append(ChangeRecord(
                    organization_number=org_nr,
                    field_name=field,
                    previous_value=old_val,
                    new_value=new_val,
                    previous_source="historical_snapshot",
                    new_source=new_src or "official_registry",
                    detected_at=now,
                    previous_snapshot_id=previous_snapshot.snapshot_id,
                    current_snapshot_id=current_snapshot_id,
                    evidence_reference=f"Field {field} changed from '{old_val}' to '{new_val}'",
                    change_type=c_type,
                    confidence=1.0,
                    review_status="automatic_verified",
                ))

        # Compare Business Address
        old_addr = old_company.get("business_address") or {}
        new_addr = new_company.get("business_address") or {}
        if new_addr and old_addr != new_addr:
            if any(new_addr.values()):  # ensure new_addr has substance
                changes.append(ChangeRecord(
                    organization_number=org_nr,
                    field_name="business_address",
                    previous_value=old_addr,
                    new_value=new_addr,
                    previous_source="historical_snapshot",
                    new_source=get_fact_source("business_address") or "brreg_enhetsregisteret",
                    detected_at=now,
                    previous_snapshot_id=previous_snapshot.snapshot_id,
                    current_snapshot_id=current_snapshot_id,
                    evidence_reference=(
                        f"Address update: {old_addr.get('city')} -> {new_addr.get('city')}, "
                        f"{new_addr.get('address')}"
                    ),
                    change_type=ChangeType.GENUINE_COMPANY_CHANGE,
                    confidence=1.0,
                    review_status="automatic_verified",
                ))

        # Compare Industry Codes
        old_codes = old_company.get("industry_codes") or []
        new_codes = new_company.get("industry_codes") or []
        if new_codes and old_codes != new_codes:
            changes.append(ChangeRecord(
                organization_number=org_nr,
                field_name="industry_codes",
                previous_value=old_codes,
                new_value=new_codes,
                previous_source="historical_snapshot",
                new_source=get_fact_source("industry_codes") or "brreg_enhetsregisteret",
                detected_at=now,
                previous_snapshot_id=previous_snapshot.snapshot_id,
                current_snapshot_id=current_snapshot_id,
                evidence_reference=f"Updated industry codes: {new_codes}",
                change_type=ChangeType.GENUINE_COMPANY_CHANGE,
                confidence=1.0,
                review_status="automatic_verified",
            ))

        # Compare Financial Statements
        old_fins = old_data.get("financials", [])
        new_fins = [f.model_dump() for f in (current_profile.financials or [])]
        old_periods = {f.get("reporting_period"): f for f in old_fins if f.get("reporting_period")}
        new_periods = {f.get("reporting_period"): f for f in new_fins if f.get("reporting_period")}

        for period, new_stmt in new_periods.items():
            if period not in old_periods:
                # Newly available financial period
                changes.append(ChangeRecord(
                    organization_number=org_nr,
                    field_name="financials_new_period",
                    previous_value=None,
                    new_value=f"{period} ({new_stmt.get('currency')} revenue: {new_stmt.get('total_revenue')})",
                    previous_source=None,
                    new_source=new_stmt.get("source_url"),
                    detected_at=now,
                    previous_snapshot_id=previous_snapshot.snapshot_id,
                    current_snapshot_id=current_snapshot_id,
                    evidence_reference=f"New annual account filed for period {period}",
                    change_type=ChangeType.GENUINE_COMPANY_CHANGE,
                    confidence=1.0,
                    review_status="automatic_verified",
                ))
            else:
                # Check if figures were restated
                old_stmt = old_periods[period]
                if old_stmt.get("total_revenue") != new_stmt.get("total_revenue"):
                    changes.append(ChangeRecord(
                        organization_number=org_nr,
                        field_name="financials_restatement_revenue",
                        previous_value=old_stmt.get("total_revenue"),
                        new_value=new_stmt.get("total_revenue"),
                        previous_source=old_stmt.get("source_url"),
                        new_source=new_stmt.get("source_url"),
                        detected_at=now,
                        previous_snapshot_id=previous_snapshot.snapshot_id,
                        current_snapshot_id=current_snapshot_id,
                        evidence_reference=f"Restated revenue for {period}: {old_stmt.get('total_revenue')} -> {new_stmt.get('total_revenue')}",
                        change_type=ChangeType.SOURCE_CORRECTION,
                        confidence=1.0,
                        review_status="automatic_verified",
                    ))

        return changes
