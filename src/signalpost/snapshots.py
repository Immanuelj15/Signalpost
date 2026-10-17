"""Snapshot manager: point-in-time serialization and hashing of company profiles."""

import json
import hashlib
from typing import Optional
from signalpost.models import CompanyProfile, SnapshotRecord, utc_now_iso


class SnapshotManager:
    """Creates deterministic serialized snapshots and content hashes."""

    @staticmethod
    def create_snapshot(profile: CompanyProfile) -> SnapshotRecord:
        """Serialize profile to normalized JSON and compute sha256 hash."""
        # Dump core company and financial facts deterministically
        snapshot_payload = {
            "organization_number": profile.organization_number,
            "company": profile.company.model_dump(),
            "financials": [f.model_dump() for f in (profile.financials or [])],
            "missing_fields": sorted(profile.missing_fields),
            "identity_status": profile.identity_status.value,
        }
        normalized_json = json.dumps(snapshot_payload, sort_keys=True)
        profile_hash = hashlib.sha256(normalized_json.encode("utf-8")).hexdigest()

        return SnapshotRecord(
            organization_number=profile.organization_number,
            created_at=utc_now_iso(),
            normalized_profile_json=normalized_json,
            profile_hash=profile_hash,
        )
