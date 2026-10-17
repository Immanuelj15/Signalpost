"""Base source adapter with safe retrieval, SSRF prevention, and request budgeting."""

import time
import socket
import ipaddress
import hashlib
import logging
from abc import ABC, abstractmethod
from urllib.parse import urlparse
from typing import Any, Dict, List, Optional, Tuple
import httpx

from signalpost.config import settings
from signalpost.models import Fact, SourceRecord, utc_now_iso
from signalpost.request_budget import budget

logger = logging.getLogger(__name__)

# Max allowed response size in bytes (5 MB)
MAX_RESPONSE_BYTES = 5 * 1024 * 1024


class SSRFSecurityError(ValueError):
    """Raised when an outbound URL points to an unsafe or private network destination."""
    pass


def is_safe_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Validate that the URL does not resolve to private, loopback, or cloud-metadata IPs.
    Guards against Server-Side Request Forgery (SSRF).
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False, f"Unsupported scheme: {parsed.scheme}"

        hostname = parsed.hostname
        if not hostname:
            return False, "Missing hostname in URL"

        # Disallow localhost keywords
        if hostname.lower() in ("localhost", "127.0.0.1", "::1", "metadata.google.internal"):
            return False, f"Host disallowed: {hostname}"

        # Fast path if hostname is already an IP address
        try:
            ip_obj = ipaddress.ip_address(hostname)
            if (
                ip_obj.is_private
                or ip_obj.is_loopback
                or ip_obj.is_link_local
                or ip_obj.is_multicast
                or ip_obj.is_reserved
                or ip_obj.is_unspecified
                or str(ip_obj) == "169.254.169.254"
            ):
                return False, f"Target IP {hostname} is a non-public or reserved address"
            return True, None
        except ValueError:
            pass

        # Resolve hostname with bounded timeout
        old_timeout = socket.getdefaulttimeout()
        try:
            socket.setdefaulttimeout(3.0)
            addr_info = socket.getaddrinfo(hostname, None)
        finally:
            socket.setdefaulttimeout(old_timeout)

        for entry in addr_info:
            ip_str = entry[4][0]
            ip_obj = ipaddress.ip_address(ip_str)

            if (
                ip_obj.is_private
                or ip_obj.is_loopback
                or ip_obj.is_link_local
                or ip_obj.is_multicast
                or ip_obj.is_reserved
                or ip_obj.is_unspecified
                or str(ip_obj) == "169.254.169.254"
            ):
                return False, f"Target IP {ip_str} for host {hostname} is a non-public or reserved address"

        return True, None
    except Exception as e:
        return False, f"DNS resolution or URL parsing error: {e}"


class BaseSourceAdapter(ABC):
    """Abstract base class for all public information source adapters."""

    source_name: str = "base"
    source_type: str = "api"  # "api", "html", "document"

    def __init__(self, cache_enabled: bool = True):
        self.cache_enabled = cache_enabled
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        self.headers = {
            "User-Agent": settings.user_agent,
            "Accept": "application/json, text/html, application/xhtml+xml;q=0.9, */*;q=0.8",
        }

    def safe_get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        check_ssrf: bool = True,
    ) -> Tuple[Optional[httpx.Response], Optional[str], Optional[int]]:
        """
        Safely fetch an HTTP endpoint with retries, exponential backoff, SSRF checks, and budget accounting.
        Returns: (response, error_category, status_code)
        """
        # Check cache
        cache_key = f"{url}_{str(sorted(params.items()) if params else '')}"
        if self.cache_enabled and cache_key in self._memory_cache:
            cached_data = self._memory_cache[cache_key]
            logger.debug(f"Cache hit for {url}")
            return cached_data["response"], None, cached_data["status_code"]

        # Validate URL for SSRF
        if check_ssrf:
            is_safe, reason = is_safe_url(url)
            if not is_safe:
                logger.warning(f"SSRF block on {url}: {reason}")
                return None, f"ssrf_blocked: {reason}", None

        req_headers = dict(self.headers)
        if headers:
            req_headers.update(headers)

        req_timeout = timeout if timeout is not None else settings.request_timeout_seconds
        retries = settings.max_retries
        backoff = settings.backoff_factor

        for attempt in range(retries):
            # Record request in budget manager (will raise BudgetExceededError if limit breached)
            budget.record_request(source_name=self.source_name, cost_usd=0.0)

            try:
                with httpx.Client(
                    timeout=req_timeout,
                    follow_redirects=False,  # Re-evaluate redirects for SSRF
                    limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
                ) as client:
                    resp = client.get(url, params=params, headers=req_headers)

                    # Handle Redirects safely
                    if resp.is_redirect:
                        redirect_url = resp.headers.get("Location")
                        if not redirect_url:
                            return None, "invalid_redirect", resp.status_code
                        # Check redirect destination
                        if check_ssrf:
                            safe_redir, redir_reason = is_safe_url(redirect_url)
                            if not safe_redir:
                                return None, f"ssrf_redirect_blocked: {redir_reason}", resp.status_code
                        # Follow single safe redirect
                        budget.record_request(source_name=self.source_name, cost_usd=0.0)
                        resp = client.get(redirect_url, headers=req_headers)

                    # Check response size
                    content_length = resp.headers.get("Content-Length")
                    if content_length and int(content_length) > MAX_RESPONSE_BYTES:
                        return None, f"response_size_exceeded_{content_length}_bytes", resp.status_code

                    # Check rate limits / 429
                    if resp.status_code == 429:
                        retry_after = resp.headers.get("Retry-After")
                        sleep_time = float(retry_after) if retry_after and retry_after.isdigit() else (backoff ** attempt)
                        logger.warning(f"Rate limited (429) on {url}. Sleeping {sleep_time}s.")
                        time.sleep(min(sleep_time, 10.0))
                        continue

                    # Server errors: retry
                    if resp.status_code in (500, 502, 503, 504) and attempt < retries - 1:
                        time.sleep(backoff ** attempt)
                        continue

                    # Success or deterministic client error (like 404)
                    if self.cache_enabled and resp.status_code == 200:
                        self._memory_cache[cache_key] = {
                            "response": resp,
                            "status_code": resp.status_code
                        }

                    error_cat = None
                    if resp.status_code == 404:
                        error_cat = "not_found"
                    elif resp.status_code >= 400:
                        error_cat = f"http_{resp.status_code}"

                    return resp, error_cat, resp.status_code

            except httpx.TimeoutException:
                if attempt == retries - 1:
                    return None, "timeout", None
                time.sleep(backoff ** attempt)
            except httpx.RequestError as e:
                if attempt == retries - 1:
                    return None, f"network_error: {str(e)}", None
                time.sleep(backoff ** attempt)
            except Exception as e:
                return None, f"unexpected_error: {str(e)}", None

        return None, "retries_exhausted", None

    @abstractmethod
    def fetch_and_extract(self, org_nr: str) -> Tuple[List[Fact], Optional[SourceRecord]]:
        """Fetch raw source data and extract structured facts for a given company."""
        pass
