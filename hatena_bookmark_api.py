#!/usr/bin/env python3
import requests
from requests_oauthlib import OAuth1
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

def get_read_later_bookmarks():
    """
    はてなブックマークから「後で読む」タグのブックマークを取得
    マイブックマーク全文検索APIを使用（はてなブックマークプラス必須）
    
    Returns:
        list: [{'url': str, 'title': str, 'comment': str, 'tags': list}, ...]
    """
    # OAuth認証情報を環境変数から取得
    consumer_key = os.getenv("HATENA_CONSUMER_KEY")
    consumer_secret = os.getenv("HATENA_CONSUMER_SECRET")
    access_token = os.getenv("HATENA_ACCESS_TOKEN")
    access_token_secret = os.getenv("HATENA_ACCESS_TOKEN_SECRET")
    
    if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
        print("エラー: OAuth認証情報を.envファイルに設定してください")
        return []
    
    # OAuth1認証オブジェクトを生成
    auth = OAuth1(
        consumer_key,
        consumer_secret,
        access_token,
        access_token_secret,
        signature_type='auth_header'
    )

    try:
        # マイブックマーク全文検索APIで「あとで読む」ブックマークを取得
        search_api_url = "https://b.hatena.ne.jp/my/search/json"
        
        # 全ての「あとで読む」ブックマークを取得（ページング対応）
        all_entries = []
        offset = 0
        limit = 100  # 最大値
        
        while True:
            search_params = {
                'q': 'あとで読む',  # コメントで「あとで読む」を検索
                'limit': limit,
                'of': offset
            }
        
            print(f"検索中... offset: {offset}, limit: {limit}")
            
            try:
                # OAuth認証でAPIアクセス
                response = requests.get(search_api_url, params=search_params, auth=auth)
                
                if response.status_code == 200:
                    content_type = response.headers.get('Content-Type', '')
                    
                    # HTMLが返されている場合はエラー
                    if 'text/html' in content_type:
                        print("認証エラー: ログインが必要です")
                        break
                    else:
                        try:
                            search_results = response.json()
                            
                            if 'bookmarks' in search_results:
                                bookmarks = search_results['bookmarks']
                                if bookmarks:
                                    batch_entries = []
                                    for bookmark in bookmarks:
                                        entry_info = bookmark.get('entry', {})
                                        
                                        batch_entries.append({
                                            'url': entry_info.get('url', ''),
                                            'title': entry_info.get('title', ''),
                                            'comment': bookmark.get('comment', ''),
                                            'tags': bookmark.get('tags', []),
                                            'date': bookmark.get('timestamp', '')
                                        })
                                    
                                    all_entries.extend(batch_entries)
                                    
                                    # 次のページがあるかチェック
                                    if len(batch_entries) < limit:
                                        break
                                    else:
                                        offset += limit
                                        continue
                                else:
                                    break
                                
                            elif 'error' in search_results:
                                break
                            else:
                                break
                                    
                        except ValueError as e:
                            break
                        
                elif response.status_code == 401:
                    print("認証エラー")
                    break
                elif response.status_code == 403:
                    print("アクセス拒否")
                    break
                elif response.status_code == 404:
                    print("エンドポイントが見つかりません")
                    break
                    
            except Exception as e:
                break
        
        # 日付フィルター処理
        if all_entries:
            
            # 1か月以上前のブックマークを除外
            one_month_ago = datetime.now() - timedelta(days=30)
            one_month_ago_timestamp = int(one_month_ago.timestamp())
            
            recent_entries = []
            old_entries = []
            
            for entry in all_entries:
                bookmark_timestamp = entry.get('date', 0)
                if isinstance(bookmark_timestamp, (int, float)) and bookmark_timestamp > one_month_ago_timestamp:
                    recent_entries.append(entry)
                else:
                    old_entries.append(entry)
            
            return recent_entries if recent_entries else []
        else:
            return []
        
    except Exception as e:
        return []

def save_bookmarks_to_file(bookmarks, filename=None):
    """
    ブックマーク一覧をテキストファイルに保存
    
    Args:
        bookmarks: ブックマークのリスト
        filename: 保存するファイル名（省略時は日時から自動生成）
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"hatena_bookmarks_{timestamp}.txt"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            for bookmark in bookmarks:
                f.write(f"### {bookmark['title']}\n")
                f.write(f"[{bookmark['url']}:embed:cite]\n")
                f.write("\n")
        
        print(f"ブックマーク一覧を {filename} に保存しました")
        return filename
        
    except IOError as e:
        print(f"ファイル保存エラー: {e}")
        return None

def main():
    # OAuth認証情報を環境変数から取得
    bookmarks = get_read_later_bookmarks()
    
    if bookmarks:
        print(f"「後で読む」ブックマーク数: {len(bookmarks)}")
        
        # コンソールに表示
        for i, bookmark in enumerate(bookmarks, 1):
            print(f"{i}. {bookmark['title']}")
            print(f"   URL: {bookmark['url']}")
            print(f"   コメント: {bookmark['comment']}")
            print(f"   タグ: {', '.join(bookmark['tags'])}")
            print(f"   日付: {bookmark['date']}")
            print()
        
        # テキストファイルに保存
        save_bookmarks_to_file(bookmarks)
    else:
        print("ブックマークが取得できませんでした")

if __name__ == "__main__":
    main()