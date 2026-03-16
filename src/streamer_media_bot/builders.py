from __future__ import annotations

import json
import math
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


def read_json_files(directory: Path) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    if not directory.exists():
        return items
    for path in sorted(directory.glob("*.json")):
        with path.open("r", encoding="utf-8") as f:
            items.append(json.load(f))
    return items


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _font(size: int):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size=size)
    except Exception:
        return ImageFont.load_default()


def create_card_png(card: dict[str, Any], output_path: Path) -> None:
    ensure_dir(output_path.parent)
    width, height = 1600, 900
    image = Image.new("RGB", (width, height), color=(22, 27, 34))
    draw = ImageDraw.Draw(image)

    title_font = _font(60)
    subtitle_font = _font(32)
    bullet_font = _font(34)

    draw.rounded_rectangle((60, 60, width - 60, height - 60), radius=36, outline=(100, 180, 255), width=4, fill=(27, 35, 47))
    draw.text((110, 110), card["title"], font=title_font, fill=(255, 255, 255))
    draw.text((110, 200), card.get("subtitle", ""), font=subtitle_font, fill=(177, 210, 255))

    y = 290
    for idx, bullet in enumerate(card.get("bullets", []), start=1):
        wrapped = textwrap.wrap(f"{idx}. {bullet}", width=28)
        for line in wrapped:
            draw.text((130, y), line, font=bullet_font, fill=(238, 243, 248))
            y += 52
        y += 10

    draw.text((110, height - 110), "驟堺ｿ｡閠・髄縺醍┌譁吝ｮ溽畑蜩√Γ繝・ぅ繧｢", font=_font(26), fill=(170, 190, 210))
    image.save(output_path)


def html_page(title: str, body: str, site_title: str, base_url: str = "") -> str:
    return f"""<!doctype html>
<html lang=\"ja\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>{title}</title>
  <style>
    :root {{ --bg:#0f1318; --panel:#181f27; --line:#2b3440; --text:#f1f5f9; --muted:#9fb0c3; --accent:#68b4ff; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background:var(--bg); color:var(--text); }}
    a {{ color:var(--accent); text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
    .wrap {{ max-width: 1120px; margin: 0 auto; padding: 24px; }}
    .hero {{ padding: 28px 0 8px; }}
    .muted {{ color: var(--muted); }}
    .grid {{ display:grid; gap:16px; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); }}
    .card {{ background:var(--panel); border:1px solid var(--line); border-radius:20px; padding:18px; }}
    .table-wrap {{ overflow:auto; }}
    table {{ width:100%; border-collapse:collapse; }}
    th, td {{ padding:10px 12px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }}
    th {{ color:var(--muted); font-weight:600; }}
    .pill {{ display:inline-block; padding:4px 10px; border-radius:999px; font-size:12px; background:#112132; color:#a8d2ff; }}
    code, pre {{ background:#0b1015; border:1px solid var(--line); border-radius:12px; }}
    pre {{ padding:14px; overflow:auto; }}
    .topnav {{ display:flex; gap:12px; flex-wrap:wrap; margin:10px 0 0; }}
    .topnav a {{ background:#111923; border:1px solid var(--line); border-radius:999px; padding:8px 12px; }}
    .footer {{ margin:48px 0 16px; color:var(--muted); font-size:14px; }}
    button,input,select {{ font:inherit; }}
    .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
  </style>
</head>
<body>
  <div class=\"wrap\">
    <header class=\"hero\">
      <div class=\"pill\">{site_title}</div>
      <div class=\"topnav\">
        <a href=\"{base_url}/index.html\">繝帙・繝</a>
        <a href=\"{base_url}/news/index.html\">譖ｴ譁ｰ荳隕ｧ</a>
        <a href=\"{base_url}/tools/index.html\">繝・・繝ｫ</a>
        <a href=\"{base_url}/posts/index.html\">謚慕ｨｿ蛟呵｣・/a>
      </div>
    </header>
    {body}
    <div class=\"footer\">Generated at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</div>
  </div>
</body>
</html>
"""


