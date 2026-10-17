"""Tests for request budgeting, accounting, and limits enforcement."""

import pytest
from signalpost.request_budget import RequestBudgetManager, BudgetExceededError


def test_request_budget_accounting():
    mgr = RequestBudgetManager(max_requests=10, max_cost_usd=5.0, timeout_seconds=60)
    
    mgr.record_request("brreg_enhetsregisteret", cost_usd=0.0)
    mgr.record_request("brreg_regnskap", cost_usd=0.0)
    mgr.record_request("company_website", cost_usd=0.0)

    summary = mgr.get_summary()
    assert summary["total_outbound_requests"] == 3
    assert summary["requests_remaining"] == 7
    assert summary["total_external_cost_usd"] == 0.0
    assert summary["is_zero_cost"] is True
    assert summary["requests_by_source"]["brreg_enhetsregisteret"] == 1


def test_budget_exceeded_raises_error():
    mgr = RequestBudgetManager(max_requests=2, max_cost_usd=1.0, timeout_seconds=60)
    
    mgr.record_request("test_source", cost_usd=0.0)
    mgr.record_request("test_source", cost_usd=0.0)

    # 3rd request should exceed max_requests of 2
    with pytest.raises(BudgetExceededError) as exc_info:
        mgr.record_request("test_source", cost_usd=0.0)
    assert "Outbound request limit reached" in str(exc_info.value)


def test_cost_budget_exceeded():
    mgr = RequestBudgetManager(max_requests=100, max_cost_usd=0.5, timeout_seconds=60)
    
    mgr.record_request("paid_source", cost_usd=0.4)
    # Next request breaches 0.5 threshold
    mgr.record_request("paid_source", cost_usd=0.2)

    with pytest.raises(BudgetExceededError) as exc_info:
        mgr.record_request("paid_source", cost_usd=0.0)
    assert "Cost limit reached" in str(exc_info.value)
