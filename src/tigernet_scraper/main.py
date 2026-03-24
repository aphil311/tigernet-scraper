"""CLI entrypoint for TigerNet scraper."""

import typer

from .auth import login, load_session, save_session
from .exporter import write_excel
from .models import AlumRecord
from .scraper import search

app = typer.Typer()


@app.command()
def scrape(
    netid: str = typer.Option(..., prompt=True, hide_input=True),
    password: str = typer.Option(..., prompt=True, hide_input=True),
    company: str = typer.Argument(..., help="Company name to search"),
    orgs: list[str] | None = typer.Option(
        None, "--org", help="Organization/department filter"
    ),
    output: str = typer.Option(
        "output/alumni.xlsx", "--output", "-o", help="Output Excel file path"
    ),
) -> None:

    # Perform search (returns empty list for now)
    records = search(
        netid=netid,
        password=password,
        company=company,
        orgs=orgs or [],
    )

    # Export to Excel (will create empty file if no records)
    output_path = write_excel(records, output)
    typer.echo(f"Exported {len(records)} records to {output_path}")


if __name__ == "__main__":
    app()
