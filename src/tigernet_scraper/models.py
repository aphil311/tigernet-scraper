"""Models module for TigerNet scraper."""

from dataclasses import dataclass


@dataclass
class AlumRecord:
    """Represents a TigerNet alumni record."""

    name: str
    class_year: int | None
    degree: str | None
    company: str | None
    title: str | None
    org: str | None  # concentration/dept
    email: str | None
    linkedin: str | None
    location: str | None