def render_home(site: dict[str, Any], cards: list[dict[str, Any]], tables: list[dict[str, Any]], items: list[dict[str, Any]], posts: list[dict[str, Any]]) -> str:
    card_html = "".join(
        f"<article class='card'><h3>{card['title']}</h3><p class='muted'>{card.get('subtitle','')}</p><img src='assets/cards/{card['slug']}.png' alt='{card['title']}' style='width:100%;border-radius:16px;border:1px solid var(--line);'><p><a href='cards/{card['slug']}.html'>隧ｳ邏ｰ繧定ｦ九ｋ</a></p></article>"
        for card in cards
    )
    table_html = "".join(
        f"<article class='card'><h3>{table['title']}</h3><p class='muted'>{table.get('description','')}</p><p><a href='tables/{table['slug']}.html'>豈碑ｼ・｡ｨ繧定ｦ九ｋ</a></p></article>"
        for table in tables
    )
    item_html = "".join(
        f"<article class='card'><div class='pill'>{item['source_name']}</div><h3><a href='{item['url']}'>{item['title']}</a></h3><p class='muted'>{item['published_at'][:10]} / {item['category']}</p><p>{item['summary']}</p></article>"
        for item in items[:6]
    )
    post_html = "".join(
        f"<article class='card'><h3>{post['headline']}</h3><p>{post['body']}</p><p class='muted'>ALT: {post['alt_text']}</p></article>"
        for post in posts[:4]
    )
    body = f"""
    <section>
      <h1>{site['title']}</h1>
      <p class='muted'>{site['tagline']}</p>
    </section>
    <section>
      <h2>譛譁ｰ譖ｴ譁ｰ</h2>
      <div class='grid'>{item_html or '<p class="muted">縺ｾ縺譖ｴ譁ｰ縺後≠繧翫∪縺帙ｓ縲・/p>'}</div>
    </section>
    <section>
      <h2>菫晏ｭ倡沿繧ｫ繝ｼ繝・/h2>
      <div class='grid'>{card_html}</div>
    </section>
    <section>
      <h2>豈碑ｼ・｡ｨ繝ｻ譌ｩ隕玖｡ｨ</h2>
      <div class='grid'>{table_html}</div>
    </section>
    <section>
      <h2>莉頑律縺ｮ謚慕ｨｿ蛟呵｣・/h2>
      <div class='grid'>{post_html}</div>
    </section>
    """
    return html_page(site['title'], body, site['title'], site.get('base_url', ''))


def render_card_page(site: dict[str, Any], card: dict[str, Any]) -> str:
    bullets = "".join(f"<li>{bullet}</li>" for bullet in card.get("bullets", []))
    body = f"""
    <article class='card'>
      <h1>{card['title']}</h1>
      <p class='muted'>{card.get('subtitle', '')}</p>
      <img src='../assets/cards/{card['slug']}.png' alt='{card['title']}' style='width:100%;max-width:900px;border-radius:18px;border:1px solid var(--line);'>
      <ul>{bullets}</ul>
    </article>
    """
    return html_page(card['title'], body, site['title'], '..')


def render_table_page(site: dict[str, Any], table: dict[str, Any]) -> str:
    headers = "".join(f"<th>{col}</th>" for col in table.get("columns", []))
    rows = "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in table.get("rows", []))
    body = f"""
    <article class='card'>
      <h1>{table['title']}</h1>
      <p class='muted'>{table.get('description','')}</p>
      <div class='table-wrap'>
        <table>
          <thead><tr>{headers}</tr></thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
    </article>
    """
    return html_page(table['title'], body, site['title'], '..')


def render_news_page(site: dict[str, Any], items: list[dict[str, Any]]) -> str:
    html = "".join(
        f"<article class='card'><div class='pill'>{item['source_name']}</div><h3><a href='{item['url']}'>{item['title']}</a></h3><p class='muted'>{item['published_at']}</p><p>{item['summary']}</p></article>"
        for item in items
    )
    body = f"<section><h1>譖ｴ譁ｰ荳隕ｧ</h1><div class='grid'>{html or '<p class="muted">譖ｴ譁ｰ縺後≠繧翫∪縺帙ｓ縲・/p>'}</div></section>"
    return html_page('譖ｴ譁ｰ荳隕ｧ', body, site['title'], '..')


