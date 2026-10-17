"""Research planner: plans source queries deterministically based on existing profile state."""

from dataclasses import dataclass
from typing import List, Optional
from signalpost.models import CompanyProfile


@dataclass
class ResearchPlan:
    """Bounded, deterministic plan of sources to consult."""
    organization_number: str
    query_registry: bool = True
    query_financials: bool = True
    query_website: bool = True
    forced_refresh: bool = False
    reasons: List[str] = None


class ResearchPlanner:
    """Plans source retrieval to avoid redundant network calls."""

    @staticmethod
    def create_plan(
        org_nr: str,
        existing_profile: Optional[CompanyProfile] = None,
        force_refresh: bool = False
    ) -> ResearchPlan:
        """Construct bounded research plan."""
        reasons = []

        if force_refresh or existing_profile is None:
            return ResearchPlan(
                organization_number=org_nr,
                query_registry=True,
                query_financials=True,
                query_website=True,
                forced_refresh=force_refresh,
                reasons=["Initial research" if not existing_profile else "Forced refresh requested"]
            )

        # Stored profile exists: inspect missing or refreshable areas
        query_registry = False
        query_financials = False
        query_website = False

        # If name or core fields are missing, re-query registry
        if not existing_profile.company.official_name:
            query_registry = True
            reasons.append("Official company name missing")

        # If financial accounts are absent
        if not existing_profile.financials:
            query_financials = True
            reasons.append("No financial accounts recorded")

        # If website was found in registry but website facts have not been extracted
        has_website_url = bool(existing_profile.company.website)
        has_website_facts = any(f.source_name == "company_website" for f in existing_profile.facts)
        if has_website_url and not has_website_facts:
            query_website = True
            reasons.append("Registered website has not yet been analyzed")

        return ResearchPlan(
            organization_number=org_nr,
            query_registry=query_registry,
            query_financials=query_financials,
            query_website=query_website,
            forced_refresh=False,
            reasons=reasons or ["Profile is already fresh"]
        )
