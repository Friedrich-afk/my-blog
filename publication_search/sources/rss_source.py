"""Generic RSS/Atom source."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Iterable, List

import feedparser

from ..models import Publication, SearchFilters
from . import BaseSource

LOGGER = logging.getLogger(__name__)


class RssSource(BaseSource):
    """Fetch publications from an RSS/Atom feed."""

    name = "RSS"

    def search(self, filters: SearchFilters) -> Iterable[Publication]:
        feed_url = self.options.get("url")
        if not feed_url:
            LOGGER.warning("RSS source missing URL option")
            return []
        try:
            feed = feedparser.parse(feed_url)
        except Exception as exc:  # pragma: no cover - network
            LOGGER.warning("RSS request failed: %s", exc)
            return []

        publications: List[Publication] = []
        for entry in feed.entries:
            published = None
            if entry.get("published_parsed"):
                try:
                    published = datetime(*entry.published_parsed[:6])
                except Exception:  # pragma: no cover - parsing guard
                    published = None
            publication = Publication(
                title=entry.get("title", "").strip(),
                authors=[entry.get("author")] if entry.get("author") else [],
                abstract=entry.get("summary"),
                doi=None,
                url=entry.get("link"),
                published=published,
                language=self.options.get("language"),
                publisher=feed.feed.get("title"),
                source=self.options.get("name", self.name),
                publication_type=self.options.get("format"),
            )
            if self._matches_filters(publication, filters):
                publications.append(publication)
        return publications

    def _matches_filters(self, publication: Publication, filters: SearchFilters) -> bool:
        if filters.languages and publication.language:
            if publication.language not in filters.languages:
                return False
        if filters.start_date and publication.published:
            if publication.published.date() < filters.start_date.date():
                return False
        if filters.end_date and publication.published:
            if publication.published.date() > filters.end_date.date():
                return False
        if filters.keywords and publication.title:
            title_lower = publication.title.lower()
            if not any(keyword.lower() in title_lower for keyword in filters.keywords):
                return False
        if filters.authors and publication.authors:
            lower_authors = [author.lower() for author in publication.authors]
            if not any(author.lower() in lower_authors for author in filters.authors):
                return False
        return True
