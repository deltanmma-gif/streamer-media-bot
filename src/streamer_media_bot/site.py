from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .builders import (
    create_card_png,
    ensure_dir,
    generate_posts,
    read_json_files,
    render_card_page,
    render_home,
    render_news_page,
    render_posts_page,
    render_table_page,
    render_tools_page,
)


def build_site(config: dict, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    root = Path(__file__).resolve().parents[2]
    output_dir = root / config["site"]["output_dir"]
    cards_dir = root / "content" / "cards"
    tables_dir = root / "content" / "tables"
    tool_dir = root / "content" / "tool_data"

    ensure_dir(output_dir)
    ensure_dir(output_dir / "assets" / "cards")
    ensure_dir(output_dir / "cards")
    ensure_dir(output_dir / "tables")
    ensure_dir(output_dir / "news")
    ensure_dir(output_dir / "tools")
    ensure_dir(output_dir / "posts")
    ensure_dir(output_dir / "data")

    cards = read_json_files(cards_dir)
    tables = read_json_files(tables_dir)
    tool_data_path = next(tool_dir.glob("*.json"), None)
    tool_data: dict[str, Any] = {}
    if tool_data_path:
        with tool_data_path.open("r", encoding="utf-8") as f:
            tool_data = json.load(f)

    for card in cards:
        create_card_png(card, output_dir / "assets" / "cards" / f"{card['slug']}.png")
        (output_dir / "cards" / f"{card['slug']}.html").write_text(render_card_page(config["site"], card), encoding="utf-8")

    for table in tables:
        (output_dir / "tables" / f"{table['slug']}.html").write_text(render_table_page(config["site"], table), encoding="utf-8")

    posts = generate_posts(items, cards)
    (output_dir / "index.html").write_text(render_home(config["site"], cards, tables, items, posts), encoding="utf-8")
    (output_dir / "news" / "index.html").write_text(render_news_page(config["site"], items), encoding="utf-8")
    (output_dir / "tools" / "index.html").write_text(render_tools_page(config["site"], tool_data), encoding="utf-8")
    (output_dir / "posts" / "index.html").write_text(render_posts_page(config["site"], posts), encoding="utf-8")
    (output_dir / "posts" / "today.md").write_text(_render_posts_markdown(posts), encoding="utf-8")
    (output_dir / "data" / "news.json").write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "data" / "posts.json").write_text(json.dumps(posts, ensure_ascii=False, indent=2), encoding="utf-8")

    return posts


def _render_posts_markdown(posts: list[dict[str, Any]]) -> str:
    lines = ["# 今日の投稿候補", ""]
    for idx, post in enumerate(posts, start=1):
        lines.extend(
            [
                f"## {idx}. {post['headline']}",
                "",
                post["body"],
                "",
                f"- ALT: {post['alt_text']}",
                f"- 画像: {post['image_path']}",
                "",
            ]
        )
    return "\n".join(lines)
