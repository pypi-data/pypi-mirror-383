"""Fetch and cache Wikipedia metadata referenced in MkDocs pages."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import click
import requests
from mkdocs.utils import log
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from ruamel.yaml import YAML


class ThumbnailModel(BaseModel):
    """Model for Wikipedia thumbnail data."""
    source: str
    width: int
    height: int


class WikipediaEntryModel(BaseModel):
    """Model for a Wikipedia entry."""
    title: str
    tid: str | None = None
    description: str | None = None
    extract: str | None = None
    key: str | None = None
    thumbnail: ThumbnailModel | None = None
    timestamp: str | None = None
    plainlink: str | None = None


class WikipediaCacheModel(BaseModel):
    """Model for the Wikipedia cache file."""
    model_config = ConfigDict(extra="forbid")

    version: str = Field(default="0.2")
    wikipedia: dict[str, WikipediaEntryModel] = Field(default_factory=dict)


class Wikipedia:
    """Lightweight wrapper around the Wikipedia API with local caching."""

    def __init__(
        self,
        filename: Path | str = Path("links.yml"),
        lang: str = "en",
        domain: str = "wikipedia.org",
        timeout: int = 5,
    ) -> None:
        self.filename = Path(filename)
        self.language = lang
        self.domain = domain.strip().lower()
        self.timeout = timeout
        self.headers = {
            "User-Agent": "MkDocs-Wikipedia/1.0 (+https://github.com/yves-chevallier/mkdocs-wikipedia)"
        }
        self.data: dict[str, Any] = {}
        self._update_endpoints()

    def configure(
        self,
        *,
        language: str | None = None,
        domain: str | None = None,
        timeout: int | None = None,
    ) -> None:
        """Update runtime settings and recompute API endpoints."""

        if language is not None:
            self.language = language
        if domain is not None:
            self.domain = domain.strip().lower()
        if timeout is not None:
            self.timeout = timeout

        self._update_endpoints()

    def _update_endpoints(self) -> None:
        """Recompute derived URLs from the current configuration."""

        self.base_url = self._build_base_url()
        self.search_url = f"{self.base_url}/w/api.php"

    def _build_base_url(self, language: str | None = None) -> str:
        """Construct the base URL for the configured domain and language."""

        lang = (language if language is not None else self.language) or ""
        lang = lang.strip()
        if lang:
            return f"https://{lang}.{self.domain}".rstrip(".")
        return f"https://{self.domain}"

    def build_page_url(self, title: str, language: str | None = None) -> str:
        """Return the canonical page URL for a given title."""

        return f"{self._build_base_url(language)}/wiki/{title}"

    def get_api_url(self, language: str | None = None) -> str:
        """Return the REST API endpoint for the given language."""

        return f"{self._build_base_url(language)}/api/rest_v1"

    def search_from_keyword(
        self,
        keyword: str,
        limit: int = 5,
        interactive: bool = False,
    ) -> dict[str, str] | None:
        """Retrieve a Wikipedia link for the provided keyword."""

        params = {
            "action": "query",
            "list": "search",
            "format": "json",
            "srlimit": limit,
            "srsearch": keyword,
        }
        try:
            response = requests.get(
                self.search_url,
                headers=self.headers,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            log.error(
                "Error while fetching wikipedia search for keyword: %s (%s)",
                keyword,
                exc,
            )
            return None

        data = response.json()
        query = data.get("query", {})
        results = query.get("search", [])
        if not results:
            log.error("No search results found for keyword: %s", keyword)
            return None

        if interactive:
            click.echo(f"Search results for keyword '{keyword}':")
            for index, result in enumerate(results):
                click.echo(f"   {index}: {result['title']}")

            choice = click.prompt("Choose a result", type=int)
            if choice < 0 or choice >= len(results):
                log.error("Invalid choice")
                return None
            result = results[choice]
        else:
            result = results[0]

        page_title = result["title"]
        page_url = self.build_page_url(page_title.replace(" ", "_"))
        return {
            "title": page_title,
            "url": page_url,
            "timestamp": result.get("timestamp", ""),
        }

    def fetch_summary(
        self,
        page_title: str,
        language: str | None = None,
    ) -> dict[str, Any] | None:
        """Fetch the page summary for the provided Wikipedia title."""

        api_url = self.get_api_url(language)
        summary_url = f"{api_url}/page/summary/{page_title}"

        try:
            response = requests.get(
                summary_url,
                timeout=self.timeout,
                headers=self.headers,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            log.error(
                "Error while fetching wikipedia summary for page: %s (%s)",
                page_title,
                exc,
            )
            return None

        data = response.json()
        extract = data.get("extract", "")
        keep_keys = {"title", "thumbnail", "timestamp", "description", "extract", "tid"}
        filtered = {key: value for key, value in data.items() if key in keep_keys}
        if extract:
            filtered["extract"] = extract.strip()
        return filtered

    def load(self) -> None:
        """Load the cached metadata from disk if available."""

        default: dict[str, Any] = {"wikipedia": {}, "version": "0.2"}
        yaml = YAML()
        yaml.preserve_quotes = True

        if not self.filename.exists():
            self.data = default
            return

        with self.filename.open(encoding="utf-8") as handle:
            links = yaml.load(handle)

        try:
            validated = WikipediaCacheModel.model_validate(links)
        except (ValidationError, TypeError) as exc:
            log.error("Invalid links file, regenerate it...", exc_info=exc)
            self.data = default
            return

        self.data = validated.model_dump(exclude_none=True)

        if self.data.get("version") != "0.2":
            log.error("Invalid version in links file, regenerate it...")
            self.data = default

    def save(self) -> None:
        """Persist the cached metadata to disk."""

        yaml = YAML()
        with self.filename.open("w", encoding="utf-8") as handle:
            yaml.dump(self.data, handle)

    def __contains__(self, keyword: str) -> bool:
        return keyword in self.data.get("wikipedia", {})

    def __iter__(self) -> Iterator[tuple[str, Any]]:
        return iter(self.data.get("wikipedia", {}).items())

    def __getitem__(self, keyword: str) -> Any:
        return self.data["wikipedia"][keyword]

    def __setitem__(self, keyword: str, value: Any) -> None:
        self.data.setdefault("wikipedia", {})[keyword] = value