def render_posts_page(site: dict[str, Any], posts: list[dict[str, Any]]) -> str:
    entries = []
    for post in posts:
        entries.append(
            f"<article class='card'><h2>{post['headline']}</h2><p>{post['body']}</p><p class='muted'>ALT: {post['alt_text']}</p><p class='muted'>逕ｻ蜒・ {post['image_path']}</p></article>"
        )
    body = f"<section><h1>謚慕ｨｿ蛟呵｣・/h1><div class='grid'>{''.join(entries)}</div></section>"
    return html_page('謚慕ｨｿ蛟呵｣・, body, site['title'], '..')


def render_tools_page(site: dict[str, Any], tool_data: dict[str, Any]) -> str:
    js_data = json.dumps(tool_data, ensure_ascii=False)
    body = f"""
    <section>
      <h1>繝悶Λ繧ｦ繧ｶ蜀・ヤ繝ｼ繝ｫ</h1>
      <div class='grid'>
        <article class='card'>
          <h2>驟堺ｿ｡繧ｿ繧､繝医Ν逕滓・</h2>
          <p class='muted'>騾壻ｿ｡縺ｪ縺・/ GitHub Pages 荳翫〒蜍穂ｽ・/p>
          <p><button id='generateBtn'>繧ｿ繧､繝医Ν繧剃ｽ懊ｋ</button></p>
          <pre class='mono' id='titleOut'>縺薙％縺ｫ蛟呵｣懊′蜃ｺ縺ｾ縺・/pre>
        </article>
        <article class='card'>
          <h2>蜻顔衍譁・・蝙・/h2>
          <pre class='mono'>縲蝉ｻ頑律縺ｮ驟堺ｿ｡縲曾n菴輔ｒ縺吶ｋ縺欺n隱ｰ蜷代￠縺欺n髢句ｧ区凾蛻ｻ\n譛蠕後↓荳險</pre>
        </article>
      </div>
    </section>
    <script>
      const DATA = {js_data};
      function pick(arr) {{ return arr[Math.floor(Math.random() * arr.length)]; }}
      document.getElementById('generateBtn').addEventListener('click', () => {{
        const title = `${{pick(DATA.games)}} / ${{pick(DATA.hooks)}} / ${{pick(DATA.goals)}} / ${{pick(DATA.endings)}}`;
        document.getElementById('titleOut').textContent = title;
      }});
    </script>
    """
    return html_page('繝・・繝ｫ', body, site['title'], '..')


def generate_posts(items: list[dict[str, Any]], cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    posts: list[dict[str, Any]] = []
    for item in items[:3]:
        posts.append(
            {
                "headline": f"譖ｴ譁ｰ謨ｴ逅・ {item['title']}",
                "body": f"{item['source_name']} 縺ｮ譖ｴ譁ｰ繧・蛻・〒謚頑升縺ｧ縺阪ｋ繧医≧縺ｫ謨ｴ逅・＠縺ｾ縺励◆縲りｦ∫せ縺縺大・縺ｫ遒ｺ隱阪＠縺溘＞莠ｺ蜷代￠縲・{item['url']}",
                "alt_text": f"{item['source_name']} 縺ｮ譖ｴ譁ｰ隕∫せ繧呈紛逅・＠縺溘き繝ｼ繝臥判蜒上ゅち繧､繝医Ν縺ｯ {item['title']}縲・,
                "image_path": f"assets/cards/{cards[0]['slug']}.png" if cards else "",
            }
        )
    for card in cards[:2]:
        posts.append(
            {
                "headline": f"菫晏ｭ倡沿: {card['title']}",
                "body": f"驟堺ｿ｡蜑榊ｾ後〒菴ｿ縺・屓縺帙ｋ繧医≧縺ｫ縲＋card['title']} 繧・譫壹↓縺ｾ縺ｨ繧√∪縺励◆縲・,
                "alt_text": f"菫晏ｭ倡沿繧ｫ繝ｼ繝峨ゅち繧､繝医Ν縺ｯ {card['title']}縲らｮ・擅譖ｸ縺阪〒謇矩・ｒ5縺､謗ｲ霈峨・,
                "image_path": f"assets/cards/{card['slug']}.png",
            }
        )
    return posts[:6]
