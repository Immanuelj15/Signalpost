"""Company Website Adapter with domain verification, rule-based parsing, and SSRF guard."""

import re
import hashlib
import logging
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from signalpost.models import (
    Fact,
    SourceRecord,
    VerificationStatus,
    ExtractionMethod,
    utc_now_iso,
)
from signalpost.sources.base import BaseSourceAdapter, is_safe_url

logger = logging.getLogger(__name__)


def extract_emails(text: str) -> List[str]:
    """Find valid email addresses in text."""
    pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    matches = re.findall(pattern, text)
    valid = []
    for m in matches:
        # Filter out common false positives (.png, .jpg, etc.)
        if not re.search(r"\.(png|jpg|jpeg|gif|svg|webp|css|js)$", m, re.I):
            if m.lower() not in [v.lower() for v in valid]:
                valid.append(m)
    return valid[:5]


def extract_phones(text: str) -> List[str]:
    """Find Norwegian phone numbers in text (+47 or 8 digits with boundary assertions)."""
    pattern = r"(?<!\d)(?:(?:\+|00)47[\s.-]*)?[2-9]\d(?:[\s.-]*\d{2}){3}(?!\d)|(?<!\d)[2-9]\d{7}(?!\d)"
    matches = re.findall(pattern, text)
    cleaned = []
    for m in matches:
        digits = re.sub(r"[^\d]", "", m)
        if digits.startswith("47") and len(digits) == 10:
            digits = digits[2:]
        if len(digits) == 8 and digits not in cleaned:
            cleaned.append(digits)
    return cleaned[:3]


