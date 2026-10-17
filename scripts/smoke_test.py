"""Live smoke test executing research against official public Brønnøysund APIs."""

import sys
import json
from pathlib import Path

# Ensure UTF-8 output on Windows terminals
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from signalpost.database import db
from signalpost.orchestrator import ResearchAgent
from signalpost.request_budget import budget
from signalpost.export import display_profile_summary

def run_smoke_test():
    print("=" * 70)
    print("SIGNALPOST LIVE SMOKE TEST")
    print("Evidence-First Norwegian Company Intelligence Agent")
    print("=" * 70)

    db.init_db()
    agent = ResearchAgent(database=db)

    # Test cases: Real verified Norwegian entities + 1 invalid checksum edge-case
    test_orgs = [
        "923609016",  # Equinor ASA (ASA with financial statements)
        "984851006",  # Brønnøysundregistrene (ORGL government agency)
        "123456789",  # Synthetic invalid test case (must return structured error)
    ]

    print(f"\n[1/3] Executing research batch for {len(test_orgs)} entities...")
    profiles, run = agent.research_batch(test_orgs, max_workers=2)

    assert len(profiles) == len(test_orgs), f"Expected {len(test_orgs)} terminal results, got {len(profiles)}"
    print(f"[OK] Received exactly {len(profiles)} terminal results (1-per-input invariant preserved).")

    # Inspect results
    for p in profiles:
        print(f"\n--- Result for {p.organization_number} ---")
        print(f"  Official Name   : {p.company.official_name}")
        print(f"  Identity Status : {p.identity_status.value}")
        print(f"  Research Status : {p.research_status.value}")
        print(f"  Verified Facts  : {len(p.facts)}")
        print(f"  Financial Stmts : {len(p.financials or [])}")
        if p.errors:
            print(f"  Errors Captured : {p.errors}")
        if p.financials:
            latest = p.financials[0]
            print(f"  Latest Revenue  : {latest.total_revenue} {latest.currency} ({latest.reporting_period})")

    # Verify invalid entity produced structured failure
    invalid_res = next(p for p in profiles if p.organization_number == "123456789")
    assert invalid_res.identity_status.value == "invalid"
    assert invalid_res.research_status.value == "failed"
    print("\n[OK] Verified invalid organization number returned structured failure without throwing.")

    # Idempotency check: run again without change
    print("\n[2/3] Checking idempotency (second run over unchanged data)...")
    p2 = agent.research_company("923609016", force_refresh=False)
    assert len(p2.changes) == 0, f"Expected 0 changes on unchanged data, got {len(p2.changes)}"
    print("[OK] Idempotency verified: 0 duplicate changes recorded on unchanged data.")

    # Cost & Budget Verification
    print("\n[3/3] Checking budget and $0 cost accounting...")
    b_summary = budget.get_summary()
    print(f"  Total outbound requests : {b_summary['total_outbound_requests']}")
    print(f"  Measured external cost  : ${b_summary['total_external_cost_usd']:.4f} (₹0.00)")
    assert b_summary["total_external_cost_usd"] == 0.0, "Expected ₹0 / $0 external API cost"
    print("[OK] Zero cost requirement verified ($0.00 / ₹0.00).")

    print("\n" + "=" * 70)
    print("ALL SMOKE TEST CHECKS PASSED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_smoke_test()
