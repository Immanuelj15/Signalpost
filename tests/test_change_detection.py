"""Tests for change detection engine, diffing, and idempotency."""

from signalpost.models import (
    CompanyProfile,
    CompanyCoreData,
    Address,
    FinancialStatement,
    Fact,
    ChangeType,
)
from signalpost.snapshots import SnapshotManager
from signalpost.change_detection import ChangeDetectionEngine


def test_first_run_no_previous_snapshot():
    profile = CompanyProfile(
        organization_number="923609016",
        company=CompanyCoreData(official_name="Fresh Company AS")
    )
    changes = ChangeDetectionEngine.detect_changes(profile, previous_snapshot=None)
    assert len(changes) == 0


def test_unchanged_profile_produces_zero_changes_idempotent():
    profile = CompanyProfile(
        organization_number="923609016",
        company=CompanyCoreData(
            official_name="Static Corp AS",
            status="active",
            business_address=Address(address=["Gate 1"], city="Bergen")
        )
    )
    snap = SnapshotManager.create_snapshot(profile)

    # Detect changes on identical profile
    changes = ChangeDetectionEngine.detect_changes(profile, previous_snapshot=snap)
    assert len(changes) == 0


def test_detect_name_change():
    old_profile = CompanyProfile(
        organization_number="923609016",
        company=CompanyCoreData(official_name="Statoil ASA")
    )
    old_snap = SnapshotManager.create_snapshot(old_profile)

    new_profile = CompanyProfile(
        organization_number="923609016",
        company=CompanyCoreData(official_name="Equinor ASA"),
        facts=[
            Fact(
                organization_number="923609016",
                field_name="official_name",
                value="Equinor ASA",
                source_name="brreg",
                source_url="https://data.brreg.no/enhetsregisteret/api/enheter/923609016",
                evidence_excerpt="navn: Equinor ASA"
            )
        ]
    )

    changes = ChangeDetectionEngine.detect_changes(new_profile, previous_snapshot=old_snap)
    assert len(changes) == 1
    ch = changes[0]
    assert ch.field_name == "official_name"
    assert ch.previous_value == "Statoil ASA"
    assert ch.new_value == "Equinor ASA"
    assert ch.change_type == ChangeType.GENUINE_COMPANY_CHANGE


def test_detect_address_change():
    old_profile = CompanyProfile(
        organization_number="923609016",
        company=CompanyCoreData(
            official_name="Tech AS",
            business_address=Address(address=["Old Street 1"], city="Oslo")
        )
    )
    old_snap = SnapshotManager.create_snapshot(old_profile)

    new_profile = CompanyProfile(
        organization_number="923609016",
        company=CompanyCoreData(
            official_name="Tech AS",
            business_address=Address(address=["New Avenue 10"], city="Trondheim")
        )
    )

    changes = ChangeDetectionEngine.detect_changes(new_profile, previous_snapshot=old_snap)
    assert len(changes) == 1
    assert changes[0].field_name == "business_address"
    assert "Trondheim" in str(changes[0].new_value)


def test_detect_new_financial_period():
    old_profile = CompanyProfile(
        organization_number="923609016",
        company=CompanyCoreData(official_name="Finance AS"),
        financials=[
            FinancialStatement(
                reporting_period="2022-01-01 to 2022-12-31",
                year=2022,
                total_revenue=5000000.0,
                source_url="https://brreg.no",
            )
        ]
    )
    old_snap = SnapshotManager.create_snapshot(old_profile)

    new_profile = CompanyProfile(
        organization_number="923609016",
        company=CompanyCoreData(official_name="Finance AS"),
        financials=[
            FinancialStatement(
                reporting_period="2023-01-01 to 2023-12-31",
                year=2023,
                total_revenue=7000000.0,
                source_url="https://brreg.no",
            ),
            FinancialStatement(
                reporting_period="2022-01-01 to 2022-12-31",
                year=2022,
                total_revenue=5000000.0,
                source_url="https://brreg.no",
            ),
        ]
    )

    changes = ChangeDetectionEngine.detect_changes(new_profile, previous_snapshot=old_snap)
    assert any(c.field_name == "financials_new_period" for c in changes)


def test_failed_run_does_not_delete_previous_truth():
    # If a new run fails or is empty, it should NOT mark existing facts as removed
    old_profile = CompanyProfile(
        organization_number="923609016",
        company=CompanyCoreData(
            official_name="Solid AS",
            status="active",
            business_address=Address(address=["Storgata 1"], city="Oslo")
        )
    )
    old_snap = SnapshotManager.create_snapshot(old_profile)

    # Simulated transient failure resulting in empty/failed profile
    failed_profile = CompanyProfile(
        organization_number="923609016",
        company=CompanyCoreData(),  # empty
        research_status="failed",
        errors=["503 Service Unavailable"]
    )

    changes = ChangeDetectionEngine.detect_changes(failed_profile, previous_snapshot=old_snap)
    assert len(changes) == 0  # Zero changes reported; historical truth preserved!
