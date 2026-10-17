"""Tests for snapshot creation and serialization."""

from signalpost.models import CompanyProfile, CompanyCoreData, Address
from signalpost.snapshots import SnapshotManager


def test_snapshot_deterministic_hashing():
    profile_a = CompanyProfile(
        organization_number="923609016",
        company=CompanyCoreData(
            official_name="Nordic Energy AS",
            status="active",
            business_address=Address(address=["Storgata 1"], postal_code="0155", city="OSLO"),
        )
    )
    profile_b = CompanyProfile(
        organization_number="923609016",
        company=CompanyCoreData(
            official_name="Nordic Energy AS",
            status="active",
            business_address=Address(address=["Storgata 1"], postal_code="0155", city="OSLO"),
        )
    )

    snap_a = SnapshotManager.create_snapshot(profile_a)
    snap_b = SnapshotManager.create_snapshot(profile_b)

    assert snap_a.profile_hash == snap_b.profile_hash
    assert len(snap_a.profile_hash) == 64  # sha256


def test_snapshot_hash_changes_on_modification():
    profile_a = CompanyProfile(
        organization_number="923609016",
        company=CompanyCoreData(official_name="Old Name AS")
    )
    profile_b = CompanyProfile(
        organization_number="923609016",
        company=CompanyCoreData(official_name="New Name AS")
    )

    snap_a = SnapshotManager.create_snapshot(profile_a)
    snap_b = SnapshotManager.create_snapshot(profile_b)

    assert snap_a.profile_hash != snap_b.profile_hash
