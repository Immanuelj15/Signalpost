"""Evidence, identity, and claim validation engine."""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from signalpost.models import Fact, VerificationStatus

logger = logging.getLogger(__name__)


class ValidationReport:
    """Report detailing validity of extracted facts."""

    def __init__(self):
        self.validated_facts: List[Fact] = []
        self.rejected_facts: List[Tuple[Fact, str]] = []
        self.conflicts: List[str] = []

    @property
    def is_valid(self) -> bool:
        return len(self.rejected_facts) == 0 and len(self.conflicts) == 0


class EvidenceValidator:
    """Validates factual claims against provenance, identity, and source evidence."""

    @staticmethod
    def validate_fact(fact: Fact, expected_org_nr: str) -> Tuple[bool, Optional[str]]:
        """
        Validate an individual fact against standards:
        - Organization number match
        - Valid source URL
        - Non-empty value
        - Evidence excerpt present
        - Data type consistency
        """
        if fact.organization_number != expected_org_nr:
            return False, f"Org number mismatch: fact has '{fact.organization_number}', expected '{expected_org_nr}'"

        if not fact.source_url:
            return False, f"Missing source URL for fact '{fact.field_name}'"

        if not fact.source_url.startswith(("http://", "https://")):
            return False, f"Invalid source URL protocol: '{fact.source_url}'"

        if not fact.evidence_excerpt or not fact.evidence_excerpt.strip():
            return False, f"Missing evidence excerpt for fact '{fact.field_name}'"

        if fact.value is None:
            return False, f"Fact value is None for '{fact.field_name}'"

        # Validate currency amounts
        if fact.data_type == "currency_amount":
            if not isinstance(fact.value, (int, float)):
                return False, f"Financial metric '{fact.field_name}' value must be numeric, got {type(fact.value)}"
            if not fact.reporting_period:
                return False, f"Financial metric '{fact.field_name}' missing reporting_period"

        # Validate date format (YYYY-MM-DD)
        if fact.data_type == "date":
            val_str = str(fact.value).strip()
            if not re.match(r"^\d{4}-\d{2}-\d{2}", val_str):
                return False, f"Invalid date format for '{fact.field_name}': '{val_str}'"

        return True, None

    @classmethod
    def validate_facts_batch(
        cls,
        facts: List[Fact],
        expected_org_nr: str
    ) -> ValidationReport:
        """Validate a collection of facts for a company, checking for internal conflicts."""
        report = ValidationReport()
        values_by_field: Dict[str, List[Fact]] = {}

        for fact in facts:
            is_valid, reason = cls.validate_fact(fact, expected_org_nr)
            if not is_valid:
                report.rejected_facts.append((fact, reason or "unknown validation failure"))
                logger.warning(f"Rejected fact {fact.field_name} for org {expected_org_nr}: {reason}")
            else:
                report.validated_facts.append(fact)
                values_by_field.setdefault(fact.field_name, []).append(fact)

        # Check for contradictions across sources for critical fields
        critical_fields = ["official_name", "organization_type", "status"]
        for field in critical_fields:
            if field in values_by_field and len(values_by_field[field]) > 1:
                vals = set(str(f.value).strip().lower() for f in values_by_field[field])
                if len(vals) > 1:
                    sources = [f"{f.source_name} ({f.value})" for f in values_by_field[field]]
                    conflict_msg = f"Contradiction detected for field '{field}': {', '.join(sources)}"
                    report.conflicts.append(conflict_msg)
                    logger.warning(conflict_msg)

        return report
