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

def clean_text(text: str | None, max_len: int = 140) -> str:
    t = html.unescape(text or "")
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"`[^`]+`", " ", t)
    t = re.sub(r"\[[^\]]+\]", " ", t)
    t = re.sub(r"https?://\S+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    if len(t) > max_len:
        t = t[:max_len].rstrip(" ,.;:-") + "..."
    return t

def detect_pk_column(conn: sqlite3.Connection) -> str | None:
    rows = conn.execute("PRAGMA table_info(items)").fetchall()
    for row in rows:
        if row[5]:
            return row[1]
    names = [row[1] for row in rows]
    if "id" in names:
        return "id"
    return None

def normalize_summary(source_name: str, title: str, summary: str) -> str:
    title_clean = clean_text(title, 100)
    summary_clean = clean_text(summary, 140)

    lower = (summary or "").lower()

    if source_name == "OBS Studio Releases":
        return f"{title_clean} の更新です。変更点の詳細は公式リリースノートで確認できます。"

    if source_name == "TeamYouTube":
        if len(summary_clean) < 20:
            return f"{title_clean} に関する更新です。配信動画運用への影響を確認してください。"
        if "tutorial" in lower or "watch" in lower or "learn" in lower:
            return f"{title_clean} に関する案内です。配信設定や運用改善の参考になります。"
        return summary_clean

    if source_name == "Twitch Blog":
        if len(summary_clean) < 20:
            return f"{title_clean} に関する更新です。配信導線やクリップ運用への影響を確認してください。"
        return summary_clean

    return summary_clean or f"{title_clean} の要点を確認できるよう準備中です。"

def main() -> None:
    if not DB_PATH.exists():
        print("DB not found, skip normalize")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    pk_col = detect_pk_column(conn)

    if pk_col:
        rows = conn.execute(
            f"SELECT {pk_col} AS _pk, source_name, url, title, summary FROM items"
        ).fetchall()
        update_sql = f"UPDATE items SET url = ?, summary = ? WHERE {pk_col} = ?"
    else:
        rows = conn.execute(
            "SELECT rowid AS _pk, source_name, url, title, summary FROM items"
        ).fetchall()
        update_sql = "UPDATE items SET url = ?, summary = ? WHERE rowid = ?"

    count = 0
    for row in rows:
        pk = row["_pk"]
        source_name = row["source_name"] if "source_name" in row.keys() else ""
        url = row["url"] if "url" in row.keys() else ""
        title = row["title"] if "title" in row.keys() else ""
        summary = row["summary"] if "summary" in row.keys() else ""

        new_url = url
        if isinstance(url, str) and "example.com" in url:
            new_url = SOURCE_URLS.get(source_name, url)

        new_summary = normalize_summary(source_name, title, summary)

        conn.execute(update_sql, (new_url, new_summary, pk))
        count += 1

    conn.commit()
    conn.close()
    print(f"normalized {count} items")

if __name__ == "__main__":
    main()