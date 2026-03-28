"""CLI entrypoint for TigerNet scraper."""

import asyncio
import os
from pathlib import Path

import typer
from dotenv import load_dotenv

from .exporter import write_excel
from .scraper import search

app = typer.Typer()


def _load_env_credentials() -> tuple[str, str]:
    """Load credentials from .env file."""
    env_path = Path(".env")
    if not env_path.exists():
        typer.echo("Error: .env file not found.", err=True)
        typer.echo("Create a .env file with NETID and PASSWORD variables.", err=True)
        raise typer.Exit(1)

    load_dotenv(env_path)
    netid = os.getenv("NETID")
    password = os.getenv("PASSWORD")

    if not netid or not password:
        typer.echo("Error: NETID and PASSWORD must be set in .env file", err=True)
        raise typer.Exit(1)

    return netid, password


@app.command()
def scrape(
    netid: str | None = typer.Option(
        None, "--netid", help="NetID for TigerNet (optional if using --test)"
    ),
    password: str | None = typer.Option(
        None, "--password", help="Password for TigerNet (optional if using --test)"
    ),
    company: str = typer.Argument(..., help="Company name to search"),
    orgs: list[str] | None = typer.Option(
        None, "--org", help="Organization/department filter"
    ),
    output: str = typer.Option(
        "output/alumni.xlsx", "--output", "-o", help="Output Excel file path"
    ),
    test: bool = typer.Option(
        False, "--test", help="Use credentials from .env file instead of prompting"
    ),
    max_results: int = typer.Option(
        int(1e9), "--max", "-m", help="Maximum number of alumni records to scrape"
    ),
) -> None:
    # Handle credential acquisition
    if test:
        netid, password = _load_env_credentials()
    else:
        # If not using --test, use provided credentials or prompt
        if netid is None:
            netid = typer.prompt("NetID", hide_input=True)
        if password is None:
            password = typer.prompt("Password", hide_input=True)

    # Perform search (returns list of AlumRecord, exports to Excel internally)
    records = asyncio.run(
        search(
            netid=netid,
            password=password,
            company=company,
            orgs=orgs or [],
            max_results=max_results
        )
    )

    typer.echo(f"Completed: {len(records)} records scraped and exported.")


if __name__ == "__main__":
    app()
