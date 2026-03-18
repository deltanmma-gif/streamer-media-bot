from __future__ import annotations

import html
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "streamer_media.db"

SOURCE_URLS = {
    "TeamYouTube": "https://www.youtube.com/@TeamYouTube",
    "OBS Studio Releases": "https://github.com/obsproject/obs-studio/releases",
    "Twitch Blog": "https://blog.twitch.tv/",
}

def clean_text(text: str | None, max_len: int = 160) -> str:
    t = html.unescape(text or "")
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"\[[^\]]+\]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    if len(t) > max_len:
        t = t[:max_len].rstrip(" ,.;:-") + "..."
    return t

def main() -> None:
    if not DB_PATH.exists():
        print("DB not found, skip normalize")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute("SELECT rowid, * FROM items").fetchall()

    for row in rows:
        rowid = row["rowid"]
        source_name = row["source_name"] if "source_name" in row.keys() else ""
        url = row["url"] if "url" in row.keys() else ""
        title = row["title"] if "title" in row.keys() else ""
        summary = row["summary"] if "summary" in row.keys() else ""

        new_url = url
        if isinstance(url, str) and "example.com" in url:
            new_url = SOURCE_URLS.get(source_name, url)

        new_summary = clean_text(summary, 160)
        if not new_summary:
            new_summary = clean_text(title, 120) or "要点を確認できるよう準備中です。"

        conn.execute(
            "UPDATE items SET url = ?, summary = ? WHERE rowid = ?",
            (new_url, new_summary, rowid),
        )

    conn.commit()
    conn.close()
    print(f"normalized {len(rows)} items")

if __name__ == "__main__":
    main()