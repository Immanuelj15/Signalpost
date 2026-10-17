"""Explanation generator: produces concise, evidence-grounded explanations."""

from typing import List
from signalpost.models import CompanyProfile, ChangeRecord


class ExplanationGenerator:
    """Generates audit-ready, plain-text explanations grounded in verified facts and changes."""

    @staticmethod
    def generate_explanations(profile: CompanyProfile, changes: List[ChangeRecord]) -> List[str]:
        """Produce grounded natural language explanations for profile state and changes."""
        explanations = []

        # 1. Base identity and registration explanation
        comp = profile.company
        if comp.official_name:
            reg_text = f"registered on {comp.registration_date}" if comp.registration_date else "registered in Norway"
            explanations.append(
                f"Company '{comp.official_name}' ({profile.organization_number}) is an active/recorded "
                f"{comp.organization_type or 'entity'} {reg_text}, verified via the Brønnøysund Enhetsregisteret."
            )
        elif profile.identity_status == "invalid":
            explanations.append(
                f"Organization number '{profile.organization_number}' failed Modulo 11 checksum verification."
            )
        elif profile.research_status == "not_found":
            explanations.append(
                f"No entity record was found for organization number '{profile.organization_number}' "
                f"in the official Brønnøysund Register Centre."
            )

        # 2. Financial filings explanation
        if profile.financials:
            latest = profile.financials[0]
            rev_txt = f"{latest.total_revenue:,.0f} {latest.currency}" if latest.total_revenue is not None else "undisclosed revenue"
            profit_txt = f"{latest.net_profit:,.0f} {latest.currency}" if latest.net_profit is not None else "undisclosed net profit"
            explanations.append(
                f"Latest audited accounts for period '{latest.reporting_period}' indicate total revenue of {rev_txt} "
                f"and net annual profit of {profit_txt}, sourced directly from Regnskapsregisteret."
            )
        elif comp.official_name:
            explanations.append(
                "No annual financial accounts have been filed with or published by Regnskapsregisteret for this entity."
            )

        # 3. Change explanations
        for ch in changes:
            if ch.field_name == "official_name":
                explanations.append(
                    f"Official company name updated from '{ch.previous_value}' to '{ch.new_value}', "
                    f"verified via registry update retrieved at {ch.detected_at}."
                )
            elif ch.field_name == "business_address":
                explanations.append(
                    f"Business address changed. Current registered address is verified by official Brreg records."
                )
            elif ch.field_name == "financials_new_period":
                explanations.append(
                    f"A new annual financial filing was recorded: {ch.new_value}."
                )
            elif ch.field_name == "status":
                explanations.append(
                    f"Company status transitioned from '{ch.previous_value}' to '{ch.new_value}'."
                )
            else:
                explanations.append(
                    f"Field '{ch.field_name}' updated from '{ch.previous_value}' to '{ch.new_value}'."
                )

        # 4. Error / conflict explanations
        for err in profile.errors:
            explanations.append(f"Attention: {err}")

        return explanations
