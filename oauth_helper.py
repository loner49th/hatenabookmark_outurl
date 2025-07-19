#!/usr/bin/env python3
import requests
from requests_oauthlib import OAuth1
import webbrowser
import os
from dotenv import load_dotenv
from urllib.parse import parse_qs, urlencode, quote_plus
import re

load_dotenv()

def get_oauth_tokens():
    """
    はてなOAuthのアクセストークンを取得する
    
    Returns:
        tuple: (access_token, access_token_secret) または (None, None)
    """
    consumer_key = os.getenv("HATENA_CONSUMER_KEY")
    consumer_secret = os.getenv("HATENA_CONSUMER_SECRET")
    
    if not consumer_key or not consumer_secret:
        print("エラー: HATENA_CONSUMER_KEYとHATENA_CONSUMER_SECRETを.envファイルに設定してください")
        return None, None
    
    # Step 1: Request Token取得
    request_token_url = "https://www.hatena.com/oauth/initiate"
    
    # OAuth1認証オブジェクトを作成 (callback_uri='oob'を指定)
    auth = OAuth1(
        consumer_key,
        client_secret=consumer_secret,
        callback_uri='oob',
        signature_method='HMAC-SHA1',
        signature_type='auth_header'
    )
    
    try:
        # Request Tokenを取得（read_privateスコープを指定）
        # scopeはPOSTのbodyで送信する必要がある
        data = {'scope': 'read_public,read_private'}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(request_token_url, auth=auth, data=data, headers=headers)
        
        response.raise_for_status()
        
        # レスポンスをパース
        token_data = parse_qs(response.text)
        
        if 'oauth_token' not in token_data or 'oauth_token_secret' not in token_data:
            print("エラー: Request Tokenの取得に失敗しました")
            return None, None
        
        resource_owner_key = token_data['oauth_token'][0]
        resource_owner_secret = token_data['oauth_token_secret'][0]
        
    except Exception as e:
        print("Request Token取得エラー: 認証に失敗しました")
        return None, None
    
    # Step 2: 認証URL生成とユーザー認証
    authorization_url = "https://www.hatena.ne.jp/oauth/authorize"
    # URLエスケープを適用
    auth_url = f"{authorization_url}?oauth_token={quote_plus(resource_owner_key)}"
    
    print(f"認証URL: {auth_url}")
    
    # ブラウザを自動で開く
    try:
        webbrowser.open(auth_url)
    except:
        pass
    
    # 認証コード（verifier）の入力を求める
    verifier = input("verifierコードを入力してください: ").strip()
    
    # verifierの形式検証（英数字のみ、適切な長さ）
    if not verifier:
        print("verifierが入力されませんでした。")
        return None, None
    
    if not re.match(r'^[a-zA-Z0-9+/=]+$', verifier) or len(verifier) < 10:
        print("無効なverifierコードです。")
        return None, None
    
    # Step 3: Access Token取得
    access_token_url = "https://www.hatena.com/oauth/token"
    
    # Access Token取得用の認証オブジェクト
    auth = OAuth1(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
        verifier=verifier,
        signature_method='HMAC-SHA1',
        signature_type='auth_header'
    )
    
    try:
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(access_token_url, auth=auth, headers=headers)
        
        response.raise_for_status()
        
        # レスポンスをパース
        access_data = parse_qs(response.text)
        
        if 'oauth_token' not in access_data or 'oauth_token_secret' not in access_data:
            print("エラー: Access Tokenの取得に失敗しました")
            return None, None
        
        access_token = access_data['oauth_token'][0]
        access_token_secret = access_data['oauth_token_secret'][0]
        
        print("✓ Access Token取得成功!")
        
        return access_token, access_token_secret
        
    except Exception as e:
        print(f"Access Token取得エラー: {e}")
        return None, None

def update_env_file(access_token, access_token_secret):
    """
    .envファイルにアクセストークンを保存する
    
    Args:
        access_token: アクセストークン
        access_token_secret: アクセストークンシークレット
    """
    env_file = ".env"
    
    # 既存の.envファイルを読み込み
    env_lines = []
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            env_lines = f.readlines()
    
    # アクセストークンの行を更新または追加
    updated_lines = []
    token_updated = False
    secret_updated = False
    
    for line in env_lines:
        if line.startswith('HATENA_ACCESS_TOKEN='):
            updated_lines.append(f'HATENA_ACCESS_TOKEN={access_token}\n')
            token_updated = True
        elif line.startswith('HATENA_ACCESS_TOKEN_SECRET='):
            updated_lines.append(f'HATENA_ACCESS_TOKEN_SECRET={access_token_secret}\n')
            secret_updated = True
        else:
            updated_lines.append(line)
    
    # 新しい行を追加（存在しない場合）
    if not token_updated:
        updated_lines.append(f'HATENA_ACCESS_TOKEN={access_token}\n')
    if not secret_updated:
        updated_lines.append(f'HATENA_ACCESS_TOKEN_SECRET={access_token_secret}\n')
    
    # ファイルに書き込み
    with open(env_file, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)
    
    print(f"✓ アクセストークンを {env_file} に保存しました")

def main():
    """
    OAuth認証フローを実行してアクセストークンを取得・保存し、ブックマークを取得する
    """
    print("はてなOAuth認証を開始します...")
    
    access_token, access_token_secret = get_oauth_tokens()
    
    if access_token and access_token_secret:
        # .envファイルに保存
        update_env_file(access_token, access_token_secret)
        print("✓ OAuth認証が完了しました！")
        
        # 直接ブックマーク取得を実行
        print("「後で読む」ブックマークを取得しています...")
        from hatena_bookmark_api import get_read_later_bookmarks, save_bookmarks_to_file
        
        # 環境変数を再読み込み
        load_dotenv()
        
        bookmarks = get_read_later_bookmarks()
        
        if bookmarks:
            print(f"「後で読む」ブックマーク数: {len(bookmarks)}")
            
            # テキストファイルに保存
            save_bookmarks_to_file(bookmarks)
        else:
            print("ブックマークが取得できませんでした")
    else:
        print("OAuth認証に失敗しました。")

if __name__ == "__main__":
    main()