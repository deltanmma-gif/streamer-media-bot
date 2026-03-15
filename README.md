# streamer-media-bot

0円運用を前提にした、配信者向け実用品メディアの自動生成基盤です。

このリポジトリは次の最小構成を実装しています。

- RSS / Atom / sitemap からの収集
- SQLite への重複排除つき保存
- 静的サイトの生成 (`docs/`)
- 保存版カード画像の生成 (`docs/assets/cards/`)
- 比較表 / テンプレ / ブラウザ内ツールの生成
- X 投稿候補（本文・ALT案つき）の出力
- GitHub Actions での日次更新

## ディレクトリ構成

- `config/config.json` : 収集ソースと運用設定
- `content/cards/*.json` : 保存版カードの元データ
- `content/tables/*.json` : 比較表の元データ
- `content/tool_data/*.json` : ブラウザ内ツール用データ
- `src/streamer_media_bot/` : 実装本体
- `data/streamer_media.db` : 収集データ保存先
- `docs/` : GitHub Pages 公開対象
- `.github/workflows/daily.yml` : 日次実行ワークフロー

## 初期セットアップ

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## コマンド

### 1. デモデータ投入

```bash
python -m streamer_media_bot seed-demo
```

ネット接続なしでもサイト確認ができるよう、サンプル更新情報を DB に入れます。

### 2. 収集実行

```bash
python -m streamer_media_bot run
```

`config/config.json` に定義した feed / sitemap から更新情報を取得し、SQLite に保存します。

### 3. サイト生成

```bash
python -m streamer_media_bot build
```

### 4. 一括実行

```bash
python -m streamer_media_bot all
```

## GitHub Pages の使い方

1. このリポジトリを **public repository** で作成
2. Settings → Pages → Build and deployment → `Deploy from a branch`
3. Branch を `main` / `/docs` に設定
4. Actions タブで `Daily build` を有効化

## GitHub Actions の使い方

- `daily.yml` は UTC の `17:23` に起動します（JST 02:23）
- 毎時ちょうどを避けています
- 手動実行 (`workflow_dispatch`) にも対応しています

## 収集ソースの追加例

`config/config.json` の `sources` に追加します。

```json
{
  "id": "youtube_teamyoutube",
  "name": "TeamYouTube",
  "kind": "feed",
  "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCkRfArvrzheW2E7b6SVT7vQ",
  "category": "youtube"
}
```

sitemap の場合は `include_patterns` を追加できます。

```json
{
  "id": "twitch_blog",
  "name": "Twitch Blog",
  "kind": "sitemap",
  "url": "https://blog.twitch.tv/sitemap.xml",
  "include_patterns": ["blog", "update", "product"],
  "category": "twitch"
}
```

## 運用メモ

- X 連携は実装していません
- `docs/posts/today.md` に投稿候補を出力します
- 画像 ALT 案もあわせて生成するので、X の UI からそのまま貼り付ける前提です
- 履歴を残したい場合は `data/streamer_media.db` をリポジトリにコミットしてください

## 将来拡張

- 週次サマリをカテゴリ別に生成
- カードのテーマ追加
- ルールベース分類の強化
- ローカル LLM による文案のリライト
