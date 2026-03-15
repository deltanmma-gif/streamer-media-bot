from __future__ import annotations

import hashlib
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse, urlunparse

import feedparser
import httpx
from bs4 import BeautifulSoup

from .models import SourceItem


def canonicalize_url(url: str) -> str:
    parsed = urlparse(url)
    clean = parsed._replace(query="", fragment="")
    return urlunparse(clean)


def normalize_date(value: str | None) -> str:
    if not value:
        return datetime.now(timezone.utc).isoformat()
    try:
        if value.endswith("Z"):
            return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc).isoformat()
        return datetime.fromisoformat(value).astimezone(timezone.utc).isoformat()
    except Exception:
        pass
    try:
        return parsedate_to_datetime(value).astimezone(timezone.utc).isoformat()
    except Exception:
        return datetime.now(timezone.utc).isoformat()


def html_to_text(value: str) -> str:
    if not value:
        return ""
    soup = BeautifulSoup(value, "html.parser")
    return re.sub(r"\s+", " ", soup.get_text(" ", strip=True)).strip()


def make_fingerprint(source_id: str, url: str, title: str) -> str:
    base = f"{source_id}|{canonicalize_url(url)}|{title.strip()}".encode("utf-8")
    return hashlib.sha1(base).hexdigest()


def fetch_text(url: str, timeout: int, user_agent: str) -> str:
    headers = {"User-Agent": user_agent, "Accept": "text/html,application/xml,application/rss+xml,application/atom+xml,*/*"}
    with httpx.Client(timeout=timeout, follow_redirects=True, headers=headers) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.text


def collect_from_feed(source: dict, timeout: int, user_agent: str, max_items: int) -> list[SourceItem]:
    text = fetch_text(source["url"], timeout, user_agent)
    feed = feedparser.parse(text)
    items: list[SourceItem] = []
    for entry in feed.entries[:max_items]:
        link = entry.get("link") or source["url"]
        title = entry.get("title", "無題")
        summary = html_to_text(entry.get("summary") or entry.get("description") or "")
        published = normalize_date(entry.get("published") or entry.get("updated") or entry.get("pubDate"))
        items.append(
            SourceItem(
                source_id=source["id"],
                source_name=source["name"],
                category=source.get("category", "general"),
                title=title,
                url=canonicalize_url(link),
                published_at=published,
                summary=summary,
                fingerprint=make_fingerprint(source["id"], link, title),
            )
        )
    return items


def _iter_sitemap_entries(xml_text: str) -> Iterable[tuple[str, str | None]]:
    root = ET.fromstring(xml_text)
    namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    if root.tag.endswith("sitemapindex"):
        for sitemap in root.findall(f"{namespace}sitemap"):
            loc = sitemap.findtext(f"{namespace}loc")
            if loc:
                yield (loc, None)
    else:
        for url in root.findall(f"{namespace}url"):
            loc = url.findtext(f"{namespace}loc")
            lastmod = url.findtext(f"{namespace}lastmod")
            if loc:
                yield (loc, lastmod)


def _slug_title(url: str) -> str:
    path = urlparse(url).path.rstrip("/")
    slug = path.split("/")[-1] or path.split("/")[-2]
    title = slug.replace("-", " ").replace("_", " ").strip()
    return title.title() if title else url


def collect_from_sitemap(source: dict, timeout: int, user_agent: str, max_items: int) -> list[SourceItem]:
    include_patterns = [p.lower() for p in source.get("include_patterns", [])]
    pending = [source["url"]]
    visited: set[str] = set()
    items: list[SourceItem] = []

    while pending and len(items) < max_items:
        current = pending.pop(0)
        if current in visited:
            continue
        visited.add(current)
        xml_text = fetch_text(current, timeout, user_agent)
        for loc, lastmod in _iter_sitemap_entries(xml_text):
            if loc.endswith(".xml"):
                pending.append(loc)
                continue
            target = loc.lower()
            if include_patterns and not any(pattern in target for pattern in include_patterns):
                continue
            title = _slug_title(loc)
            items.append(
                SourceItem(
                    source_id=source["id"],
                    source_name=source["name"],
                    category=source.get("category", "general"),
                    title=title,
                    url=canonicalize_url(loc),
                    published_at=normalize_date(lastmod),
                    summary=f"{source['name']} の更新ページ候補",
                    fingerprint=make_fingerprint(source["id"], loc, title),
                )
            )
            if len(items) >= max_items:
                break
    return items


def collect_sources(config: dict) -> list[SourceItem]:
    collection = config["collection"]
    timeout = int(collection.get("timeout_seconds", 20))
    user_agent = collection.get("user_agent", "streamer-media-bot/0.1")
    max_items = int(collection.get("max_items_per_source", 25))
    items: list[SourceItem] = []

    for source in config.get("sources", []):
        try:
            kind = source["kind"]
            if kind == "feed":
                items.extend(collect_from_feed(source, timeout, user_agent, max_items))
            elif kind == "sitemap":
                items.extend(collect_from_sitemap(source, timeout, user_agent, max_items))
            else:
                print(f"[WARN] unsupported source kind: {kind}")
        except Exception as exc:
            print(f"[WARN] failed to collect {source['id']}: {exc}")
    return items
