"""Request budget and cost accounting manager."""

import time
import threading
from typing import Dict, Any, Optional
from signalpost.config import settings


class BudgetExceededError(Exception):
    """Raised when request budget or cost threshold is reached."""
    pass


class RequestBudgetManager:
    """Thread-safe request and cost accounting singleton."""

    def __init__(
        self,
        max_requests: Optional[int] = None,
        max_cost_usd: Optional[float] = None,
        timeout_seconds: Optional[float] = None,
    ):
        self._lock = threading.RLock()
        self.max_requests = max_requests if max_requests is not None else settings.max_outbound_requests
        self.max_cost_usd = max_cost_usd if max_cost_usd is not None else settings.max_external_api_cost_usd
        self.timeout_seconds = timeout_seconds if timeout_seconds is not None else (settings.execution_timeout_minutes * 60)
        
        self.start_time = time.time()
        self.requests_count = 0
        self.requests_by_source: Dict[str, int] = {}
        self.external_cost_usd = 0.0
        self.cost_by_source: Dict[str, float] = {}

    def reset(self):
        """Reset budget tracking for a new run."""
        with self._lock:
            self.start_time = time.time()
            self.requests_count = 0
            self.requests_by_source.clear()
            self.external_cost_usd = 0.0
            self.cost_by_source.clear()

    def check_budget(self):
        """Check if any operational limits have been breached."""
        with self._lock:
            elapsed = time.time() - self.start_time
            if elapsed > self.timeout_seconds:
                raise BudgetExceededError(
                    f"Execution timeout of {self.timeout_seconds}s exceeded (elapsed: {elapsed:.1f}s)"
                )
            if self.requests_count >= self.max_requests:
                raise BudgetExceededError(
                    f"Outbound request limit reached: {self.requests_count}/{self.max_requests}"
                )
            if self.external_cost_usd >= self.max_cost_usd:
                raise BudgetExceededError(
                    f"Cost limit reached: ${self.external_cost_usd:.4f}/${self.max_cost_usd:.2f}"
                )

    def record_request(self, source_name: str, cost_usd: float = 0.0):
        """Record an outbound request and its associated cost."""
        with self._lock:
            self.check_budget()
            self.requests_count += 1
            self.requests_by_source[source_name] = self.requests_by_source.get(source_name, 0) + 1
            if cost_usd > 0.0:
                self.external_cost_usd += cost_usd
                self.cost_by_source[source_name] = self.cost_by_source.get(source_name, 0.0) + cost_usd

    def get_summary(self) -> Dict[str, Any]:
        """Return usage and budget summary."""
        with self._lock:
            elapsed = time.time() - self.start_time
            return {
                "elapsed_seconds": round(elapsed, 2),
                "total_outbound_requests": self.requests_count,
                "max_allowed_requests": self.max_requests,
                "requests_remaining": max(0, self.max_requests - self.requests_count),
                "requests_by_source": dict(self.requests_by_source),
                "total_external_cost_usd": round(self.external_cost_usd, 6),
                "max_cost_usd": self.max_cost_usd,
                "cost_by_source": dict(self.cost_by_source),
                "is_zero_cost": (self.external_cost_usd == 0.0),
            }


# Global singleton instance
budget = RequestBudgetManager()
