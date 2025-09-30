"""Configuration management for publication search data sources."""
from __future__ import annotations

import json
import shutil
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

DEFAULT_SOURCES = [
    {
        "name": "Crossref",
        "type": "crossref",
        "enabled": True,
        "options": {},
    },
    {
        "name": "arXiv",
        "type": "arxiv",
        "enabled": True,
        "options": {},
    },
]

APP_DIR = Path.home() / ".publication_scout"
CONFIG_PATH = APP_DIR / "data_sources.json"
DEFAULT_CONFIG_BUNDLE = Path(__file__).resolve().parent / "data_sources.json"


@dataclass
class DataSource:
    """Represents a search data source definition."""

    name: str
    type: str
    enabled: bool = True
    options: Dict[str, str] = field(default_factory=dict)


class DataSourceConfig:
    """Thread-safe storage for data source configuration."""

    def __init__(
        self,
        path: Path = CONFIG_PATH,
        default_bundle: Path = DEFAULT_CONFIG_BUNDLE,
    ) -> None:
        self._path = path
        self._default_bundle = default_bundle
        self._lock = threading.Lock()
        if not self._path.exists():
            self._initialise()

    def _initialise(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if self._default_bundle.exists():
            shutil.copyfile(self._default_bundle, self._path)
            return
        self._write(DEFAULT_SOURCES)

    def _read(self) -> List[Dict[str, object]]:
        if not self._path.exists():
            return DEFAULT_SOURCES
        with self._path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _write(self, data: List[Dict[str, object]]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)

    def list_sources(self) -> List[DataSource]:
        with self._lock:
            data = self._read()
        return [DataSource(**item) for item in data]

    def save_sources(self, sources: List[DataSource]) -> None:
        serialisable = [
            {
                "name": source.name,
                "type": source.type,
                "enabled": source.enabled,
                "options": source.options,
            }
            for source in sources
        ]
        with self._lock:
            self._write(serialisable)

    def add_source(self, source: DataSource) -> None:
        sources = self.list_sources()
        sources.append(source)
        self.save_sources(sources)


def get_config(path: Path | None = None) -> DataSourceConfig:
    """Return a configuration instance for the provided path."""

    return DataSourceConfig(path or CONFIG_PATH)
