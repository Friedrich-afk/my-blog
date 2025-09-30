"""Search data source implementations."""
from __future__ import annotations

from typing import Dict, Iterable, List, Type

from ..models import Publication, SearchFilters

from .arxiv_source import ArxivSource
from .crossref_source import CrossrefSource
from .rss_source import RssSource

SOURCE_REGISTRY: Dict[str, Type["BaseSource"]] = {
    "crossref": CrossrefSource,
    "arxiv": ArxivSource,
    "rss": RssSource,
}


class BaseSource:
    """Base class for all search sources."""

    name: str = "Base"

    def __init__(self, options: Dict[str, str] | None = None) -> None:
        self.options = options or {}

    def search(self, filters: SearchFilters) -> Iterable[Publication]:
        raise NotImplementedError


def get_source(source_type: str, options: Dict[str, str] | None = None) -> BaseSource:
    """Instantiate a source by its type identifier."""

    if source_type not in SOURCE_REGISTRY:
        raise KeyError(f"Unknown source type: {source_type}")
    return SOURCE_REGISTRY[source_type](options=options)


def list_available_sources() -> List[str]:
    return list(SOURCE_REGISTRY.keys())
