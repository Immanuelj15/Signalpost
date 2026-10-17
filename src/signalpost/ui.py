"""Streamlit dashboard for Signalpost: Evidence-First Norwegian Company Intelligence Agent.
Modern Blue & White Enterprise Design.
"""

import json
from pathlib import Path
import streamlit as st
import pandas as pd

from signalpost.database import db
from signalpost.orchestrator import ResearchAgent
from signalpost.export import export_profiles_csv
from signalpost.request_budget import budget

# 1. Page Configuration
st.set_page_config(
    page_title="Signalpost | Norwegian Company Intelligence",
    page_icon="🇳🇴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Inject Custom Blue & White Theme CSS
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #0F172A;
}

/* Background */
.stApp {
    background-color: #F8FAFC;
}

/* Header Hero Banner */
.hero-banner {
    background: linear-gradient(135deg, #1E3A8A 0%, #1D4ED8 50%, #2563EB 100%);
    border-radius: 16px;
    padding: 32px 36px;
    color: #FFFFFF;
    margin-bottom: 28px;
    box-shadow: 0 10px 25px -5px rgba(29, 78, 216, 0.25), 0 8px 10px -6px rgba(29, 78, 216, 0.15);
    position: relative;
    overflow: hidden;
}

.hero-banner::after {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 350px;
    height: 350px;
    background: radial-gradient(circle, rgba(255,255,255,0.12) 0%, rgba(255,255,255,0) 70%);
    border-radius: 50%;
}

.hero-title {
    font-size: 2.2rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    margin: 0;
    color: #FFFFFF;
    display: flex;
    align-items: center;
    gap: 12px;
}

.hero-subtitle {
    font-size: 1.05rem;
    color: #DBEAFE;
    margin-top: 8px;
    max-width: 750px;
    line-height: 1.5;
}

.badge-row {
    display: flex;
    gap: 10px;
    margin-top: 18px;
    flex-wrap: wrap;
}

.hero-badge {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.25);
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 600;
    color: #FFFFFF;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* Card Container */
.sp-card {
    background: #FFFFFF;
    border-radius: 14px;
    border: 1px solid #E2E8F0;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.04), 0 2px 4px -2px rgba(15, 23, 42, 0.03);
    transition: all 0.2s ease-in-out;
}

.sp-card:hover {
    border-color: #BFDBFE;
    box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.08), 0 4px 6px -4px rgba(37, 99, 235, 0.04);
}

/* KPI Stat Cards */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
}

.kpi-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-top: 4px solid #2563EB;
    border-radius: 12px;
    padding: 18px 20px;
    box-shadow: 0 2px 4px rgba(15, 23, 42, 0.03);
}

.kpi-label {
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #64748B;
    margin-bottom: 6px;
}

.kpi-value {
    font-size: 1.6rem;
    font-weight: 800;
    color: #1E3A8A;
    letter-spacing: -0.02em;
}

.kpi-sub {
    font-size: 0.8rem;
    color: #059669;
    font-weight: 600;
    margin-top: 4px;
}

/* Company Header Card */
.company-header-card {
    background: #FFFFFF;
    border: 1px solid #BFDBFE;
    border-radius: 14px;
    padding: 24px 28px;
    margin-bottom: 24px;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.06);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
}

.company-title {
    font-size: 1.75rem;
    font-weight: 800;
    color: #0F172A;
    margin: 0;
    letter-spacing: -0.02em;
}

.company-meta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.95rem;
    color: #2563EB;
    font-weight: 600;
    margin-top: 4px;
}

/* Status Pill */
.status-pill-verified {
    background: #EFF6FF;
    color: #1D4ED8;
    border: 1px solid #93C5FD;
    padding: 6px 16px;
    border-radius: 24px;
    font-size: 0.85rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

.status-dot {
    width: 8px;
    height: 8px;
    background-color: #2563EB;
    border-radius: 50%;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2);
}

.status-pill-error {
    background: #FEF2F2;
    color: #B91C1C;
    border: 1px solid #FCA5A5;
    padding: 6px 16px;
    border-radius: 24px;
    font-size: 0.85rem;
    font-weight: 700;
}

