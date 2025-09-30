"""Core data models for publication search."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class Publication:
    """Represents a single publication search result."""

    title: str
    authors: List[str]
    abstract: Optional[str]
    doi: Optional[str]
    url: Optional[str]
    published: Optional[datetime]
    language: Optional[str]
    publisher: Optional[str]
    source: str
    publication_type: Optional[str]

    @property
    def year(self) -> Optional[str]:
        if self.published:
            return str(self.published.year)
        return None


@dataclass
class SearchFilters:
    """Represents the set of filters applied to a search."""

    keywords: List[str]
    authors: List[str]
    languages: List[str]
    publication_types: List[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
