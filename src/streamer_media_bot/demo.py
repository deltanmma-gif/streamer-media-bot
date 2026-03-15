from __future__ import annotations

from datetime import datetime, timedelta, timezone

from .models import SourceItem


def demo_items() -> list[SourceItem]:
    now = datetime.now(timezone.utc)
    raw = [
        (
            "youtube_teamyoutube",
            "TeamYouTube",
            "youtube",
            "YouTube ライブ配信の管理画面更新まとめ",
            "https://example.com/youtube-live-update",
            "配信前チェックに影響する導線変更を整理",
        ),
        (
            "obs_releases",
            "OBS Studio Releases",
            "obs",
            "OBS Studio 31.1 リリース候補で追加された改善点",
            "https://example.com/obs-release",
            "音声メーターと安定性まわりの更新を確認",
        ),
        (
            "twitch_blog",
            "Twitch Blog",
            "twitch",
            "Twitch のクリップ導線改善を見直すための更新",
            "https://example.com/twitch-clips-update",
            "切り抜き導線と通知文に関係する変更を整理",
        ),
    ]
    items: list[SourceItem] = []
    for idx, row in enumerate(raw):
        source_id, source_name, category, title, url, summary = row
        published = (now - timedelta(days=idx)).isoformat()
        fingerprint = f"demo-{idx}-{source_id}"
        items.append(
            SourceItem(
                source_id=source_id,
                source_name=source_name,
                category=category,
                title=title,
                url=url,
                published_at=published,
                summary=summary,
                fingerprint=fingerprint,
            )
        )
    return items
