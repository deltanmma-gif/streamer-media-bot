from __future__ import annotations

import argparse
from pathlib import Path

from .collector import collect_sources
from .config import load_config, project_root
from .db import Database
from .demo import demo_items
from .site import build_site


def db_from_config(config: dict) -> Database:
    root = project_root()
    db_path = root / config["database"]["path"]
    return Database(db_path)


def command_run(config: dict) -> int:
    db = db_from_config(config)
    run_id = db.create_run("collect")
    items = collect_sources(config)
    inserted = db.insert_items(items)
    db.finish_run(run_id, inserted)
    print(f"Collected {len(items)} items / inserted {inserted} items")
    return 0


def command_build(config: dict) -> int:
    db = db_from_config(config)
    recent_days = int(config["collection"].get("recent_days", 14))
    rows = db.recent_items(days=recent_days, limit=50)
    items = [dict(row) for row in rows]
    posts = build_site(config, items)
    print(f"Built site with {len(items)} news items and {len(posts)} post candidates")
    return 0


def command_seed_demo(config: dict) -> int:
    db = db_from_config(config)
    inserted = db.insert_items(demo_items())
    print(f"Seeded {inserted} demo items")
    return 0


def command_all(config: dict) -> int:
    command_run(config)
    return command_build(config)


def main() -> int:
    parser = argparse.ArgumentParser(description="Streamer media bot")
    parser.add_argument("command", choices=["run", "build", "all", "seed-demo"])
    args = parser.parse_args()
    config = load_config()
    if args.command == "run":
        return command_run(config)
    if args.command == "build":
        return command_build(config)
    if args.command == "all":
        return command_all(config)
    if args.command == "seed-demo":
        return command_seed_demo(config)
    return 1
