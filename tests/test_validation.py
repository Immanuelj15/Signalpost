"""Tests for evidence validation and SSRF security controls."""

import pytest
from signalpost.models import Fact, VerificationStatus, ExtractionMethod
from signalpost.validation import EvidenceValidator
from signalpost.sources.base import is_safe_url


def test_validate_valid_fact():
    f = Fact(
        organization_number="923609016",
        field_name="official_name",
        value="Equinor ASA",
        data_type="string",
        source_name="brreg_enhetsregisteret",
        source_url="https://data.brreg.no/enhetsregisteret/api/enheter/923609016",
        evidence_excerpt="navn: Equinor ASA",
    )
    is_valid, err = EvidenceValidator.validate_fact(f, "923609016")
    assert is_valid is True
    assert err is None


def test_reject_fact_missing_source_url():
    f = Fact(
        organization_number="923609016",
        field_name="official_name",
        value="Equinor ASA",
        source_name="brreg",
        source_url="",
        evidence_excerpt="navn: Equinor",
    )
    is_valid, err = EvidenceValidator.validate_fact(f, "923609016")
    assert is_valid is False
    assert "Missing source URL" in err


def test_reject_fact_missing_evidence():
    f = Fact(
        organization_number="923609016",
        field_name="official_name",
        value="Equinor ASA",
        source_name="brreg",
        source_url="https://data.brreg.no/enhetsregisteret/api/enheter/923609016",
        evidence_excerpt="  ",
    )
    is_valid, err = EvidenceValidator.validate_fact(f, "923609016")
    assert is_valid is False
    assert "Missing evidence excerpt" in err


def test_reject_financial_fact_missing_reporting_period():
    f = Fact(
        organization_number="923609016",
        field_name="revenue",
        value=1000000.0,
        data_type="currency_amount",
        source_name="brreg_regnskap",
        source_url="https://data.brreg.no/regnskapsregisteret/regnskap/923609016",
        evidence_excerpt="sumDriftsinntekter: 1000000",
        reporting_period=None,  # Missing!
    )
    is_valid, err = EvidenceValidator.validate_fact(f, "923609016")
    assert is_valid is False
    assert "reporting_period" in err


def test_ssrf_protection_guards():
    # Loopback
    safe, reason = is_safe_url("http://127.0.0.1:8080/secret")
    assert safe is False

    safe, reason = is_safe_url("http://localhost/admin")
    assert safe is False

    # Cloud metadata
    safe, reason = is_safe_url("http://169.254.169.254/latest/meta-data/")
    assert safe is False

    # Disallowed scheme
    safe, reason = is_safe_url("file:///etc/passwd")
    assert safe is False

    safe, reason = is_safe_url("gopher://evil.com")
    assert safe is False

    # Legitimate public domain (mock DNS resolution to stay strictly offline)
    from unittest.mock import patch
    with patch("socket.getaddrinfo", return_value=[(2, 0, 0, "", ("195.43.63.68", 0))]):
        safe, reason = is_safe_url("https://data.brreg.no/enhetsregisteret/api/enheter")
        assert safe is True
