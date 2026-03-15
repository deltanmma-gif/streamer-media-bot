from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class SourceItem:
    source_id: str
    source_name: str
    category: str
    title: str
    url: str
    published_at: str
    summary: str
    fingerprint: str