class CompanyWebsiteAdapter(BaseSourceAdapter):
    """Adapter for retrieving and parsing verified company websites."""

    source_name = "company_website"
    source_type = "html"

    def fetch_website_facts(
        self,
        org_nr: str,
        website_url: str,
        company_name: Optional[str] = None
    ) -> Tuple[List[Fact], Optional[SourceRecord], Dict[str, Any]]:
        """
        Safely fetch and parse company website.
        Verifies domain-to-company relationship before attaching facts.
        """
        now = utc_now_iso()
        if not website_url:
            return [], None, {}

        # Ensure scheme
        if not website_url.startswith(("http://", "https://")):
            website_url = f"https://{website_url}"

        # SSRF validation
        safe, reason = is_safe_url(website_url)
        if not safe:
            logger.warning(f"Blocked website fetch {website_url}: {reason}")
            rec = SourceRecord(
                source_name=self.source_name,
                source_url=website_url,
                source_type=self.source_type,
                retrieved_at=now,
                extraction_status="ssrf_blocked",
                error_category=f"ssrf_blocked: {reason}",
            )
            return [], rec, {}

        resp, error_cat, status_code = self.safe_get(
            website_url,
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            },
            timeout=10.0,
            check_ssrf=True
        )

        source_rec = SourceRecord(
            source_name=self.source_name,
            source_url=website_url,
            source_type=self.source_type,
            retrieved_at=now,
            http_status=status_code,
            extraction_status="success" if resp and resp.status_code == 200 else (error_cat or "failed"),
            error_category=error_cat,
        )

        if not resp or resp.status_code != 200:
            return [], source_rec, {}

        html_text = resp.text
        source_rec.content_hash = hashlib.sha256(html_text.encode("utf-8", errors="ignore")).hexdigest()

        try:
            soup = BeautifulSoup(html_text, "html.parser")
        except Exception as e:
            source_rec.extraction_status = f"parse_error: {e}"
            return [], source_rec, {}

        # Extract visible text
        for tag in soup(["script", "style", "noscript", "svg"]):
            tag.decompose()
        page_text = soup.get_text(separator=" ", strip=True)

        # Domain verification: verify link between website and company
        # Check if org number or company name appears on page
        domain_verified = False
        evidence_found = []

        if org_nr in page_text:
            domain_verified = True
            evidence_found.append(f"Organisasjonsnummer {org_nr} found on website")

        if company_name:
            # Check for words from company name
            clean_name = re.sub(r"\b(AS|ASA|ENK|BA|ANS|DA|NUF)\b", "", company_name, flags=re.I).strip()
            if len(clean_name) >= 3 and clean_name.lower() in page_text.lower():
                domain_verified = True
                evidence_found.append(f"Company name match '{clean_name}' found on website")

        verification_status = VerificationStatus.VERIFIED if domain_verified else VerificationStatus.UNVERIFIED
        confidence = 0.95 if domain_verified else 0.50

        facts: List[Fact] = []
        extracted_metadata: Dict[str, Any] = {}

        # 1. Business Description (meta description, og:description, or first paragraph)
        meta_desc = ""
        meta_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
        if meta_tag and meta_tag.get("content"):
            meta_desc = meta_tag["content"].strip()

        if meta_desc:
            extracted_metadata["description"] = meta_desc
            ch = hashlib.sha256(f"{org_nr}:business_description:{meta_desc}".encode("utf-8")).hexdigest()
            facts.append(Fact(
                organization_number=org_nr,
                field_name="business_description",
                value=meta_desc,
                data_type="string",
                source_name=self.source_name,
                source_url=website_url,
                retrieved_at=now,
                evidence_excerpt=f"meta description: {meta_desc[:250]}",
                verification_status=verification_status,
                confidence=confidence,
                extraction_method=ExtractionMethod.RULE_BASED_HTML,
                content_hash=ch,
            ))

        # 2. Contact Email
        emails = extract_emails(page_text)
        if emails:
            extracted_metadata["email"] = emails[0]
            ch = hashlib.sha256(f"{org_nr}:contact_email:{emails[0]}".encode("utf-8")).hexdigest()
            facts.append(Fact(
                organization_number=org_nr,
                field_name="contact_email",
                value=emails[0],
                data_type="email",
                source_name=self.source_name,
                source_url=website_url,
                retrieved_at=now,
                evidence_excerpt=f"Identified contact email: {emails[0]}",
                verification_status=verification_status,
                confidence=confidence,
                extraction_method=ExtractionMethod.RULE_BASED_HTML,
                content_hash=ch,
            ))

        # 3. Contact Phone
        phones = extract_phones(page_text)
        if phones:
            extracted_metadata["phone"] = phones[0]
            ch = hashlib.sha256(f"{org_nr}:contact_phone:{phones[0]}".encode("utf-8")).hexdigest()
            facts.append(Fact(
                organization_number=org_nr,
                field_name="contact_phone",
                value=phones[0],
                data_type="phone",
                source_name=self.source_name,
                source_url=website_url,
                retrieved_at=now,
                evidence_excerpt=f"Identified phone number: {phones[0]}",
                verification_status=verification_status,
                confidence=confidence,
                extraction_method=ExtractionMethod.RULE_BASED_HTML,
                content_hash=ch,
            ))

        # 4. Products & Services keywords / offerings
        products = []
        for header in soup.find_all(["h1", "h2", "h3", "li"]):
            text = header.get_text(strip=True)
            if any(k in text.lower() for k in ["tjenester", "produkter", "services", "solutions", "solutions", "hva vi gjør"]):
                # look at following sibling or list items
                parent = header.parent
                if parent:
                    for li in parent.find_all("li")[:6]:
                        li_text = li.get_text(strip=True)
                        if 3 <= len(li_text) <= 80 and li_text not in products:
                            products.append(li_text)
        if products:
            extracted_metadata["products_and_services"] = products
            ch = hashlib.sha256(f"{org_nr}:products_and_services:{','.join(products)}".encode("utf-8")).hexdigest()
            facts.append(Fact(
                organization_number=org_nr,
                field_name="products_and_services",
                value=products,
                data_type="list",
                source_name=self.source_name,
                source_url=website_url,
                retrieved_at=now,
                evidence_excerpt=f"Products/Services list: {', '.join(products)[:250]}",
                verification_status=verification_status,
                confidence=confidence,
                extraction_method=ExtractionMethod.RULE_BASED_HTML,
                content_hash=ch,
            ))

        return facts, source_rec, extracted_metadata

    def fetch_and_extract(self, org_nr: str) -> Tuple[List[Fact], Optional[SourceRecord]]:
        """Base interface implementation."""
        # Website adapter needs the website URL from registry or planner
        return [], None
