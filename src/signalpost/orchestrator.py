"""Orchestrator: coordinates identity resolution, source adapters, validation, snapshots, and changes."""

import time
import logging
import uuid
from typing import Any, Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from signalpost.config import settings
from signalpost.models import (
    CompanyProfile,
    Fact,
    IdentityStatus,
    ResearchStatus,
    ResearchRun,
    utc_now_iso,
)
from signalpost.identity import IdentityResolver, validate_norwegian_org_number
from signalpost.database import db
from signalpost.request_budget import budget, BudgetExceededError
from signalpost.planner import ResearchPlanner
from signalpost.sources.brreg import BrregEnhetsregisterAdapter
from signalpost.sources.financial import BrregRegnskapAdapter
from signalpost.sources.website import CompanyWebsiteAdapter
from signalpost.validation import EvidenceValidator
from signalpost.profile_builder import ProfileBuilder
from signalpost.snapshots import SnapshotManager
from signalpost.change_detection import ChangeDetectionEngine
from signalpost.explanations import ExplanationGenerator

logger = logging.getLogger(__name__)


class ResearchAgent:
    """The Signalpost research agent."""

    def __init__(self, database=None):
        self.db = database or db
        self.brreg_adapter = BrregEnhetsregisterAdapter()
        self.financial_adapter = BrregRegnskapAdapter()
        self.website_adapter = CompanyWebsiteAdapter()

    def research_company(
        self,
        raw_org: str,
        force_refresh: bool = False
    ) -> CompanyProfile:
        """
        Execute full evidence-first research for a single Norwegian organization number.
        Always returns exactly one CompanyProfile, even if the identifier is invalid or not found.
        """
        now = utc_now_iso()
        cleaned_org, identity_status, error_msg = IdentityResolver.resolve_input(raw_org)

        # 1. Handle invalid format or checksum
        if identity_status == IdentityStatus.INVALID:
            failed_profile = ProfileBuilder.build_profile(
                org_nr=cleaned_org or str(raw_org),
                facts=[],
                financial_statements=[],
                identity_status=IdentityStatus.INVALID,
                errors=[error_msg or "Invalid organization number format or checksum"],
            )
            failed_profile.research_status = ResearchStatus.FAILED
            failed_profile.explanations = ExplanationGenerator.generate_explanations(failed_profile, [])
            return failed_profile

        # 2. Check existing profile & plan
        existing_profile = self.db.get_company(cleaned_org) if not force_refresh else None
        plan = ResearchPlanner.create_plan(cleaned_org, existing_profile, force_refresh)

        facts: List[Fact] = list(existing_profile.facts) if existing_profile else []
        financial_statements = list(existing_profile.financials) if existing_profile else []
        errors: List[str] = []

        # 3. Query Official Registry (Enhetsregisteret)
        if plan.query_registry and settings.enable_brreg_registry:
            try:
                brreg_facts, source_rec = self.brreg_adapter.fetch_and_extract(cleaned_org)
                if source_rec:
                    self.db.insert_source(source_rec)

                if brreg_facts:
                    # Filter out old brreg facts if refreshing
                    facts = [f for f in facts if f.source_name != self.brreg_adapter.source_name] + brreg_facts
                elif source_rec and source_rec.http_status == 404:
                    errors.append(f"Entity not found in official Enhetsregisteret (404)")
            except BudgetExceededError:
                raise
            except Exception as e:
                logger.error(f"Error querying registry for {cleaned_org}: {e}")
                errors.append(f"Registry retrieval failed: {str(e)}")

        # Check if we got an official company name
        comp_name = None
        for f in facts:
            if f.field_name == "official_name":
                comp_name = str(f.value)
                break

        if not comp_name:
            # Cannot find company in official register
            not_found_profile = ProfileBuilder.build_profile(
                org_nr=cleaned_org,
                facts=facts,
                financial_statements=[],
                identity_status=IdentityStatus.UNVERIFIED,
                errors=errors or ["Company not registered in Brønnøysund Register Centre"],
            )
            not_found_profile.research_status = ResearchStatus.NOT_FOUND
            not_found_profile.explanations = ExplanationGenerator.generate_explanations(not_found_profile, [])
            # Store in DB
            self.db.upsert_company(not_found_profile)
            return not_found_profile

        # 4. Query Regnskapsregisteret (Official Financial Accounts)
        if plan.query_financials and settings.enable_brreg_financial:
            try:
                stmts, fin_facts, fin_source_rec = self.financial_adapter.fetch_and_extract_statements(cleaned_org)
                if fin_source_rec:
                    self.db.insert_source(fin_source_rec)
                if stmts:
                    financial_statements = stmts
                    # Replace previous financial facts
                    facts = [f for f in facts if f.source_name != self.financial_adapter.source_name] + fin_facts
            except BudgetExceededError:
                raise
            except Exception as e:
                logger.error(f"Error querying financial accounts for {cleaned_org}: {e}")
                errors.append(f"Financial accounts retrieval failed: {str(e)}")

        # 5. Query Company Website (if official website is registered)
        website_url = None
        for f in facts:
            if f.field_name == "website" and f.value:
                website_url = str(f.value)
                break

        if plan.query_website and settings.enable_website_discovery and website_url:
            try:
                web_facts, web_src_rec, _ = self.website_adapter.fetch_website_facts(
                    org_nr=cleaned_org,
                    website_url=website_url,
                    company_name=comp_name,
                )
                if web_src_rec:
                    self.db.insert_source(web_src_rec)
                if web_facts:
                    facts = [f for f in facts if f.source_name != self.website_adapter.source_name] + web_facts
            except BudgetExceededError:
                raise
            except Exception as e:
                logger.warning(f"Website analysis non-fatal error for {cleaned_org} ({website_url}): {e}")
                # Optional source: graceful degradation

        # 6. Validate Evidence and Facts
        validation_report = EvidenceValidator.validate_facts_batch(facts, cleaned_org)
        verified_facts = validation_report.validated_facts
        if validation_report.conflicts:
            errors.extend(validation_report.conflicts)

        # 7. Construct Normalized CompanyProfile
        current_profile = ProfileBuilder.build_profile(
            org_nr=cleaned_org,
            facts=verified_facts,
            financial_statements=financial_statements,
            identity_status=IdentityStatus.VERIFIED,
            errors=errors,
        )

        # 8. Create Snapshot & Detect Historical Changes
        previous_snapshot = self.db.get_latest_snapshot(cleaned_org)
        new_snapshot = SnapshotManager.create_snapshot(current_profile)

        changes = []
        if previous_snapshot:
            # Detect changes between previous snapshot and current profile
            changes = ChangeDetectionEngine.detect_changes(
                current_profile=current_profile,
                previous_snapshot=previous_snapshot,
            )

        # 9. Generate Grounded Explanations
        current_profile.changes = changes
        current_profile.explanations = ExplanationGenerator.generate_explanations(
            current_profile, changes
        )

        # 10. Persist to SQLite Database
        self.db.upsert_company(current_profile)
        self.db.insert_facts(verified_facts)
        new_snapshot_id = self.db.insert_snapshot(new_snapshot)

        # Assign snapshot IDs to changes and persist
        if changes:
            for ch in changes:
                ch.current_snapshot_id = new_snapshot_id
            self.db.insert_changes(changes)

        return current_profile

    def research_batch(
        self,
        raw_orgs: List[str],
        max_workers: int = 5,
        force_refresh: bool = False
    ) -> Tuple[List[CompanyProfile], ResearchRun]:
        """
        Process a batch of organization numbers.
        Guarantees:
        - Preserves original input order.
        - Deduplicates inputs while producing results for each unique input.
        - Tracks run metrics, budgets, and produces a complete ResearchRun audit record.
        - Never throws: captures exceptions per company.
        """
        run_id = str(uuid.uuid4())
        started_at = utc_now_iso()
        run = ResearchRun(
            run_id=run_id,
            started_at=started_at,
            companies_requested=len(raw_orgs),
            companies_completed=0,
            requests_used=0,
            external_api_cost_usd=0.0,
            run_status="running",
        )

        # Deduplicate while preserving order
        seen = set()
        unique_orgs = []
        for o in raw_orgs:
            s = str(o).strip()
            if s and s not in seen:
                seen.add(s)
                unique_orgs.append(s)

        results_map: Dict[str, CompanyProfile] = {}
        errors_summary: Dict[str, int] = {}

        logger.info(f"Starting batch run {run_id} for {len(unique_orgs)} unique organizations.")

        # If batch is small or 1, process sequentially; else bounded ThreadPoolExecutor
        if len(unique_orgs) == 1 or max_workers <= 1:
            for org in unique_orgs:
                try:
                    profile = self.research_company(org, force_refresh=force_refresh)
                    results_map[org] = profile
                except BudgetExceededError as be:
                    logger.error(f"Budget exceeded during batch: {be}")
                    errors_summary["budget_exceeded"] = errors_summary.get("budget_exceeded", 0) + 1
                    results_map[org] = ProfileBuilder.build_profile(
                        org_nr=org,
                        facts=[],
                        identity_status=IdentityStatus.UNVERIFIED,
                        errors=[str(be)]
                    )
                    break
                except Exception as e:
                    logger.error(f"Unexpected error for {org}: {e}")
                    errors_summary["exception"] = errors_summary.get("exception", 0) + 1
                    results_map[org] = ProfileBuilder.build_profile(
                        org_nr=org,
                        facts=[],
                        identity_status=IdentityStatus.UNVERIFIED,
                        errors=[f"Agent error: {str(e)}"]
                    )
        else:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_org = {
                    executor.submit(self.research_company, org, force_refresh): org
                    for org in unique_orgs
                }
                for future in as_completed(future_to_org):
                    org = future_to_org[future]
                    try:
                        profile = future.result()
                        results_map[org] = profile
                    except BudgetExceededError as be:
                        logger.error(f"Budget exceeded for {org}: {be}")
                        errors_summary["budget_exceeded"] = errors_summary.get("budget_exceeded", 0) + 1
                        results_map[org] = ProfileBuilder.build_profile(
                            org_nr=org,
                            facts=[],
                            identity_status=IdentityStatus.UNVERIFIED,
                            errors=[str(be)]
                        )
                    except Exception as e:
                        logger.error(f"Unexpected error for {org}: {e}")
                        errors_summary["exception"] = errors_summary.get("exception", 0) + 1
                        results_map[org] = ProfileBuilder.build_profile(
                            org_nr=org,
                            facts=[],
                            identity_status=IdentityStatus.UNVERIFIED,
                            errors=[f"Agent error: {str(e)}"]
                        )

        # Assemble results in exact original order of raw_orgs
        ordered_results: List[CompanyProfile] = []
        for o in raw_orgs:
            s = str(o).strip()
            if s in results_map:
                ordered_results.append(results_map[s])

        # Complete run record
        b_summary = budget.get_summary()
        run.finished_at = utc_now_iso()
        run.companies_completed = len(results_map)
        run.requests_used = b_summary["total_outbound_requests"]
        run.external_api_cost_usd = b_summary["total_external_cost_usd"]
        run.run_status = "completed" if "budget_exceeded" not in errors_summary else "aborted_budget"
        run.errors_summary = errors_summary

        self.db.record_run(run)
        return ordered_results, run
