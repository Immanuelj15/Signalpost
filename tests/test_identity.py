"""Tests for identity resolution and Norwegian organization number validation."""

import pytest
from signalpost.identity import (
    normalize_org_number,
    validate_norwegian_org_number,
    IdentityResolver,
)
from signalpost.models import IdentityStatus


def test_normalize_org_number():
    assert normalize_org_number(" 923 609 016 ") == "923609016"
    assert normalize_org_number("NO-984.851.006MVA") == "984851006"
    assert normalize_org_number("") == ""
    assert normalize_org_number(None) == ""


def test_validate_valid_org_numbers():
    # 923609016 is valid Norwegian org nr
    is_valid, err = validate_norwegian_org_number("923609016")
    assert is_valid is True
    assert err is None

    # 984851006 (Brønnøysundregistrene) is valid
    is_valid, err = validate_norwegian_org_number("984851006")
    assert is_valid is True
    assert err is None


def test_validate_invalid_org_numbers():
    # Bad length
    is_valid, err = validate_norwegian_org_number("12345")
    assert is_valid is False
    assert "9 digits" in err

    # Non-digit
    is_valid, err = validate_norwegian_org_number("abcdefghi")
    assert is_valid is False

    # Checksum failure
    is_valid, err = validate_norwegian_org_number("123456789")
    assert is_valid is False
    assert "mismatch" in err.lower() or "checksum" in err.lower()


def test_identity_resolver_input():
    cleaned, status, err = IdentityResolver.resolve_input("923609016")
    assert cleaned == "923609016"
    assert status == IdentityStatus.UNVERIFIED
    assert err is None

    cleaned, status, err = IdentityResolver.resolve_input("000000000")
    assert status == IdentityStatus.INVALID
    assert err is not None


def test_verify_registry_match():
    # Exact match
    matched, status, err = IdentityResolver.verify_registry_match(
        "923609016",
        {"organisasjonsnummer": "923609016", "navn": "Test AS"}
    )
    assert matched is True
    assert status == IdentityStatus.VERIFIED

    # Mismatch org
    matched, status, err = IdentityResolver.verify_registry_match(
        "923609016",
        {"organisasjonsnummer": "984851006", "navn": "Other AS"}
    )
    assert matched is False
    assert status == IdentityStatus.MISMATCH

    # Missing name
    matched, status, err = IdentityResolver.verify_registry_match(
        "923609016",
        {"organisasjonsnummer": "923609016", "navn": None}
    )
    assert matched is False
    assert status == IdentityStatus.MISMATCH


def test_never_merge_companies_with_similar_names():
    # Two companies with identical name must be distinguished by organization number
    comp_a = {"organisasjonsnummer": "923609016", "navn": "Nordic Tech AS"}
    comp_b = {"organisasjonsnummer": "984851006", "navn": "Nordic Tech AS"}

    # Resolving for 923609016 must reject comp_b even though names match
    matched, status, _ = IdentityResolver.verify_registry_match("923609016", comp_b)
    assert matched is False
    assert status == IdentityStatus.MISMATCH