/* Explanation Box */
.explanation-box {
    background: #F0FDF4;
    border-left: 4px solid #16A34A;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 12px;
    font-size: 0.92rem;
    color: #14532D;
    line-height: 1.5;
}

.warning-box {
    background: #FFFBEB;
    border-left: 4px solid #D97706;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 12px;
    font-size: 0.92rem;
    color: #78350F;
}

/* Sidebar Custom Styling */
section[data-testid="stSidebar"] {
    background-color: #FFFFFF;
    border-right: 1px solid #E2E8F0;
}

.sidebar-logo {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 0 20px 0;
    border-bottom: 1px solid #E2E8F0;
    margin-bottom: 20px;
}

.sidebar-brand {
    font-size: 1.25rem;
    font-weight: 800;
    color: #1E3A8A;
    letter-spacing: -0.02em;
}

.sidebar-card {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 14px;
    margin-bottom: 16px;
}

.sidebar-stat-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    font-weight: 700;
    color: #64748B;
    letter-spacing: 0.04em;
}

.sidebar-stat-val {
    font-size: 1.25rem;
    font-weight: 800;
    color: #1E3A8A;
    margin-top: 2px;
}

/* Streamlit Tabs Customization */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: transparent;
    border-bottom: 2px solid #E2E8F0;
}

.stTabs [data-baseweb="tab"] {
    height: 48px;
    white-space: pre-wrap;
    background-color: transparent;
    border-radius: 8px 8px 0 0;
    color: #64748B;
    font-weight: 600;
    font-size: 0.92rem;
    padding: 0 18px;
}

