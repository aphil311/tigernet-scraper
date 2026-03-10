import typer

app = typer.Typer(
    name="tigernet-scraper",
    help="Simple web scraper for TigerNet",
    add_completion=False,
)


@app.command()
def scrape(
    company: str = typer.Argument(..., help="Company to scrape"),
    organizations: list[str] | None = typer.Option(
        None, "--org", "-o", help="Organizations to scrape"
    ),
) -> None:
    """Scrape company data from TigerNet.

    Args:
        company: The company name to scrape
        organizations: Optional list of organizations to scrape
    """
    typer.echo(f"Company: {company}")
    if organizations:
        typer.echo(f"Organizations: {organizations}")


if __name__ == "__main__":
    app()
