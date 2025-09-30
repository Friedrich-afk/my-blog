"""Crossref search source implementation."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Iterable, List

import requests

from ..models import Publication, SearchFilters
from ..utils import format_publication_date
from . import BaseSource

LOGGER = logging.getLogger(__name__)


class CrossrefSource(BaseSource):
    """Search publications using the Crossref REST API."""

    name = "Crossref"
    API_URL = "https://api.crossref.org/works"

    def search(self, filters: SearchFilters) -> Iterable[Publication]:
        params = self._build_params(filters)
        try:
            response = requests.get(self.API_URL, params=params, timeout=20)
            response.raise_for_status()
        except requests.RequestException as exc:  # pragma: no cover - network
            LOGGER.warning("Crossref request failed: %s", exc)
            return []

        payload = response.json()
        items: List[dict] = payload.get("message", {}).get("items", [])
        publications: List[Publication] = []
        for item in items:
            published = format_publication_date(item.get("issued", {}).get("date-parts", [None])[0])
            publication = Publication(
                title=item.get("title", [""])[0],
                authors=[
                    " ".join(filter(None, [author.get("given"), author.get("family")]))
                    for author in item.get("author", [])
                ],
                abstract=item.get("abstract"),
                doi=item.get("DOI"),
                url=item.get("URL"),
                published=published,
                language=item.get("language"),
                publisher=item.get("container-title", [item.get("publisher", "Crossref")])[0],
                source=self.name,
                publication_type=item.get("type"),
            )
            publications.append(publication)
        return publications

    def _build_params(self, filters: SearchFilters) -> dict:
        params: dict = {
            "rows": self.options.get("rows", 50),
        }
        if filters.keywords:
            params["query"] = " ".join(filters.keywords)
        if filters.authors:
            params["query.author"] = " ".join(filters.authors)
        if filters.languages:
            params["filter"] = ",".join([f"language:{lang}" for lang in filters.languages])
        if filters.publication_types:
            params.setdefault("filter", "")
            clauses = params["filter"].split(",") if params["filter"] else []
            clauses.extend(f"type:{pub_type}" for pub_type in filters.publication_types)
            params["filter"] = ",".join(clauses)
        date_filters = []
        if filters.start_date:
            date_filters.append(f"from-pub-date:{filters.start_date.date()}" )
        if filters.end_date:
            date_filters.append(f"until-pub-date:{filters.end_date.date()}" )
        if date_filters:
            params.setdefault("filter", "")
            clauses = params["filter"].split(",") if params["filter"] else []
            clauses.extend(date_filters)
            params["filter"] = ",".join(clauses)
        return params