.stTabs [aria-selected="true"] {
    background-color: #FFFFFF !important;
    color: #1D4ED8 !important;
    border-bottom: 3px solid #1D4ED8 !important;
    font-weight: 700;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #1D4ED8 0%, #2563EB 100%) !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 8px 24px !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25) !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    box-shadow: 0 6px 16px rgba(37, 99, 235, 0.35) !important;
    transform: translateY(-1px);
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# 3. Initialize Database & Agent
db.init_db()
agent = ResearchAgent(database=db)

# 4. Sidebar Content
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div style="font-size: 2rem;">🇳🇴</div>
        <div>
            <div class="sidebar-brand">SIGNALPOST</div>
            <div style="font-size: 0.75rem; color: #64748B; font-weight: 600;">Norwegian Intelligence Agent</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Operational metrics in clean white cards
    b_summary = budget.get_summary()
    st.markdown(f"""
    <div class="sidebar-card">
        <div class="sidebar-stat-label">Outbound API Requests</div>
        <div class="sidebar-stat-val">{b_summary['total_outbound_requests']} <span style="font-size: 0.85rem; color: #64748B; font-weight: 500;">/ {b_summary['max_allowed_requests']}</span></div>
        <div style="height: 6px; background: #E2E8F0; border-radius: 4px; margin-top: 8px; overflow: hidden;">
            <div style="height: 100%; width: {min(100, int((b_summary['total_outbound_requests']/b_summary['max_allowed_requests'])*100))}%; background: #2563EB;"></div>
        </div>
    </div>

    <div class="sidebar-card">
        <div class="sidebar-stat-label">Measured External Cost</div>
        <div class="sidebar-stat-val" style="color: #059669;">${b_summary['total_external_cost_usd']:.4f} <span style="font-size: 0.85rem; color: #059669; font-weight: 600;">(₹0.00)</span></div>
        <div style="font-size: 0.72rem; color: #64748B; margin-top: 4px;">100% Free-First Execution</div>
    </div>

    <div class="sidebar-card">
        <div class="sidebar-stat-label">Companies In Database</div>
        <div class="sidebar-stat-val">{db.count_companies()}</div>
        <div style="font-size: 0.72rem; color: #64748B; margin-top: 4px;">SQLite WAL Local Storage</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-stat-label' style='margin-bottom: 8px;'>Navigation</div>", unsafe_allow_html=True)
    view_mode = st.radio(
        "Navigation",
        ["Company Research", "Batch Processing", "Historical Audit & Changes", "System & Cost Overview"],
        label_visibility="collapsed"
    )

# 5. Top Hero Banner
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">
        <span>🇳🇴</span>
        <span>Signalpost Intelligence</span>
    </div>
    <div class="hero-subtitle">
        Autonomous, evidence-first Norwegian corporate research agent. Sources verifiable public data from Brønnøysund Enhetsregisteret, Regnskapsregisteret, and audited filings.
    </div>
    <div class="badge-row">
        <div class="hero-badge">✓ Official Brreg REST API</div>
        <div class="hero-badge">✓ Regnskapsregisteret Audited Financials</div>
        <div class="hero-badge">✓ Modulo 11 Verified</div>
        <div class="hero-badge">✓ ₹0 Cost Default Path</div>
        <div class="hero-badge">✓ 1,000+ Profile Capacity</div>
    </div>
</div>
""", unsafe_allow_html=True)

# TAB 1: Company Research
if view_mode == "Company Research":
    st.markdown("<h3 style='color: #1E3A8A; font-weight: 800; margin-bottom: 8px;'>Company Intelligence Research</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B; font-size: 0.95rem; margin-bottom: 20px;'>Accepts Norwegian 9-digit organization numbers (<em>organisasjonsnummer</em>). Resolves official registry records, multi-year audited financial accounts, and attributable evidence excerpts.</p>", unsafe_allow_html=True)

    # Search Box & Quick Chips
    st.markdown("<div style='font-size: 0.85rem; font-weight: 600; color: #475569; margin-bottom: 6px;'>Quick Select Example Entities:</div>", unsafe_allow_html=True)
    chip_cols = st.columns(5)
    selected_chip = None
    if chip_cols[0].button("Equinor ASA (923609016)", use_container_width=True):
        st.session_state["search_org"] = "923609016"
    if chip_cols[1].button("DNB Bank ASA (984851006)", use_container_width=True):
        st.session_state["search_org"] = "984851006"
    if chip_cols[2].button("Posten Bring (915000578)", use_container_width=True):
        st.session_state["search_org"] = "915000578"
    if chip_cols[3].button("Telenor ASA (998848316)", use_container_width=True):
        st.session_state["search_org"] = "998848316"
    if chip_cols[4].button("Yara Intl (986228608)", use_container_width=True):
        st.session_state["search_org"] = "986228608"

    default_org = st.session_state.get("search_org", "923609016")

    col1, col2, col3 = st.columns([4, 1.5, 1.5])
    with col1:
        org_input = st.text_input(
            "Norwegian Organization Number",
            value=default_org,
            help="Enter a 9-digit Norwegian organization number",
            label_visibility="collapsed"
        )
    with col2:
        refresh_check = st.checkbox("Force Fresh API Fetch", value=False)
    with col3:
        search_clicked = st.button("Research Entity", type="primary", use_container_width=True)

    # Auto-run if chip clicked or button pressed or initial default
    if search_clicked or "search_org" in st.session_state or org_input:
        with st.spinner(f"Querying official Norwegian registries for {org_input}..."):
            profile = agent.research_company(org_input, force_refresh=refresh_check)

        comp = profile.company
        is_verified = (profile.identity_status.value == "verified")

        # Company Header Card
        status_badge_html = f"""
        <div class="{"status-pill-verified" if is_verified else "status-pill-error"}">
            {"<div class='status-dot'></div>" if is_verified else ""}
            {profile.identity_status.value.upper()}
        </div>
        """

        st.markdown(f"""
        <div class="company-header-card">
            <div>
                <h1 class="company-title">{comp.official_name or 'Entity Not Found'}</h1>
                <div class="company-meta">ORG.NR: {profile.organization_number} • FORM: {comp.organization_type or 'N/A'} • STATUS: {comp.status or 'Unknown'}</div>
            </div>
            <div>
                {status_badge_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 4 Core KPI Stat Cards
        latest_rev_str = "N/A"
        latest_ebit_str = "N/A"
        if profile.financials:
            f = profile.financials[0]
            if f.total_revenue is not None:
                latest_rev_str = f"{f.total_revenue:,.0f} {f.currency}"
            if f.operating_profit is not None:
                latest_ebit_str = f"{f.operating_profit:,.0f} {f.currency}"

        emp_str = f"{comp.employees:,}" if comp.employees is not None else "Undisclosed"

        st.markdown(f"""
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">Corporate Status</div>
                <div class="kpi-value" style="font-size: 1.35rem; color: #1E3A8A;">{(comp.status or 'Unknown').capitalize()}</div>
                <div class="kpi-sub">Form: {comp.organization_type or 'Entity'}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Registered Workforce</div>
                <div class="kpi-value">{emp_str}</div>
                <div class="kpi-sub">Employees on Record</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Latest Annual Revenue</div>
                <div class="kpi-value" style="font-size: 1.25rem;">{latest_rev_str}</div>
                <div class="kpi-sub">Regnskapsregisteret</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Attributable Facts</div>
                <div class="kpi-value">{len(profile.facts)}</div>
                <div class="kpi-sub">100% Source-Backed</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Evidence Explanations Banner
        if profile.explanations:
            st.markdown("<div style='font-size: 0.95rem; font-weight: 700; color: #1E3A8A; margin-bottom: 8px;'>Traceable Audit Explanations</div>", unsafe_allow_html=True)
            for exp in profile.explanations:
                st.markdown(f"<div class='explanation-box'><strong>Verified Claim:</strong> {exp}</div>", unsafe_allow_html=True)

        # Tab Navigation
        tab_overview, tab_financials, tab_facts, tab_changes, tab_missing = st.tabs([
            "🏢 Company Overview",
            "📊 Financial Statements",
            "📑 Attributable Facts",
            "⏱️ Changes & History",
            "⚠️ Missing Data Summary"
        ])

        with tab_overview:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("<div class='sp-card'>", unsafe_allow_html=True)
                st.markdown("<h4 style='color: #1E3A8A; font-weight: 700;'>Registration & Identifiers</h4>", unsafe_allow_html=True)
                st.write(f"**Legal Name:** {comp.official_name or 'N/A'}")
                st.write(f"**Organization Number:** `{profile.organization_number}`")
                st.write(f"**Entity Form:** {comp.organization_type or 'N/A'} ({comp.organization_type_description or ''})")
                st.write(f"**Registration Date:** {comp.registration_date or 'N/A'}")
                st.write(f"**Incorporation Date:** {comp.incorporation_date or 'N/A'}")
                st.write(f"**Official Website:** [{comp.website}]({comp.website})" if comp.website else "**Official Website:** Not registered")
                st.write(f"**Parent Organization:** `{comp.parent_organization}`" if comp.parent_organization else "**Parent Organization:** Independent")
                st.write(f"**Bankruptcy Proceeding:** {'⚠️ YES' if comp.is_in_bankruptcy else 'No'}")
                st.write(f"**Liquidation Status:** {'⚠️ In Liquidation' if comp.is_in_liquidation else 'Active'}")
                st.markdown("</div>", unsafe_allow_html=True)

            with c2:
                st.markdown("<div class='sp-card'>", unsafe_allow_html=True)
                st.markdown("<h4 style='color: #1E3A8A; font-weight: 700;'>Registered Location & Address</h4>", unsafe_allow_html=True)
                if comp.business_address:
                    b = comp.business_address
                    st.write(f"**Street Address:** {', '.join(b.address) if b.address else 'N/A'}")
                    st.write(f"**Postal Code & City:** {b.postal_code or ''} {b.city or ''}")
                    st.write(f"**Municipality:** {b.municipality or 'N/A'} (Kommune nr: `{b.municipality_number or 'N/A'}`)")
                    st.write(f"**Country:** {b.country or 'Norge'} ({b.country_code or 'NO'})")
                else:
                    st.info("No business address published.")
                st.markdown("</div>", unsafe_allow_html=True)

            if comp.business_activity:
                st.markdown("<div class='sp-card'>", unsafe_allow_html=True)
                st.markdown("<h4 style='color: #1E3A8A; font-weight: 700;'>Declared Commercial Objectives</h4>", unsafe_allow_html=True)
                for act in comp.business_activity:
                    st.markdown(f"- {act}")
                st.markdown("</div>", unsafe_allow_html=True)

            if comp.products_and_services:
                st.markdown("<div class='sp-card'>", unsafe_allow_html=True)
                st.markdown("<h4 style='color: #1E3A8A; font-weight: 700;'>Discovered Products & Services</h4>", unsafe_allow_html=True)
                for prod in comp.products_and_services:
                    st.markdown(f"• **{prod}**")
                st.markdown("</div>", unsafe_allow_html=True)

        with tab_financials:
            if profile.financials:
                st.markdown("<div class='sp-card'>", unsafe_allow_html=True)
                st.markdown("<h4 style='color: #1E3A8A; font-weight: 700;'>Annual Accounts from Regnskapsregisteret</h4>", unsafe_allow_html=True)
                st.markdown("<p style='color: #64748B; font-size: 0.88rem;'>Distinguishes operating revenue, sales revenue, operating profit (EBIT), net annual profit, total assets, equity, and debt by reporting period.</p>", unsafe_allow_html=True)
                
                fin_rows = []
                for stmt in profile.financials:
                    fin_rows.append({
                        "Reporting Period": stmt.reporting_period,
                        "Year": stmt.year,
                        "Type": stmt.statement_type,
                        "Currency": stmt.currency,
                        "Total Revenue": f"{stmt.total_revenue:,.0f}" if stmt.total_revenue is not None else "-",
                        "EBIT (Operating Profit)": f"{stmt.operating_profit:,.0f}" if stmt.operating_profit is not None else "-",
                        "Net Annual Profit": f"{stmt.net_profit:,.0f}" if stmt.net_profit is not None else "-",
                        "Total Assets": f"{stmt.total_assets:,.0f}" if stmt.total_assets is not None else "-",
                        "Total Equity": f"{stmt.total_equity:,.0f}" if stmt.total_equity is not None else "-",
                        "Total Debt": f"{stmt.total_debt:,.0f}" if stmt.total_debt is not None else "-",
                        "Filing ID": stmt.filing_id or "-",
                    })
                st.dataframe(pd.DataFrame(fin_rows), use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class='warning-box'>
                    <strong>No Commercial Financial Statements on Record:</strong>
                    This entity either has not filed annual accounts with Regnskapsregisteret (common for government agencies, municipalities, and newly registered sole proprietorships) or the filing is exempt under the Norwegian Accounting Act.
                </div>
                """, unsafe_allow_html=True)

        with tab_facts:
            st.markdown("<div class='sp-card'>", unsafe_allow_html=True)
            st.markdown(f"<h4 style='color: #1E3A8A; font-weight: 700;'>All Atomic Facts ({len(profile.facts)})</h4>", unsafe_allow_html=True)
            st.markdown("<p style='color: #64748B; font-size: 0.88rem;'>Every fact is stored with immutable provenance, source URL, UTC timestamp, and SHA-256 hash.</p>", unsafe_allow_html=True)
            
            fact_rows = []
            for fact in profile.facts:
                fact_rows.append({
                    "Field": fact.field_name,
                    "Value": str(fact.value)[:70],
                    "Source": fact.source_name,
                    "Source URL": fact.source_url,
                    "Status": fact.verification_status.value.upper(),
                    "Evidence Excerpt": fact.evidence_excerpt[:120] if fact.evidence_excerpt else "-",
                    "Retrieved At (UTC)": fact.retrieved_at[:19],
                })
            st.dataframe(pd.DataFrame(fact_rows), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with tab_changes:
            st.markdown("<div class='sp-card'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color: #1E3A8A; font-weight: 700;'>Detected Differences Across Research Runs</h4>", unsafe_allow_html=True)
            if profile.changes:
                ch_rows = []
                for ch in profile.changes:
                    ch_rows.append({
                        "Field": ch.field_name,
                        "Previous Value": str(ch.previous_value),
                        "New Value": str(ch.new_value),
                        "Change Classification": ch.change_type.value,
                        "Detected At": ch.detected_at[:19],
                        "Evidence": ch.evidence_reference,
                    })
                st.dataframe(pd.DataFrame(ch_rows), use_container_width=True)
            else:
                st.markdown("""
                <div class='explanation-box' style='background: #EFF6FF; border-left-color: #2563EB; color: #1E40AF;'>
                    <strong>✓ Profile Stable & Verified:</strong>
                    No differences detected against previous snapshots. Re-running research against unchanged public data produces 0 duplicate changes (strict idempotency guarantee).
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with tab_missing:
            st.markdown("<div class='sp-card'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color: #1E3A8A; font-weight: 700;'>Data Availability & Missing Fields</h4>", unsafe_allow_html=True)
            if profile.missing_fields:
                st.markdown("<p style='color: #64748B;'>The following standard fields could not be verified from public sources for this company:</p>", unsafe_allow_html=True)
                for mf in profile.missing_fields:
                    st.markdown(f"- <code style='color: #D97706;'>{mf}</code>", unsafe_allow_html=True)
            else:
                st.success("All core corporate fields successfully verified!")
            st.markdown("</div>", unsafe_allow_html=True)

# TAB 2: Batch Processing
elif view_mode == "Batch Processing":
    st.markdown("<h3 style='color: #1E3A8A; font-weight: 800;'>Batch Company Research</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B;'>Upload a CSV, JSON, or TXT file containing Norwegian organization numbers to research in parallel.</p>", unsafe_allow_html=True)

    st.markdown("<div class='sp-card'>", unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload Company List (CSV, JSON, JSONL, TXT)", type=["csv", "json", "jsonl", "txt"])
    concurrency_val = st.slider("Concurrency Level (Worker Threads)", min_value=1, max_value=8, value=3)

    if uploaded:
        content = uploaded.read().decode("utf-8")
        st.write(f"File loaded successfully ({len(content)} bytes).")

        if st.button("Execute Batch Intelligence Pipeline", type="primary"):
            temp_path = "data/input/uploaded_batch.txt"
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(content)

            with st.spinner("Executing bounded research pipeline..."):
                from signalpost.export import load_organization_numbers
                org_list = load_organization_numbers(temp_path)
                profiles, run = agent.research_batch(org_list, max_workers=concurrency_val)

            st.success(f"Batch completed! Processed {len(profiles)} terminal results.")
            st.json(run.model_dump())
    st.markdown("</div>", unsafe_allow_html=True)

# TAB 3: Historical Changes
elif view_mode == "Historical Audit & Changes":
    st.markdown("<h3 style='color: #1E3A8A; font-weight: 800;'>Historical Audit Trail & Change Detection</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B;'>Inspect granular corporate changes recorded in the SQLite database across historical snapshots.</p>", unsafe_allow_html=True)

    st.markdown("<div class='sp-card'>", unsafe_allow_html=True)
    audit_org = st.text_input("Enter Organization Number to Audit:", value="923609016")
    if st.button("Query Change Ledger", type="primary"):
        changes = db.get_changes_for_org(audit_org)
        if changes:
            st.dataframe(pd.DataFrame([c.model_dump() for c in changes]), use_container_width=True)
        else:
            st.info(f"No historical changes recorded for organization {audit_org}.")
    st.markdown("</div>", unsafe_allow_html=True)

# TAB 4: System Overview
elif view_mode == "System & Cost Overview":
    st.markdown("<h3 style='color: #1E3A8A; font-weight: 800;'>System Architecture & ₹0 Cost Accounting</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='sp-card'>
        <h4 style='color: #1E3A8A;'>100% Free-First Public Data Architecture</h4>
        <p style='color: #475569; line-height: 1.6;'>
            Signalpost achieves <strong>₹0 ($0.00) external API costs</strong> by communicating directly with official Norwegian open government services:
        </p>
        <ul>
            <li><strong>Brønnøysund Enhetsregisteret API:</strong> CC0 / NLOD Norwegian Open Government Data license.</li>
            <li><strong>Brønnøysund Regnskapsregisteret API:</strong> Statutory annual financial disclosures under the Norwegian Accounting Act.</li>
            <li><strong>Verified Company Websites:</strong> Direct safe HTTP extraction with strict Server-Side Request Forgery (SSRF) defense.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='sp-card'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #1E3A8A;'>Operational Budget Ledger</h4>", unsafe_allow_html=True)
    st.json(budget.get_summary())
    st.markdown("</div>", unsafe_allow_html=True)
