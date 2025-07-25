# はてなブックマーク「あとで読む」取得ツール

はてなブックマークの「あとで読む」ブックマークをOAuth APIで取得するPythonツールです。

## 📋 現在の状況（2025年7月）

### ✅ 動作確認済み機能
- **OAuth1.0a認証**: `read_private`スコープ付きで完全動作
- **「あとで読む」ブックマーク取得**: マイブックマーク全文検索APIを使用
- **ページング対応**: 全件取得（最大100件ずつ）
- **日付フィルタリング**: 1ヶ月以内のブックマークのみ対象
- **テキストファイル出力**: はてな記法形式で保存
- **大量ブックマーク対応**: 実際に76件の取得実績あり

### 🔍 技術的発見
- **「あとで読む」の格納場所**: タグではなくコメント欄に`[あとで読む]`として保存
- **検索API活用**: `https://b.hatena.ne.jp/my/search/json` で全文検索を実行


## 🛠️ 必要な環境

- Python 3.12以上
- uv (推奨)

## 📦 インストール

```bash
# リポジトリをクローン
git clone <repository-url>
cd hatenabookmark

# 依存関係をインストール
uv sync
```

## 🚀 使用方法

### 1. はてなOAuthアプリケーション登録

1. [はてなOAuth開発者向け設定ページ](https://www.hatena.com/oauth/develop)でアプリケーションを登録
2. **重要**: `read_private`スコープを有効にする
3. Consumer KeyとConsumer Secretを取得

### 2. 認証情報設定

`.env`ファイルを作成:

```env
HATENA_CONSUMER_KEY=your_consumer_key
HATENA_CONSUMER_SECRET=your_consumer_secret
```

### 3. 初回OAuth認証

```bash
uv run oauth_helper.py
```

ブラウザが開き、OAuth認証を行います。verifierコードを入力してアクセストークンを取得します。

### 4. 「あとで読む」ブックマーク取得

```bash
uv run hatena_bookmark_api.py
```

スクリプトは以下の処理を実行します：
- マイブックマーク全文検索APIで「あとで読む」を検索
- ページングで全件取得（100件ずつ）
- 1ヶ月以内のブックマークをフィルタリング
- はてな記法形式でテキストファイルに保存

## 📁 出力形式

テキストファイル（`hatena_bookmarks_YYYYMMDD_HHMMSS.txt`）に以下の形式で保存：

```
### ページタイトル
[URL:embed:cite]

### 次のページタイトル
[URL:embed:cite]
```

## 🔧 実装のポイント

### 1. 「あとで読む」の検索方法
はてなブックマークでは「あとで読む」はタグではなく、コメント欄に`[あとで読む]`として保存されています。そのため、全文検索APIで`q=あとで読む`パラメータを使用して検索します。

### 2. ページング実装
API制限により1回のリクエストで最大100件まで取得可能。`offset`パラメータを使用して全件取得します：

```python
search_params = {
    'q': 'あとで読む',
    'limit': 100,
    'of': offset  # 0, 100, 200, ...
}
```

### 3. 日付フィルタリング
Unix timestamp形式での日付比較により、指定期間内のブックマークのみを抽出します。

### 4. エラーハンドリング
HTML応答（認証エラー）やJSON形式エラーを適切に処理し、確実にデータを取得します。

## 📝 ファイル構成

- `oauth_helper.py` - OAuth認証（初回のみ）
- `hatena_bookmark_api.py` - 「あとで読む」ブックマーク取得メインスクリプト
- `pyproject.toml` - プロジェクト設定
- `.env` - 認証情報（ユーザー作成）
- `hatena_bookmarks_*.txt` - 出力ファイル（日時付き）

## ⚠️ 注意事項・制限事項

- **検索対象**: コメント欄に`[あとで読む]`が含まれるブックマークのみが対象
- **日付フィルタ**: デフォルトで1ヶ月以内のブックマークのみを取得
- **API制限**: 1回のリクエストで最大100件まで取得可能
- **認証情報管理**: `.env`ファイルは適切に管理してください（.gitignoreに追加済み）

## 🔗 関連リンク

- [はてなOAuth開発者向け設定](https://www.hatena.com/oauth/develop)
- [はてなブックマーク マイブックマーク全文検索API](https://b.hatena.ne.jp/my/search/json)
- [はてなブックマークAPI仕様](https://developer.hatena.ne.jp/ja/documents/bookmark/apis/rest)
- [OAuth 1.0a 仕様](https://tools.ietf.org/html/rfc5849)

## 📊 開発履歴

- **2025年7月19日**: 「あとで読む」ブックマーク取得機能完成
  - マイブックマーク全文検索APIを活用
  - ページング機能実装
  - 日付フィルタリング追加