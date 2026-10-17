"""Core data models and schema definitions for Signalpost."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


def utc_now_iso() -> str:
    """Return current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


class VerificationStatus(str, Enum):
    VERIFIED = "verified"
    DERIVED = "derived"
    UNVERIFIED = "unverified"
    UNAVAILABLE = "unavailable"


class ExtractionMethod(str, Enum):
    DETERMINISTIC_API = "deterministic_api"
    RULE_BASED_HTML = "rule_based_html"
    DERIVED = "derived"
    OPTIONAL_LLM = "optional_llm"


class IdentityStatus(str, Enum):
    VERIFIED = "verified"
    MISMATCH = "mismatch"
    UNVERIFIED = "unverified"
    INVALID = "invalid"


class ResearchStatus(str, Enum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    FAILED = "failed"
    NOT_FOUND = "not_found"


class ChangeType(str, Enum):
    GENUINE_COMPANY_CHANGE = "genuine_company_change"
    EXTRACTION_CORRECTION = "extraction_correction"
    SOURCE_CORRECTION = "source_correction"
    INITIAL_DISCOVERY = "initial_discovery"


class Fact(BaseModel):
    """An individual atomic fact extracted from an attributable source."""
    fact_id: Optional[str] = None
    organization_number: str
    field_name: str
    value: Any
    data_type: str = "string"
    source_name: str
    source_url: str
    retrieved_at: str = Field(default_factory=utc_now_iso)
    published_at: Optional[str] = None
    reporting_period: Optional[str] = None
    evidence_excerpt: Optional[str] = None
    verification_status: VerificationStatus = VerificationStatus.VERIFIED
    confidence: float = 1.0
    extraction_method: ExtractionMethod = ExtractionMethod.DETERMINISTIC_API
    content_hash: Optional[str] = None


class SourceRecord(BaseModel):
    """Record of an external retrieval action."""
    source_id: Optional[str] = None
    source_name: str
    source_url: str
    source_type: str = "api"
    retrieved_at: str = Field(default_factory=utc_now_iso)
    http_status: Optional[int] = None
    content_hash: Optional[str] = None
    extraction_status: str = "success"
    error_category: Optional[str] = None


class ChangeRecord(BaseModel):
    """A detected difference between historical snapshot and current profile."""
    change_id: Optional[str] = None
    organization_number: str
    field_name: str
    previous_value: Any = None
    new_value: Any = None
    previous_source: Optional[str] = None
    new_source: Optional[str] = None
    detected_at: str = Field(default_factory=utc_now_iso)
    previous_snapshot_id: Optional[str] = None
    current_snapshot_id: Optional[str] = None
    evidence_reference: Optional[str] = None
    change_type: ChangeType = ChangeType.GENUINE_COMPANY_CHANGE
    confidence: float = 1.0
    review_status: str = "automatic_verified"


class SnapshotRecord(BaseModel):
    """Point-in-time snapshot of a company's normalized profile."""
    snapshot_id: Optional[str] = None
    organization_number: str
    created_at: str = Field(default_factory=utc_now_iso)
    normalized_profile_json: str
    profile_hash: str


class Address(BaseModel):
    address: List[str] = Field(default_factory=list)
    postal_code: Optional[str] = None
    city: Optional[str] = None
    municipality: Optional[str] = None
    municipality_number: Optional[str] = None
    country: Optional[str] = "Norge"
    country_code: Optional[str] = "NO"


class FinancialStatement(BaseModel):
    """Official annual financial figures with attributable reporting period."""
    reporting_period: str  # e.g., "2023-01-01 to 2023-12-31"
    year: int
    currency: str = "NOK"
    unit: str = "exact_amount"
    statement_type: str = "SELSKAP"  # SELSKAP or KONSERN
    accounting_rules: Optional[str] = None  # e.g., IFRS or smaaForetak
    
    # Financial metrics clearly distinguished
    total_revenue: Optional[float] = None
    sales_revenue: Optional[float] = None
    operating_profit: Optional[float] = None  # EBIT (driftsresultat)
    profit_before_tax: Optional[float] = None  # ordinaertResultatFoerSkattekostnad
    net_profit: Optional[float] = None  # aarsresultat
    total_assets: Optional[float] = None  # sumEiendeler
    total_equity: Optional[float] = None  # sumEgenkapital
    total_debt: Optional[float] = None  # sumGjeld
    
    source_url: str
    filing_id: Optional[int] = None
    journal_number: Optional[str] = None


class CompanyCoreData(BaseModel):
    """Core company metadata."""
    official_name: Optional[str] = None
    status: Optional[str] = "active"
    organization_type: Optional[str] = None
    organization_type_description: Optional[str] = None
    registration_date: Optional[str] = None
    incorporation_date: Optional[str] = None
    business_address: Optional[Address] = None
    postal_address: Optional[Address] = None
    industry_codes: List[Dict[str, str]] = Field(default_factory=list)
    business_activity: List[str] = Field(default_factory=list)
    employees: Optional[int] = None
    website: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    parent_organization: Optional[str] = None
    is_in_liquidation: bool = False
    is_in_bankruptcy: bool = False
    is_deleted: bool = False
    deleted_date: Optional[str] = None
    products_and_services: List[str] = Field(default_factory=list)
    business_description: Optional[str] = None


class CompanyProfile(BaseModel):
    """Normalized company intelligence profile meeting challenge schema."""
    schema_version: str = "1.0"
    organization_number: str
    company: CompanyCoreData = Field(default_factory=CompanyCoreData)
    financials: Optional[List[FinancialStatement]] = Field(default_factory=list)
    facts: List[Fact] = Field(default_factory=list)
    changes: List[ChangeRecord] = Field(default_factory=list)
    missing_fields: List[str] = Field(default_factory=list)
    identity_status: IdentityStatus = IdentityStatus.UNVERIFIED
    research_status: ResearchStatus = ResearchStatus.PARTIAL
    last_researched_at: Optional[str] = None
    errors: List[str] = Field(default_factory=list)
    explanations: List[str] = Field(default_factory=list)


class ResearchRun(BaseModel):
    """Execution run summary for audit and evaluation."""
    run_id: str
    started_at: str = Field(default_factory=utc_now_iso)
    finished_at: Optional[str] = None
    companies_requested: int = 0
    companies_completed: int = 0
    requests_used: int = 0
    external_api_cost_usd: float = 0.0
    run_status: str = "in_progress"
    errors_summary: Dict[str, int] = Field(default_factory=dict)
