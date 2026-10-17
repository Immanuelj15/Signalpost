"""Export and input formatting adapter: handles CSV, JSON, JSONL, and rich terminal formatting."""

import csv
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from signalpost.models import CompanyProfile, ResearchRun

console = Console()


def load_organization_numbers(input_path: str) -> List[str]:
    """
    Load organization numbers from a file (CSV, JSON, or JSONL).
    Accepts:
    - CSV files with header (e.g. 'orgnr', 'organisasjonsnummer', 'organization_number', 'org_nr') or single column
    - JSON files (list of numbers or list of dicts with 'orgnr')
    - JSONL files (one json object or string per line)
    - Plain text files (one number per line)
    """
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    orgs: List[str] = []
    suffix = path.suffix.lower()

    if suffix == ".csv":
        with open(path, mode="r", encoding="utf-8-sig") as f:
            # Check if there is a header
            sample = f.read(2048)
            f.seek(0)
            has_header = False
            try:
                has_header = csv.Sniffer().has_header(sample)
            except Exception:
                has_header = False

            reader = csv.reader(f)
            first_row = next(reader, None)
            if not first_row:
                return []

            # Determine column index
            col_idx = 0
            if has_header:
                headers = [h.strip().lower() for h in first_row]
                match_cols = ["orgnr", "organisasjonsnummer", "organization_number", "org_nr", "org", "id"]
                found = False
                for target in match_cols:
                    if target in headers:
                        col_idx = headers.index(target)
                        found = True
                        break
                # If header was matched, process subsequent rows
                for row in reader:
                    if row and len(row) > col_idx:
                        val = row[col_idx].strip()
                        if val:
                            orgs.append(val)
            else:
                # First row was data
                if first_row and len(first_row) > 0:
                    orgs.append(first_row[0].strip())
                for row in reader:
                    if row and len(row) > 0:
                        val = row[0].strip()
                        if val:
                            orgs.append(val)

    elif suffix == ".json":
        with open(path, mode="r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        for k in ["organisasjonsnummer", "orgnr", "organization_number", "org"]:
                            if k in item:
                                orgs.append(str(item[k]))
                                break
                    elif isinstance(item, (str, int)):
                        orgs.append(str(item))
            elif isinstance(data, dict):
                for k in ["organizations", "companies", "orgs"]:
                    if k in data and isinstance(data[k], list):
                        orgs.extend([str(x) for x in data[k]])
                        break

    elif suffix in (".jsonl", ".txt"):
        with open(path, mode="r", encoding="utf-8") as f:
            for line in f:
                line_str = line.strip()
                if not line_str:
                    continue
                if line_str.startswith("{"):
                    try:
                        obj = json.loads(line_str)
                        for k in ["organisasjonsnummer", "orgnr", "organization_number"]:
                            if k in obj:
                                orgs.append(str(obj[k]))
                                break
                    except Exception:
                        pass
                else:
                    orgs.append(line_str)
    else:
        # Default fallback: line by line
        with open(path, mode="r", encoding="utf-8") as f:
            for line in f:
                val = line.strip()
                if val:
                    orgs.append(val)

    return orgs


def export_profiles_json(profiles: List[CompanyProfile], output_path: str):
    """Export profiles to formatted JSON."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    payload = [p.model_dump() for p in profiles]
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def export_profiles_jsonl(profiles: List[CompanyProfile], output_path: str):
    """Export profiles to JSON Lines (one JSON object per line)."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for p in profiles:
            f.write(p.model_dump_json() + "\n")


def export_profiles_csv(profiles: List[CompanyProfile], output_path: str):
    """Export flattened company records to CSV."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "organization_number",
        "official_name",
        "organization_type",
        "status",
        "registration_date",
        "incorporation_date",
        "municipality",
        "city",
        "employees",
        "website",
        "latest_revenue_nok",
        "latest_operating_profit_nok",
        "latest_net_profit_nok",
        "latest_reporting_period",
        "identity_status",
        "research_status",
        "facts_count",
        "changes_count",
        "last_researched_at",
    ]

    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in profiles:
            c = p.company
            b_addr = c.business_address
            latest_fin = p.financials[0] if p.financials else None

            writer.writerow({
                "organization_number": p.organization_number,
                "official_name": c.official_name or "",
                "organization_type": c.organization_type or "",
                "status": c.status or "",
                "registration_date": c.registration_date or "",
                "incorporation_date": c.incorporation_date or "",
                "municipality": b_addr.municipality if b_addr else "",
                "city": b_addr.city if b_addr else "",
                "employees": c.employees if c.employees is not None else "",
                "website": c.website or "",
                "latest_revenue_nok": latest_fin.total_revenue if latest_fin and latest_fin.total_revenue is not None else "",
                "latest_operating_profit_nok": latest_fin.operating_profit if latest_fin and latest_fin.operating_profit is not None else "",
                "latest_net_profit_nok": latest_fin.net_profit if latest_fin and latest_fin.net_profit is not None else "",
                "latest_reporting_period": latest_fin.reporting_period if latest_fin else "",
                "identity_status": p.identity_status.value,
                "research_status": p.research_status.value,
                "facts_count": len(p.facts),
                "changes_count": len(p.changes),
                "last_researched_at": p.last_researched_at or "",
            })


def display_profile_summary(profile: CompanyProfile):
    """Print an attractive summary table to terminal using Rich."""
    c = profile.company
    title = f"[bold cyan]Signalpost Profile: {c.official_name or 'Unknown'} ({profile.organization_number})[/bold cyan]"

    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("Property", style="dim", width=24)
    table.add_column("Verified Value", style="bold white")

    table.add_row("Organization Number", profile.organization_number)
    table.add_row("Official Name", c.official_name or "[red]Not found[/red]")
    table.add_row("Status", c.status or "Unknown")
    table.add_row("Organization Type", f"{c.organization_type or ''} ({c.organization_type_description or ''})")
    table.add_row("Registration Date", c.registration_date or "N/A")

    if c.business_address:
        addr_str = f"{', '.join(c.business_address.address)}, {c.business_address.postal_code or ''} {c.business_address.city or ''} ({c.business_address.municipality or ''})"
        table.add_row("Business Address", addr_str)

    if c.employees is not None:
        table.add_row("Employees", f"{c.employees:,}")
    if c.website:
        table.add_row("Official Website", c.website)

    if profile.financials:
        f = profile.financials[0]
        rev = f"{f.total_revenue:,.0f} {f.currency}" if f.total_revenue is not None else "N/A"
        ebit = f"{f.operating_profit:,.0f} {f.currency}" if f.operating_profit is not None else "N/A"
        net = f"{f.net_profit:,.0f} {f.currency}" if f.net_profit is not None else "N/A"
        table.add_row("Latest Financials", f"Period: {f.reporting_period} | Rev: {rev} | EBIT: {ebit} | Net: {net}")

    table.add_row("Identity Status", f"[green]{profile.identity_status.value}[/green]" if profile.identity_status.value == "verified" else f"[red]{profile.identity_status.value}[/red]")
    table.add_row("Research Status", profile.research_status.value)
    table.add_row("Total Verified Facts", str(len(profile.facts)))
    table.add_row("Detected Changes", str(len(profile.changes)))

    console.print(table)

    if profile.changes:
        ch_table = Table(title="[bold yellow]Historical Changes Detected[/bold yellow]")
        ch_table.add_column("Field", style="cyan")
        ch_table.add_column("Previous Value", style="dim")
        ch_table.add_column("New Value", style="bold green")
        ch_table.add_column("Change Type")
        for ch in profile.changes:
            ch_table.add_row(ch.field_name, str(ch.previous_value), str(ch.new_value), ch.change_type.value)
        console.print(ch_table)

    if profile.explanations:
        expl_text = "\n".join(f"- {e}" for e in profile.explanations)
        console.print(Panel(expl_text, title="[bold green]Evidence Grounded Explanations[/bold green]", expand=False))
