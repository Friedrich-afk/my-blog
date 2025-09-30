"""Utility helpers for formatting and normalising data."""
from __future__ import annotations

from datetime import datetime
from typing import Iterable, List

from .models import Publication


def normalise_list(values: Iterable[str]) -> List[str]:
    """Return a list of trimmed, non-empty strings."""

    return [value.strip() for value in values if value and value.strip()]


def chicago_citation(publication: Publication) -> str:
    """Generate a Chicago-style reference string."""

    authors = ", ".join(publication.authors) if publication.authors else ""
    title = publication.title
    publisher = publication.publisher or ""
    year = publication.year or "n.d."
    container = publisher if publisher else publication.source
    url = publication.url or ""

    citation = f"{authors}. \"{title}.\" {container}, {year}."
    if url:
        citation += f" {url}"
    if publication.doi:
        citation += f" DOI: {publication.doi}"
    return citation


def format_publication_date(date_parts: List[int] | None) -> datetime | None:
    """Convert a date parts list to a datetime object."""

    if not date_parts:
        return None
    year = date_parts[0]
    month = date_parts[1] if len(date_parts) > 1 else 1
    day = date_parts[2] if len(date_parts) > 2 else 1
    try:
        return datetime(year, month, day)
    except ValueError:
        return None
