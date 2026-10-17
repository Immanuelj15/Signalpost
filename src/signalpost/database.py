"""Database layer for Signalpost utilizing SQLite."""

import sqlite3
import json
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional
from signalpost.config import settings
from signalpost.models import (
    CompanyProfile,
    Fact,
    SourceRecord,
    SnapshotRecord,
    ChangeRecord,
    ResearchRun,
    utc_now_iso,
)


class Database:
    """SQLite database manager with parameterized queries and transaction safety."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            self.db_path = settings.get_db_path()
        else:
            self.db_path = Path(db_path)
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """Create a connection with row factory and WAL mode."""
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def init_db(self):
        """Initialize the database schema if tables do not exist."""
        with self.get_connection() as conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS schema_versions (
                version INTEGER PRIMARY KEY,
                applied_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS companies (
                organization_number TEXT PRIMARY KEY,
                official_name TEXT,
                organization_type TEXT,
                status TEXT,
                canonical_website TEXT,
                first_seen_at TEXT NOT NULL,
                last_researched_at TEXT,
                last_successful_research_at TEXT,
                profile_json TEXT,
                profile_schema_version TEXT DEFAULT '1.0'
            );
            CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(official_name);
            CREATE INDEX IF NOT EXISTS idx_companies_status ON companies(status);

            CREATE TABLE IF NOT EXISTS sources (
                source_id TEXT PRIMARY KEY,
                source_name TEXT NOT NULL,
                source_url TEXT NOT NULL,
                source_type TEXT NOT NULL,
                retrieved_at TEXT NOT NULL,
                http_status INTEGER,
                content_hash TEXT,
                extraction_status TEXT NOT NULL,
                error_category TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_sources_url ON sources(source_url);

            CREATE TABLE IF NOT EXISTS facts (
                fact_id TEXT PRIMARY KEY,
                organization_number TEXT NOT NULL,
                field_name TEXT NOT NULL,
                value_json TEXT,
                source_id TEXT,
                source_url TEXT NOT NULL,
                retrieved_at TEXT NOT NULL,
                published_at TEXT,
                reporting_period TEXT,
                evidence_excerpt TEXT,
                verification_status TEXT NOT NULL,
                confidence REAL NOT NULL,
                extraction_method TEXT NOT NULL,
                content_hash TEXT,
                FOREIGN KEY (organization_number) REFERENCES companies(organization_number) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_facts_org_field ON facts(organization_number, field_name);
            CREATE INDEX IF NOT EXISTS idx_facts_hash ON facts(content_hash);

            CREATE TABLE IF NOT EXISTS snapshots (
                snapshot_id TEXT PRIMARY KEY,
                organization_number TEXT NOT NULL,
                created_at TEXT NOT NULL,
                normalized_profile_json TEXT NOT NULL,
                profile_hash TEXT NOT NULL,
                FOREIGN KEY (organization_number) REFERENCES companies(organization_number) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_snapshots_org_time ON snapshots(organization_number, created_at DESC);

            CREATE TABLE IF NOT EXISTS changes (
                change_id TEXT PRIMARY KEY,
                organization_number TEXT NOT NULL,
                field_name TEXT NOT NULL,
                previous_value_json TEXT,
                new_value_json TEXT,
                previous_source TEXT,
                new_source TEXT,
                detected_at TEXT NOT NULL,
                previous_snapshot_id TEXT,
                current_snapshot_id TEXT,
                evidence_reference TEXT,
                change_type TEXT NOT NULL,
                confidence REAL NOT NULL,
                review_status TEXT NOT NULL,
                FOREIGN KEY (organization_number) REFERENCES companies(organization_number) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_changes_org ON changes(organization_number, detected_at DESC);

            CREATE TABLE IF NOT EXISTS research_runs (
                run_id TEXT PRIMARY KEY,
                started_at TEXT NOT NULL,
                finished_at TEXT,
                companies_requested INTEGER NOT NULL,
                companies_completed INTEGER NOT NULL,
                requests_used INTEGER NOT NULL,
                external_api_cost_usd REAL NOT NULL,
                run_status TEXT NOT NULL,
                errors_summary TEXT
            );
            """)
            conn.execute(
                "INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (1, ?)",
                (utc_now_iso(),)
            )

    def upsert_company(self, profile: CompanyProfile):
        """Insert or update company base record and full profile JSON."""
        now = utc_now_iso()
        with self.get_connection() as conn:
            conn.execute("""
            INSERT INTO companies (
                organization_number, official_name, organization_type, status,
                canonical_website, first_seen_at, last_researched_at,
                last_successful_research_at, profile_json, profile_schema_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(organization_number) DO UPDATE SET
                official_name = excluded.official_name,
                organization_type = excluded.organization_type,
                status = excluded.status,
                canonical_website = excluded.canonical_website,
                last_researched_at = excluded.last_researched_at,
                last_successful_research_at = CASE
                    WHEN excluded.last_successful_research_at IS NOT NULL
                    THEN excluded.last_successful_research_at
                    ELSE companies.last_successful_research_at
                END,
                profile_json = excluded.profile_json,
                profile_schema_version = excluded.profile_schema_version
            """, (
                profile.organization_number,
                profile.company.official_name,
                profile.company.organization_type,
                profile.company.status,
                profile.company.website,
                now,
                profile.last_researched_at or now,
                profile.last_researched_at if profile.research_status != "failed" else None,
                profile.model_dump_json(),
                profile.schema_version,
            ))

    def insert_facts(self, facts: List[Fact]):
        """Bulk insert facts, ignoring duplicates by fact_id or content_hash."""
        if not facts:
            return
        with self.get_connection() as conn:
            for fact in facts:
                fact_id = fact.fact_id or str(uuid.uuid4())
                conn.execute("""
                INSERT OR REPLACE INTO facts (
                    fact_id, organization_number, field_name, value_json,
                    source_id, source_url, retrieved_at, published_at,
                    reporting_period, evidence_excerpt, verification_status,
                    confidence, extraction_method, content_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    fact_id,
                    fact.organization_number,
                    fact.field_name,
                    json.dumps(fact.value) if fact.value is not None else None,
                    fact.fact_id,
                    fact.source_url,
                    fact.retrieved_at,
                    fact.published_at,
                    fact.reporting_period,
                    fact.evidence_excerpt,
                    fact.verification_status.value,
                    fact.confidence,
                    fact.extraction_method.value,
                    fact.content_hash,
                ))

    def insert_source(self, source: SourceRecord) -> str:
        """Record an external HTTP/API retrieval."""
        source_id = source.source_id or str(uuid.uuid4())
        with self.get_connection() as conn:
            conn.execute("""
            INSERT OR REPLACE INTO sources (
                source_id, source_name, source_url, source_type,
                retrieved_at, http_status, content_hash, extraction_status,
                error_category
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                source_id,
                source.source_name,
                source.source_url,
                source.source_type,
                source.retrieved_at,
                source.http_status,
                source.content_hash,
                source.extraction_status,
                source.error_category,
            ))
        return source_id

    def insert_snapshot(self, snapshot: SnapshotRecord) -> str:
        """Insert a point-in-time snapshot."""
        snapshot_id = snapshot.snapshot_id or str(uuid.uuid4())
        with self.get_connection() as conn:
            conn.execute("""
            INSERT INTO snapshots (
                snapshot_id, organization_number, created_at,
                normalized_profile_json, profile_hash
            ) VALUES (?, ?, ?, ?, ?)
            """, (
                snapshot_id,
                snapshot.organization_number,
                snapshot.created_at,
                snapshot.normalized_profile_json,
                snapshot.profile_hash,
            ))
        return snapshot_id

    def get_latest_snapshot(self, org_nr: str) -> Optional[SnapshotRecord]:
        """Fetch the most recent snapshot for a company."""
        with self.get_connection() as conn:
            row = conn.execute("""
            SELECT snapshot_id, organization_number, created_at,
                   normalized_profile_json, profile_hash
            FROM snapshots
            WHERE organization_number = ?
            ORDER BY created_at DESC
            LIMIT 1
            """, (org_nr,)).fetchone()
            if not row:
                return None
            return SnapshotRecord(
                snapshot_id=row["snapshot_id"],
                organization_number=row["organization_number"],
                created_at=row["created_at"],
                normalized_profile_json=row["normalized_profile_json"],
                profile_hash=row["profile_hash"],
            )

    def insert_changes(self, changes: List[ChangeRecord]):
        """Insert detected changes."""
        if not changes:
            return
        with self.get_connection() as conn:
            for ch in changes:
                change_id = ch.change_id or str(uuid.uuid4())
                conn.execute("""
                INSERT INTO changes (
                    change_id, organization_number, field_name,
                    previous_value_json, new_value_json, previous_source,
                    new_source, detected_at, previous_snapshot_id,
                    current_snapshot_id, evidence_reference, change_type,
                    confidence, review_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    change_id,
                    ch.organization_number,
                    ch.field_name,
                    json.dumps(ch.previous_value) if ch.previous_value is not None else None,
                    json.dumps(ch.new_value) if ch.new_value is not None else None,
                    ch.previous_source,
                    ch.new_source,
                    ch.detected_at,
                    ch.previous_snapshot_id,
                    ch.current_snapshot_id,
                    ch.evidence_reference,
                    ch.change_type.value,
                    ch.confidence,
                    ch.review_status,
                ))

    def get_changes_for_org(self, org_nr: str) -> List[ChangeRecord]:
        """Retrieve change history for a company."""
        with self.get_connection() as conn:
            rows = conn.execute("""
            SELECT * FROM changes
            WHERE organization_number = ?
            ORDER BY detected_at DESC
            """, (org_nr,)).fetchall()
            changes = []
            for r in rows:
                changes.append(ChangeRecord(
                    change_id=r["change_id"],
                    organization_number=r["organization_number"],
                    field_name=r["field_name"],
                    previous_value=json.loads(r["previous_value_json"]) if r["previous_value_json"] else None,
                    new_value=json.loads(r["new_value_json"]) if r["new_value_json"] else None,
                    previous_source=r["previous_source"],
                    new_source=r["new_source"],
                    detected_at=r["detected_at"],
                    previous_snapshot_id=r["previous_snapshot_id"],
                    current_snapshot_id=r["current_snapshot_id"],
                    evidence_reference=r["evidence_reference"],
                    change_type=r["change_type"],
                    confidence=r["confidence"],
                    review_status=r["review_status"],
                ))
            return changes

    def get_company(self, org_nr: str) -> Optional[CompanyProfile]:
        """Load stored company profile."""
        with self.get_connection() as conn:
            row = conn.execute("""
            SELECT profile_json FROM companies WHERE organization_number = ?
            """, (org_nr,)).fetchone()
            if not row or not row["profile_json"]:
                return None
            return CompanyProfile.model_validate_json(row["profile_json"])

    def record_run(self, run: ResearchRun):
        """Record or update a research run."""
        with self.get_connection() as conn:
            conn.execute("""
            INSERT OR REPLACE INTO research_runs (
                run_id, started_at, finished_at, companies_requested,
                companies_completed, requests_used, external_api_cost_usd,
                run_status, errors_summary
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                run.run_id,
                run.started_at,
                run.finished_at,
                run.companies_requested,
                run.companies_completed,
                run.requests_used,
                run.external_api_cost_usd,
                run.run_status,
                json.dumps(run.errors_summary),
            ))

    def count_companies(self) -> int:
        """Count total companies stored."""
        with self.get_connection() as conn:
            row = conn.execute("SELECT COUNT(*) AS cnt FROM companies").fetchone()
            return row["cnt"] if row else 0


db = Database()
