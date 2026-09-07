# -*- coding: utf-8 -*-
"""post.txt の内容をX（旧Twitter）に自動投稿するスクリプト。

GitHub Actionsから実行されます。以下の4つの環境変数（GitHub Secrets）が
すべて設定されている場合のみ投稿し、未設定なら何もせず正常終了します。

    X_API_KEY        … APIキー（Consumer Key）
    X_API_SECRET     … APIキーシークレット（Consumer Secret）
    X_ACCESS_TOKEN   … アクセストークン
    X_ACCESS_SECRET  … アクセストークンシークレット

必要ライブラリ: tweepy（Actions内で pip install tweepy 済み）
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

KEYS = ["X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_SECRET"]


def main():
    env = {k: os.environ.get(k, "").strip() for k in KEYS}
    if not all(env.values()):
        missing = [k for k, v in env.items() if not v]
        print(f"X APIキーが未設定のため投稿をスキップします（未設定: {', '.join(missing)}）")
        return 0

    post_file = ROOT / "post.txt"
    if not post_file.exists():
        print("post.txt がありません。make_today.py を先に実行してください")
        return 1
    text = post_file.read_text(encoding="utf-8").strip()

    import tweepy

    client = tweepy.Client(
        consumer_key=env["X_API_KEY"],
        consumer_secret=env["X_API_SECRET"],
        access_token=env["X_ACCESS_TOKEN"],
        access_token_secret=env["X_ACCESS_SECRET"],
    )
    res = client.create_tweet(text=text)
    print(f"Xに投稿しました: tweet id = {res.data['id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
