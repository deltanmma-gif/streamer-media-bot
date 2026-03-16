from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REPLACEMENTS = {
    "docs/index.html": {
        "<h2>最新更新</h2>": "<h2>直近の重要更新</h2>",
        "<h2>保存版カード</h2>": "<h2>同接を増やすテンプレ</h2>",
        "<h2>比較表早見表</h2>": "<h2>収益化改善比較表</h2>",
        "<h2>比較表早見表</h2>": "<h2>収益化改善比較表</h2>",
        "<h2>今日の投稿候補</h2>": "<h2>今日のX投稿候補</h2>",
        ">更新一覧<": ">最新情報<",
        ">ツール<": ">同接収益化ツール<",
        ">投稿候補<": ">X投稿候補<",
    },
    "docs/news/index.html": {
        "<h1>更新一覧</h1>": "<h1>最新情報</h1>",
        ">更新一覧<": ">最新情報<",
        ">ツール<": ">同接収益化ツール<",
        ">投稿候補<": ">X投稿候補<",
    },
    "docs/posts/index.html": {
        "<h1>投稿候補</h1>": "<h1>X投稿候補</h1>",
        ">更新一覧<": ">最新情報<",
        ">ツール<": ">同接収益化ツール<",
        ">投稿候補<": ">X投稿候補<",
    },
    "docs/tools/index.html": {
        "<h1>ブラウザ内ツール</h1>": "<h1>同接収益化ツール</h1>",
        "<h2>告知文の型</h2>": "<h2>CTA告知文の型</h2>",
        "通信なし / GitHub Pages 上で動作": "通信なし / GitHub Pages 上でそのまま動作",
        ">更新一覧<": ">最新情報<",
        ">ツール<": ">同接収益化ツール<",
        ">投稿候補<": ">X投稿候補<",
    },
}

for rel_path, mapping in REPLACEMENTS.items():
    path = ROOT / rel_path
    text = path.read_text(encoding="utf-8")
    for old, new in mapping.items():
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")
    print(f"patched: {rel_path}")