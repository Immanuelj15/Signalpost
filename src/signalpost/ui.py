"""Streamlit dashboard for Signalpost: Evidence-First Norwegian Company Intelligence Agent."""

import json
import streamlit as st
import pandas as pd

from signalpost.database import db
from signalpost.orchestrator import ResearchAgent
from signalpost.export import export_profiles_csv
from signalpost.request_budget import budget

st.set_page_config(
    page_title="Signalpost | Norwegian Company Intelligence",
    page_icon="🇳🇴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize DB
db.init_db()
agent = ResearchAgent(database=db)

# Sidebar
st.sidebar.title("🇳🇴 Signalpost")
st.sidebar.caption("Evidence-First Norwegian Company Intelligence Agent")
st.sidebar.markdown("---")

b_summary = budget.get_summary()
st.sidebar.metric("Outbound Requests Used", f"{b_summary['total_outbound_requests']} / {b_summary['max_allowed_requests']}")
st.sidebar.metric("Measured API Cost", f"${b_summary['total_external_cost_usd']:.4f} (₹0.00)")
st.sidebar.metric("Companies in DB", db.count_companies())

st.sidebar.markdown("---")
view_mode = st.sidebar.radio("Navigation", ["Company Research", "Batch Processing", "Historical Audit & Changes", "System & Cost Overview"])

# Tab 1: Company Research
if view_mode == "Company Research":
    st.title("🔍 Company Intelligence Research")
    st.markdown("Accepts Norwegian 9-digit organization numbers (*organisasjonsnummer*). Sources facts directly from Brønnøysund Enhetsregisteret, Regnskapsregisteret, and official company sites.")

    col1, col2 = st.columns([3, 1])
    with col1:
        org_input = st.text_input("Enter 9-digit Organization Number", value="923609016", help="Example: 923609016, 984851006")
    with col2:
        st.write("")
        st.write("")
        refresh_check = st.checkbox("Force fresh retrieval", value=False)

    if st.button("Run Research Agent", type="primary"):
        with st.spinner(f"Researching public sources for organization {org_input}..."):
            profile = agent.research_company(org_input, force_refresh=refresh_check)

        comp = profile.company
        status_color = "green" if profile.identity_status.value == "verified" else "red"
        st.markdown(f"### **{comp.official_name or 'Unknown'}** (`{profile.organization_number}`) :badge[{profile.identity_status.value.upper()}]{{{status_color}}}")

        # Metrics overview
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Status", comp.status or "Unknown")
        m2.metric("Org Type", comp.organization_type or "N/A")
        m3.metric("Employees", f"{comp.employees:,}" if comp.employees is not None else "N/A")
        m4.metric("Verified Facts", len(profile.facts))

        tab_profile, tab_financials, tab_facts, tab_changes, tab_missing = st.tabs(
            ["Overview", "Financial Accounts", "Attributable Facts", "Changes & Diffs", "Missing Fields"]
        )

        with tab_profile:
            pcol1, pcol2 = st.columns(2)
            with pcol1:
                st.subheader("Core Attributes")
                st.write(f"**Registration Date:** {comp.registration_date or 'N/A'}")
                st.write(f"**Incorporation Date:** {comp.incorporation_date or 'N/A'}")
                st.write(f"**Website:** {comp.website or 'N/A'}")
                st.write(f"**Parent Org:** {comp.parent_organization or 'None'}")
                st.write(f"**Bankruptcy:** {'Yes' if comp.is_in_bankruptcy else 'No'}")
                st.write(f"**In Liquidation:** {'Yes' if comp.is_in_liquidation else 'No'}")
            with pcol2:
                st.subheader("Business Address")
                if comp.business_address:
                    b = comp.business_address
                    st.write(f"**Street:** {', '.join(b.address)}")
                    st.write(f"**Postal Code & City:** {b.postal_code or ''} {b.city or ''}")
                    st.write(f"**Municipality:** {b.municipality or ''} (code {b.municipality_number or ''})")
                    st.write(f"**Country:** {b.country or 'Norge'}")
                else:
                    st.info("No business address available")

            if comp.business_activity:
                st.subheader("Registered Business Activities")
                for act in comp.business_activity:
                    st.markdown(f"- {act}")

            if comp.products_and_services:
                st.subheader("Products & Services Discovered")
                for prod in comp.products_and_services:
                    st.markdown(f"- {prod}")

            if profile.explanations:
                st.subheader("Evidence-Grounded Explanations")
                for exp in profile.explanations:
                    st.info(exp)

        with tab_financials:
            if profile.financials:
                st.subheader("Annual Financial Accounts (Regnskapsregisteret)")
                fin_rows = []
                for f in profile.financials:
                    fin_rows.append({
                        "Period": f.reporting_period,
                        "Type": f.statement_type,
                        "Currency": f.currency,
                        "Revenue": f.total_revenue,
                        "EBIT (Operating Profit)": f.operating_profit,
                        "Net Profit": f.net_profit,
                        "Total Assets": f.total_assets,
                        "Total Equity": f.total_equity,
                        "Total Debt": f.total_debt,
                        "Filing ID": f.filing_id,
                    })
                df_fin = pd.DataFrame(fin_rows)
                st.dataframe(df_fin, use_container_width=True)
            else:
                st.warning("No annual financial accounts published or accessible for this entity.")

        with tab_facts:
            st.subheader(f"All Atomic Facts ({len(profile.facts)})")
            facts_data = []
            for f in profile.facts:
                facts_data.append({
                    "Field": f.field_name,
                    "Value": str(f.value)[:80],
                    "Source": f.source_name,
                    "URL": f.source_url,
                    "Reporting Period": f.reporting_period or "-",
                    "Status": f.verification_status.value,
                    "Evidence": f.evidence_excerpt,
                    "Retrieved At": f.retrieved_at[:19],
                })
            st.dataframe(pd.DataFrame(facts_data), use_container_width=True)

        with tab_changes:
            st.subheader("Historical Changes Detected")
            if profile.changes:
                ch_data = []
                for ch in profile.changes:
                    ch_data.append({
                        "Field": ch.field_name,
                        "Previous": str(ch.previous_value),
                        "New": str(ch.new_value),
                        "Type": ch.change_type.value,
                        "Detected At": ch.detected_at[:19],
                        "Evidence": ch.evidence_reference,
                    })
                st.dataframe(pd.DataFrame(ch_data), use_container_width=True)
            else:
                st.success("No differences detected against previous snapshots. Profile is stable.")

        with tab_missing:
            st.subheader("Missing Fields Summary")
            if profile.missing_fields:
                st.warning(f"{len(profile.missing_fields)} fields could not be verified from public sources:")
                for mf in profile.missing_fields:
                    st.markdown(f"- `{mf}`")
            else:
                st.success("All core profile fields have been successfully verified!")

# Tab 2: Batch Processing
elif view_mode == "Batch Processing":
    st.title("📁 Batch Company Research")
    st.markdown("Upload a CSV, JSON, or text file containing Norwegian organization numbers to process in batch.")

    uploaded = st.file_uploader("Upload Company List (CSV, JSON, TXT)", type=["csv", "json", "jsonl", "txt"])
    concurrency_val = st.slider("Concurrency Workers", min_value=1, max_value=10, value=5)

    if uploaded:
        content = uploaded.read().decode("utf-8")
        lines = [l.strip() for l in content.splitlines() if l.strip()]
        st.write(f"Loaded {len(lines)} lines from file.")

        if st.button("Execute Batch Run", type="primary"):
            # Write temp file and run
            temp_path = "data/input/batch_uploaded.txt"
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(content)

            with st.spinner("Processing batch..."):
                from signalpost.export import load_organization_numbers
                org_list = load_organization_numbers(temp_path)
                profiles, run = agent.research_batch(org_list, max_workers=concurrency_val)

            st.success(f"Batch completed! Processed {len(profiles)} companies.")
            st.json(run.model_dump())

# Tab 3: Historical Changes
elif view_mode == "Historical Audit & Changes":
    st.title("⏱️ Historical Audit Trail & Change Detection")
    audit_org = st.text_input("Look up change audit for Org Number:", value="923609016")
    if st.button("Lookup Changes"):
        changes = db.get_changes_for_org(audit_org)
        if changes:
            st.dataframe(pd.DataFrame([c.model_dump() for c in changes]), use_container_width=True)
        else:
            st.info(f"No changes recorded for {audit_org}.")

# Tab 4: System Overview
elif view_mode == "System & Cost Overview":
    st.title("⚙️ System Status & ₹0 Cost Accounting")
    st.markdown("""
    Signalpost executes **100% free-first** by extracting structured public data directly from:
    - **Brønnøysund Enhetsregisteret API** (Official Norwegian Business Registry, CC0/NLOD open government license)
    - **Brønnøysund Regnskapsregisteret API** (Official Annual Financial Accounts, open public access)
    - **Permitted company websites** (Rule-based parsing with SSRF protection)
    """)
    st.json(budget.get_summary())
