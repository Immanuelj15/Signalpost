"""Tests for batch processing, deduplication, error tolerance, and 1-result-per-input invariant."""

import pytest
from unittest.mock import MagicMock, patch
from signalpost.orchestrator import ResearchAgent
from signalpost.models import CompanyProfile, CompanyCoreData, IdentityStatus, ResearchStatus
from signalpost.database import Database


@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_signalpost.db"
    database = Database(str(db_file))
    database.init_db()
    return database


def test_empty_batch(temp_db):
    agent = ResearchAgent(database=temp_db)
    profiles, run = agent.research_batch([])
    assert len(profiles) == 0
    assert run.companies_requested == 0
    assert run.companies_completed == 0


def test_batch_deduplication_and_order_preservation(temp_db):
    agent = ResearchAgent(database=temp_db)

    # Mock research_company to return fake profile without network
    def mock_research(org, force_refresh=False):
        return CompanyProfile(
            organization_number=org,
            company=CompanyCoreData(official_name=f"Company {org}"),
            identity_status=IdentityStatus.VERIFIED if org == "923609016" else IdentityStatus.INVALID,
        )

    with patch.object(agent, "research_company", side_effect=mock_research):
        inputs = ["923609016", "984851006", "923609016", "984851006"]
        profiles, run = agent.research_batch(inputs, max_workers=1)

    # Exactly 4 terminal results returned corresponding to the 4 inputs
    assert len(profiles) == 4
    assert [p.organization_number for p in profiles] == inputs
    # But only 2 unique companies requested in run summary
    assert run.companies_completed == 2


def test_batch_one_failed_company_among_successful(temp_db):
    agent = ResearchAgent(database=temp_db)

    def mock_research(org, force_refresh=False):
        if org == "111111111":
            # Invalid org
            return CompanyProfile(
                organization_number=org,
                company=CompanyCoreData(),
                identity_status=IdentityStatus.INVALID,
                research_status=ResearchStatus.FAILED,
                errors=["Checksum failure"],
            )
        return CompanyProfile(
            organization_number=org,
            company=CompanyCoreData(official_name="Valid AS"),
            identity_status=IdentityStatus.VERIFIED,
            research_status=ResearchStatus.COMPLETE,
        )

    with patch.object(agent, "research_company", side_effect=mock_research):
        inputs = ["923609016", "111111111", "984851006"]
        profiles, run = agent.research_batch(inputs, max_workers=2)

    assert len(profiles) == 3
    assert profiles[0].identity_status == IdentityStatus.VERIFIED
    assert profiles[1].identity_status == IdentityStatus.INVALID
    assert profiles[1].research_status == ResearchStatus.FAILED
    assert profiles[2].identity_status == IdentityStatus.VERIFIED
