"""Filter module for TigerNet scraper."""

from typing import Any


def build_query(company: str, orgs: list[str] | None) -> dict:
    """Build search parameters dict from company and orgs."""
    pass


def validate_orgs(orgs: list[str]) -> list[str]:
    """Normalize org list and warn on unknown orgs."""
    pass
