"""Fetch and cache Wikipedia metadata referenced in MkDocs pages."""

from __future__ import annotations

import json
import re
import shutil
import urllib.parse
from html import unescape
from pathlib import Path

from jinja2 import Environment
from mkdocs.config import Config, config_options
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page
from mkdocs.utils import log
from unidecode import unidecode

from .wikipedia import Wikipedia

DEFAULT_DOMAIN = "wikipedia.org"


def to_ascii(key: str) -> str:
    """Create a slug suitable for file-system usage."""

    decoded = urllib.parse.unquote(unescape(key)).replace("_", "-").lower()
    ascii_key = unidecode(decoded)
    return re.sub(r"[^\w-]", "", ascii_key)


def to_human_url(key: str) -> str:
    """Decode percent-encoded segments for display."""

    return urllib.parse.unquote(unescape(key))


class WikipediaPluginConfig(Config):
    """Declarative configuration for the Wikipedia plugin."""

    filename = config_options.Type(str, default="links.yml")
    domain = config_options.Type(str, default=DEFAULT_DOMAIN)
    language = config_options.Optional(config_options.Type(str))
    timeout = config_options.Type(int, default=5)
    language_subdomains = config_options.Type(bool, default=True)


class WikipediaPlugin(BasePlugin[WikipediaPluginConfig]):
    """MkDocs plugin to fetch and cache Wikipedia metadata."""

    def __init__(self) -> None:
        super().__init__()
        self.wiki = Wikipedia()
        self._package_root = Path(__file__).parent
        self._asset_targets: list[tuple[Path, Path]] = []
        self._language_warning_emitted = False
        self._resolved_language = "en"
        self._resolved_domain = DEFAULT_DOMAIN
        self._link_pattern = self._compile_link_pattern(self._resolved_domain)
        self._frontend_config_target: Path | None = None
        self._frontend_payload: dict[str, object] = {}
        self._frontend_default_domain = DEFAULT_DOMAIN
        self._use_language_subdomains = True

    def on_config(self, config: MkDocsConfig) -> MkDocsConfig:
        """Load cached Wikipedia data before the build starts."""

        self.wiki.filename = Path(self.config.filename)
        domain = self._sanitize_domain(self.config.domain)
        self._use_language_subdomains = self.config.language_subdomains
        self._resolved_domain = domain
        self._link_pattern = self._compile_link_pattern(domain)
        resolved_language = self.config.language or self._detect_language(config)
        if not resolved_language:
            resolved_language = "en"
            if not self._language_warning_emitted:
                log.warning(
                    "mkdocs-wikipedia: unable to determine site language; defaulting to 'en'. "
                    "Set the plugin 'language' option to silence this warning."
                )
                self._language_warning_emitted = True

        self._resolved_language = resolved_language
        self.wiki.configure(
            language=resolved_language if self._use_language_subdomains else "",
            domain=domain,
            timeout=self.config.timeout,
        )
        self.wiki.load()

        assets_prefix = Path("assets") / "wikipedia"
        js_entry = assets_prefix / "wiki-tips.js"
        css_entry = assets_prefix / "wiki.css"
        config_slug = to_ascii(domain) or "default"
        config_entry = assets_prefix / f"config-{config_slug}.js"
        js_href = js_entry.as_posix()
        css_href = css_entry.as_posix()
        config_href = config_entry.as_posix()

        extra_js = list(config.extra_javascript or [])
        if config_href not in extra_js:
            if js_href in extra_js:
                index = extra_js.index(js_href)
                extra_js.insert(index, config_href)
            else:
                extra_js.append(config_href)
        if js_href not in extra_js:
            extra_js.append(js_href)
        config.extra_javascript = extra_js

        extra_css = list(config.extra_css or [])
        if css_href not in extra_css:
            extra_css.append(css_href)
        config.extra_css = extra_css

        site_dir = Path(config.site_dir)
        self._asset_targets = [
            (self._package_root / "js" / "wiki-tips.js", site_dir / js_entry),
            (self._package_root / "css" / "wiki.css", site_dir / css_entry),
        ]
        self._frontend_config_target = site_dir / config_entry
        self._frontend_default_domain = domain
        self._frontend_payload = {
            domain: {
                "language": self._resolved_language,
                "summaryPath": "/api/rest_v1/page/summary/",
                "languageSubdomains": self._use_language_subdomains,
            }
        }
        return config

    def on_page_content(
        self,
        html: str,
        /,
        *,
        page: Page,
        config: MkDocsConfig,
        files: Files,
    ) -> str:
        """Collect Wikipedia links and ensure their metadata is cached."""

        del page, config, files

        for match in self._link_pattern.finditer(html):
            url = match.group("url")
            page_title = match.group("title")
            language = match.group("lang")
            if self._use_language_subdomains and not language:
                language = self._resolved_language or "en"
            identifier = language if (language and self._use_language_subdomains) else self._resolved_domain
            key_source = f"{identifier}-{page_title}" if identifier else page_title
            key = to_ascii(key_source)
            if url in self.wiki:
                continue

            log.info("Fetching wikipedia summary for '%s'", to_human_url(page_title))
            summary = self.wiki.fetch_summary(
                page_title.replace("/", r"%2F"),
                language if self._use_language_subdomains else None,
            )
            if summary:
                summary["key"] = key
                summary["plainlink"] = to_human_url(url)
                self.wiki[url] = summary

        return html

    @staticmethod
    def _compile_link_pattern(domain: str) -> re.Pattern[str]:
        """Create a regex that captures wiki links for the provided domain."""

        escaped_domain = re.escape(domain)
        return re.compile(
            rf'<a[^>]+?href="(?P<url>https?://(?:(?P<lang>[a-z0-9-]+)\.)?{escaped_domain}/wiki/(?P<title>[^"#]+))"'
        )

    @staticmethod
    def _sanitize_domain(domain: str) -> str:
        """Normalize a user-provided domain for consistent processing."""

        sanitized = domain.strip()
        sanitized = re.sub(r"^https?://", "", sanitized, flags=re.IGNORECASE)
        sanitized = sanitized.strip("/").lower()
        return sanitized or DEFAULT_DOMAIN

    def _detect_language(self, config: MkDocsConfig) -> str | None:
        """Infer the site language from MkDocs configuration."""

        theme = getattr(config, "theme", None)
        if theme is not None:
            theme_language = getattr(theme, "language", None)
            if isinstance(theme_language, str) and theme_language:
                return theme_language

            theme_locale = getattr(theme, "locale", None)
            locale_language = getattr(theme_locale, "language", None)
            if isinstance(locale_language, str) and locale_language:
                return locale_language

        site_language = getattr(config, "site_language", None)
        if isinstance(site_language, str) and site_language:
            return site_language

        extra = getattr(config, "extra", None)
        if isinstance(extra, dict):
            for key in ("language", "lang", "site_language", "default_language"):
                value = extra.get(key)
                if isinstance(value, str) and value:
                    return value

            extra_i18n = extra.get("i18n")
            if isinstance(extra_i18n, dict):
                for key in ("default_language", "language", "default"):
                    value = extra_i18n.get(key)
                    if isinstance(value, str) and value:
                        return value

            extra_locale = extra.get("locale")
            if isinstance(extra_locale, dict):
                value = extra_locale.get("language")
                if isinstance(value, str) and value:
                    return value

        return None

    def on_env(
        self,
        env: Environment,
        /,
        *,
        config: MkDocsConfig,
        files: Files,
    ) -> None:
        """Persist cached data at the end of the build."""

        del env, config, files
        self.wiki.save()

    def on_post_build(self, *, config: MkDocsConfig) -> None:
        """Copy bundled static assets into the built site."""

        del config
        if not self._asset_targets:
            return

        for source, target in self._asset_targets:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)

        if self._frontend_config_target is not None:
            self._frontend_config_target.parent.mkdir(parents=True, exist_ok=True)
            payload = json.dumps(self._frontend_payload, ensure_ascii=False)
            default_domain = json.dumps(self._frontend_default_domain, ensure_ascii=False)
            content = (
                "window.mkdocsWikipediaConfig = window.mkdocsWikipediaConfig || {};\n"
                "window.mkdocsWikipediaConfig.domains = Object.assign(\n"
                "  window.mkdocsWikipediaConfig.domains || {},\n"
                f"  {payload}\n"
                ");\n"
                "if (!window.mkdocsWikipediaConfig.defaultDomain) {\n"
                f"  window.mkdocsWikipediaConfig.defaultDomain = {default_domain};\n"
                "}\n"
            )
            self._frontend_config_target.write_text(content, encoding="utf-8")
