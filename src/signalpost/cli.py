"""Command Line Interface for Signalpost using Typer."""

import sys
import json
import logging
from typing import Optional
from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table

from signalpost.database import db
from signalpost.orchestrator import ResearchAgent
from signalpost.export import (
    load_organization_numbers,
    export_profiles_json,
    export_profiles_jsonl,
    export_profiles_csv,
    display_profile_summary,
)
from signalpost.request_budget import budget

# Configure UTF-8 stdout on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

app = typer.Typer(
    name="signalpost",
    help="Signalpost: Evidence-First Norwegian Company Intelligence Agent",
    add_completion=False,
)
console = Console()
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


@app.command("init-db")
def init_database():
    """Initialize SQLite database with required tables, indexes, and schema versions."""
    console.print("[bold blue]Initializing Signalpost database...[/bold blue]")
    db.init_db()
    console.print(f"[bold green][OK] Database initialized successfully at:[/bold green] {db.db_path}")


@app.command("research")
def research(
    org: str = typer.Option(..., "--org", "-o", help="Norwegian organization number (9 digits)"),
    refresh: bool = typer.Option(False, "--refresh", "-r", help="Force fresh retrieval from public sources"),
    output: Optional[str] = typer.Option(None, "--output", help="Optional path to save profile JSON"),
):
    """Research a single Norwegian company by organization number."""
    db.init_db()
    agent = ResearchAgent(database=db)
    console.print(f"[cyan]Researching organization {org}...[/cyan]")
    
    profile = agent.research_company(org, force_refresh=refresh)
    display_profile_summary(profile)

    if output:
        out_path = Path(output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(profile.model_dump_json(indent=2))
        console.print(f"[green][OK] Saved full profile to {output}[/green]")

    b_summary = budget.get_summary()
    console.print(f"[dim]Outbound requests: {b_summary['total_outbound_requests']} | External API cost: ${b_summary['total_external_cost_usd']:.2f}[/dim]")


@app.command("batch")
def batch(
    input_file: str = typer.Option(..., "--input", "-i", help="Path to input CSV, JSON, or JSONL file containing org numbers"),
    output_file: str = typer.Option("data/output/results.jsonl", "--output", "-o", help="Path to write output results (JSON, JSONL, or CSV)"),
    concurrency: int = typer.Option(5, "--concurrency", "-c", help="Number of concurrent worker threads"),
    refresh: bool = typer.Option(False, "--refresh", "-r", help="Force fresh retrieval from sources"),
):
    """Research a batch of companies from an input file."""
    db.init_db()
    agent = ResearchAgent(database=db)
    
    try:
        org_numbers = load_organization_numbers(input_file)
    except Exception as e:
        console.print(f"[bold red]Failed to load input file:[/bold red] {e}")
        raise typer.Exit(code=1)

    console.print(f"[bold blue]Processing batch of {len(org_numbers)} organizations from {input_file}...[/bold blue]")
    
    profiles, run = agent.research_batch(
        raw_orgs=org_numbers,
        max_workers=concurrency,
        force_refresh=refresh,
    )

    # Export results
    out_lower = output_file.lower()
    if out_lower.endswith(".jsonl"):
        export_profiles_jsonl(profiles, output_file)
    elif out_lower.endswith(".csv"):
        export_profiles_csv(profiles, output_file)
    else:
        export_profiles_json(profiles, output_file)

    console.print(f"[bold green][OK] Batch complete! Produced {len(profiles)} terminal results.[/bold green]")
    console.print(f"Results written to: [bold underline]{output_file}[/bold underline]")

    # Print summary metrics table
    summary_table = Table(title="Batch Run Summary", show_header=True)
    summary_table.add_column("Metric", style="dim")
    summary_table.add_column("Value", style="bold white")

    resolved_count = sum(1 for p in profiles if p.identity_status.value == "verified")
    partial_count = sum(1 for p in profiles if p.research_status.value == "partial")
    failed_count = sum(1 for p in profiles if p.research_status.value == "failed")
    changes_count = sum(len(p.changes) for p in profiles)

    summary_table.add_row("Total Companies Processed", str(len(profiles)))
    summary_table.add_row("Fully/Partially Resolved", f"{resolved_count}")
    summary_table.add_row("Partial Info Coverage", f"{partial_count}")
    summary_table.add_row("Failed / Invalid / Not Found", f"{failed_count}")
    summary_table.add_row("Total Changes Detected", str(changes_count))
    summary_table.add_row("Outbound Requests Used", str(run.requests_used))
    summary_table.add_row("Measured External API Cost", f"${run.external_api_cost_usd:.4f} (₹0.00)")

    console.print(summary_table)


@app.command("refresh")
def refresh(
    input_file: str = typer.Option(..., "--input", "-i", help="Path to input CSV/JSON file to refresh"),
    output_file: str = typer.Option("data/output/refreshed_results.jsonl", "--output", "-o", help="Output destination"),
    concurrency: int = typer.Option(5, "--concurrency", "-c", help="Concurrency level"),
):
    """Refresh previously researched companies and detect changes over time."""
    batch(input_file=input_file, output_file=output_file, concurrency=concurrency, refresh=True)


@app.command("history")
def history(
    org: str = typer.Option(..., "--org", "-o", help="Norwegian organization number"),
):
    """Inspect historical changes and audit trail for a company."""
    db.init_db()
    changes = db.get_changes_for_org(org)
    if not changes:
        console.print(f"[yellow]No historical changes recorded for organization {org}.[/yellow]")
        return

    table = Table(title=f"Historical Changes Audit: {org}", show_header=True, header_style="bold yellow")
    table.add_column("Detected At", style="dim")
    table.add_column("Field", style="cyan")
    table.add_column("Previous Value", style="red")
    table.add_column("New Value", style="green")
    table.add_column("Type", style="magenta")
    table.add_column("Evidence Reference", style="italic")

    for ch in changes:
        table.add_row(
            ch.detected_at[:19],
            ch.field_name,
            str(ch.previous_value)[:40],
            str(ch.new_value)[:40],
            ch.change_type.value,
            str(ch.evidence_reference)[:60],
        )

    console.print(table)


@app.command("export")
def export(
    org: str = typer.Option(..., "--org", "-o", help="Organization number"),
    fmt: str = typer.Option("json", "--format", "-f", help="Output format: json, csv"),
    output: Optional[str] = typer.Option(None, "--output", help="Output file path"),
):
    """Export stored company profile to JSON or CSV."""
    db.init_db()
    profile = db.get_company(org)
    if not profile:
        console.print(f"[red]Company {org} not found in database.[/red]")
        raise typer.Exit(code=1)

    out_file = output or f"data/output/{org}.{fmt}"
    if fmt.lower() == "csv":
        export_profiles_csv([profile], out_file)
    else:
        export_profiles_json([profile], out_file)
    console.print(f"[green][OK] Exported profile to {out_file}[/green]")


@app.command("serve")
def serve(
    host: str = typer.Option("127.0.0.1", "--host", help="API host interface"),
    port: int = typer.Option(8000, "--port", "-p", help="API port"),
):
    """Run optional FastAPI server for Signalpost agent."""
    import uvicorn
    console.print(f"[bold cyan]Starting Signalpost API server on {host}:{port}...[/bold cyan]")
    uvicorn.run("signalpost.api:app", host=host, port=port, reload=False)


def main():
    app()


if __name__ == "__main__":
    main()
