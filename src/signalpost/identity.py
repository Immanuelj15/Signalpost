"""Company Identity Resolver and Norwegian Organization Number Validator."""

import re
from typing import Optional, Tuple
from signalpost.models import IdentityStatus


class InvalidOrganizationNumberError(ValueError):
    """Raised when an organization number fails format or checksum checks."""
    pass


def normalize_org_number(raw: str) -> str:
    """Normalize organization number string by stripping whitespace and non-digits."""
    if not raw:
        return ""
    # Strip spaces, hyphens, periods, etc.
    cleaned = re.sub(r"[^\d]", "", str(raw).strip())
    return cleaned


def validate_norwegian_org_number(org_nr: str) -> Tuple[bool, Optional[str]]:
    """
    Validate Norwegian organization number (9 digits with Modulo 11 checksum).
    
    Weights: 3, 2, 7, 6, 5, 4, 3, 2
    Returns (is_valid, error_message).
    """
    cleaned = normalize_org_number(org_nr)
    if not cleaned:
        return False, "Empty or missing organization number"
    if cleaned.startswith("0"):
        return False, f"Norwegian organization numbers cannot start with 0 ('{cleaned}')"
    if len(cleaned) != 9:
        return False, f"Expected exactly 9 digits, got {len(cleaned)} ('{org_nr}')"
    if not cleaned.isdigit():
        return False, f"Contains non-digit characters ('{org_nr}')"

    weights = [3, 2, 7, 6, 5, 4, 3, 2]
    digits = [int(c) for c in cleaned]
    weighted_sum = sum(w * d for w, d in zip(weights, digits[:8]))
    remainder = weighted_sum % 11

    if remainder == 0:
        expected_control = 0
    elif remainder == 1:
        # Remainder 1 cannot yield a single check digit (11 - 1 = 10)
        return False, f"Invalid Modulo 11 checksum for '{cleaned}' (remainder 1 produces 10)"
    else:
        expected_control = 11 - remainder

    actual_control = digits[8]
    if expected_control != actual_control:
        return False, (
            f"Checksum mismatch for '{cleaned}': expected check digit {expected_control}, "
            f"got {actual_control}"
        )

    return True, None


class IdentityResolver:
    """Resolves and validates Norwegian company identities."""

    @staticmethod
    def resolve_input(raw_org: str) -> Tuple[str, IdentityStatus, Optional[str]]:
        """
        Validate and normalize input identifier.
        Returns: (normalized_org, status, error_reason)
        """
        cleaned = normalize_org_number(raw_org)
        is_valid, error = validate_norwegian_org_number(cleaned)
        if not is_valid:
            return cleaned or str(raw_org), IdentityStatus.INVALID, error
        return cleaned, IdentityStatus.UNVERIFIED, None

    @staticmethod
    def verify_registry_match(
        requested_org: str,
        registry_data: dict
    ) -> Tuple[bool, IdentityStatus, Optional[str]]:
        """
        Verify that data returned from the official registry corresponds exactly to the requested company.
        Never match solely on name similarity; organization number is primary key.
        """
        returned_org = str(registry_data.get("organisasjonsnummer", "")).strip()
        if not returned_org:
            return False, IdentityStatus.MISMATCH, "Registry payload missing organisasjonsnummer"

        if returned_org != requested_org:
            return False, IdentityStatus.MISMATCH, (
                f"Identity conflict: requested '{requested_org}' but registry returned '{returned_org}'"
            )

        name = registry_data.get("navn")
        if not name:
            return False, IdentityStatus.MISMATCH, "Registry payload missing official company name"

        return True, IdentityStatus.VERIFIED, None
