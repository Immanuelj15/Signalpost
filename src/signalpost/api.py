"""FastAPI REST API service for Signalpost."""

from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from signalpost.database import db
from signalpost.orchestrator import ResearchAgent
from signalpost.models import CompanyProfile, ChangeRecord
from signalpost.request_budget import budget

app = FastAPI(
    title="Signalpost API",
    description="Evidence-First Norwegian Company Intelligence Agent REST Service",
    version="1.0.0",
)


class BatchRequest(BaseModel):
    organization_numbers: List[str]
    force_refresh: bool = False
    concurrency: int = 5


@app.on_event("startup")
def on_startup():
    db.init_db()


@app.get("/health")
def health():
    """Health check and operational budget status."""
    return {
        "status": "healthy",
        "service": "signalpost",
        "budget": budget.get_summary(),
        "total_stored_companies": db.count_companies(),
    }


@app.get("/company/{orgnr}", response_model=CompanyProfile)
def get_company(orgnr: str):
    """Retrieve stored company profile from database."""
    profile = db.get_company(orgnr)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Company {orgnr} not found in database")
    return profile


@app.post("/research/{orgnr}", response_model=CompanyProfile)
def research_company(orgnr: str, refresh: bool = Query(False)):
    """Trigger real-time research for a Norwegian organization number."""
    agent = ResearchAgent(database=db)
    profile = agent.research_company(orgnr, force_refresh=refresh)
    return profile


@app.post("/batch")
def research_batch(req: BatchRequest):
    """Trigger batch research across multiple organization numbers."""
    agent = ResearchAgent(database=db)
    profiles, run = agent.research_batch(
        raw_orgs=req.organization_numbers,
        max_workers=req.concurrency,
        force_refresh=req.force_refresh,
    )
    return {
        "run": run.model_dump(),
        "profiles": [p.model_dump() for p in profiles],
    }


@app.get("/history/{orgnr}", response_model=List[ChangeRecord])
def get_history(orgnr: str):
    """Retrieve historical detected changes for an organization."""
    return db.get_changes_for_org(orgnr)


@app.get("/stats")
def get_stats():
    """Retrieve system operational statistics."""
    return {
        "companies_in_database": db.count_companies(),
        "budget": budget.get_summary(),
    }
