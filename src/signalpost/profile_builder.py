"""Profile builder: aggregates verified facts and constructs normalized CompanyProfile."""

from typing import Any, Dict, List, Optional
from signalpost.models import (
    CompanyProfile,
    CompanyCoreData,
    FinancialStatement,
    Address,
    Fact,
    IdentityStatus,
    ResearchStatus,
    utc_now_iso,
)


CORE_PROFILE_FIELDS = [
    "official_name",
    "organization_type",
    "status",
    "registration_date",
    "business_address",
    "industry_codes",
    "business_activity",
    "website",
]


class ProfileBuilder:
    """Builds a structured CompanyProfile from verified atomic facts and financial statements."""

    @staticmethod
    def build_profile(
        org_nr: str,
        facts: List[Fact],
        financial_statements: Optional[List[FinancialStatement]] = None,
        identity_status: IdentityStatus = IdentityStatus.VERIFIED,
        errors: Optional[List[str]] = None,
        explanations: Optional[List[str]] = None,
    ) -> CompanyProfile:
        """Construct normalized CompanyProfile from facts."""
        now = utc_now_iso()
        company_data = CompanyCoreData()
        facts_by_field: Dict[str, Any] = {}

        for fact in facts:
            facts_by_field[fact.field_name] = fact.value

        # Populate company core data
        if "official_name" in facts_by_field:
            company_data.official_name = facts_by_field["official_name"]
        if "organization_type" in facts_by_field:
            company_data.organization_type = facts_by_field["organization_type"]
        if "organization_type_description" in facts_by_field:
            company_data.organization_type_description = facts_by_field["organization_type_description"]
        if "status" in facts_by_field:
            company_data.status = facts_by_field["status"]
        if "registration_date" in facts_by_field:
            company_data.registration_date = str(facts_by_field["registration_date"])
        if "incorporation_date" in facts_by_field:
            company_data.incorporation_date = str(facts_by_field["incorporation_date"])
        if "employees" in facts_by_field:
            company_data.employees = int(facts_by_field["employees"])
        if "website" in facts_by_field:
            company_data.website = str(facts_by_field["website"])
        if "contact_email" in facts_by_field:
            company_data.contact_email = str(facts_by_field["contact_email"])
        if "contact_phone" in facts_by_field:
            company_data.contact_phone = str(facts_by_field["contact_phone"])
        if "parent_organization" in facts_by_field:
            company_data.parent_organization = str(facts_by_field["parent_organization"])
        if "business_description" in facts_by_field:
            company_data.business_description = str(facts_by_field["business_description"])
        if "products_and_services" in facts_by_field:
            company_data.products_and_services = list(facts_by_field["products_and_services"])
        if "business_activity" in facts_by_field:
            company_data.business_activity = list(facts_by_field["business_activity"])
        if "industry_codes" in facts_by_field:
            company_data.industry_codes = list(facts_by_field["industry_codes"])

        # Addresses
        if "business_address" in facts_by_field and isinstance(facts_by_field["business_address"], dict):
            company_data.business_address = Address(**facts_by_field["business_address"])
        if "postal_address" in facts_by_field and isinstance(facts_by_field["postal_address"], dict):
            company_data.postal_address = Address(**facts_by_field["postal_address"])

        # Booleans
        if "is_in_bankruptcy" in facts_by_field:
            company_data.is_in_bankruptcy = bool(facts_by_field["is_in_bankruptcy"])
        if "is_in_liquidation" in facts_by_field:
            company_data.is_in_liquidation = bool(facts_by_field["is_in_liquidation"])
        if "is_deleted" in facts_by_field:
            company_data.is_deleted = bool(facts_by_field["is_deleted"])
        if "deleted_date" in facts_by_field:
            company_data.deleted_date = str(facts_by_field["deleted_date"])

        # Determine missing fields
        missing = []
        for field in CORE_PROFILE_FIELDS:
            if field not in facts_by_field or facts_by_field[field] is None:
                missing.append(field)

        # Determine research status
        if identity_status in (IdentityStatus.INVALID, IdentityStatus.MISMATCH):
            res_status = ResearchStatus.FAILED
        elif not company_data.official_name:
            res_status = ResearchStatus.NOT_FOUND
        elif len(missing) == 0 and financial_statements:
            res_status = ResearchStatus.COMPLETE
        else:
            res_status = ResearchStatus.PARTIAL

        return CompanyProfile(
            schema_version="1.0",
            organization_number=org_nr,
            company=company_data,
            financials=financial_statements or [],
            facts=facts,
            changes=[],
            missing_fields=missing,
            identity_status=identity_status,
            research_status=res_status,
            last_researched_at=now,
            errors=errors or [],
            explanations=explanations or [],
        )
