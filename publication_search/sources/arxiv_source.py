"""arXiv search source implementation."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Iterable, List

import feedparser

from ..models import Publication, SearchFilters
from ..utils import normalise_list
from . import BaseSource

LOGGER = logging.getLogger(__name__)


class ArxivSource(BaseSource):
    """Search arXiv using its Atom feed."""

    name = "arXiv"
    API_URL = "http://export.arxiv.org/api/query"

    def search(self, filters: SearchFilters) -> Iterable[Publication]:
        query = self._build_query(filters)
        params = {
            "search_query": query or "all",
            "start": 0,
            "max_results": int(self.options.get("max_results", 50)),
        }
        try:
            feed = feedparser.parse(self.API_URL, params=params)
        except Exception as exc:  # pragma: no cover - network
            LOGGER.warning("arXiv request failed: %s", exc)
            return []

        publications: List[Publication] = []
        for entry in feed.entries:
            published = None
            if entry.get("published"):
                try:
                    published = datetime.strptime(entry.published, "%Y-%m-%dT%H:%M:%SZ")
                except ValueError:
                    published = None
            publication = Publication(
                title=entry.get("title", "").strip(),
                authors=[author.name for author in entry.get("authors", [])],
                abstract=entry.get("summary"),
                doi=entry.get("arxiv_doi"),
                url=entry.get("link"),
                published=published,
                language="en",
                publisher=entry.get("arxiv_primary_category", {}).get("term"),
                source=self.name,
                publication_type="preprint",
            )
            publications.append(publication)
        return publications

    def _build_query(self, filters: SearchFilters) -> str:
        terms: List[str] = []
        if filters.keywords:
            terms.extend(f"all:{keyword}" for keyword in filters.keywords)
        if filters.authors:
            terms.extend(f"au:{author}" for author in filters.authors)
        if filters.publication_types:
            allowed = normalise_list(filters.publication_types)
            terms.extend(f"cat:{pub_type}" for pub_type in allowed)
        return "+AND+".join(terms)
