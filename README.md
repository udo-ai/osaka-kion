# 大阪市の気温グラフ

大阪市の過去10年（2016〜2025年）の最高気温・最低気温を、平年値（1991〜2020年平均）と重ねた月ごとの折れ線グラフで表示する静的Webサイトです。

## 構成

- `index.html` … サイト本体（年タブ + 12か月分のグラフ + まとめ表）
- `css/style.css` … デザイン（スマホ・ダークモード対応）
- `js/app.js` … グラフ描画（Chart.js使用）
- `js/data.js` … 全年のデータをまとめたファイル（自動生成）
- `data/*.json` … 年ごとの日別気温データ（元データ）
- `scripts/fetch_jma.py` … 気象庁サイトから日別気温を取得してJSONを作る
- `scripts/fetch_normals.py` … 気象庁サイトから日ごとの平年値を取得する
- `scripts/build_data_js.py` … JSONをまとめて `js/data.js` を生成する

## データの更新方法

```
python scripts/fetch_jma.py 2026   # 例：2026年分を取得
python scripts/build_data_js.py    # data.js を再生成
```

## 毎日の自動更新

GitHub Actions（`.github/workflows/daily-update.yml`）が毎朝10:30（日本時間）に実行され、

1. 気象庁から今年のデータを再取得
2. 「一言比較」（昨日の気温と平年値の差）を生成してページとタイトルに反映
3. 変更をコミットしてGitHub Pagesに自動反映
4. X APIキーが設定されていればXに自動投稿

## X（旧Twitter）自動投稿の設定手順

1. 投稿に使うXアカウントでログインした状態で https://developer.x.com にアクセスし、無料プラン（Free）で開発者登録する
2. アプリを作成し、「User authentication settings」で **Read and write** 権限を設定する
3. 以下の4つのキーを取得する
   - API Key / API Key Secret（Consumer Keys）
   - Access Token / Access Token Secret（権限変更後に再生成すること）
4. GitHubのリポジトリページ → Settings → Secrets and variables → Actions → New repository secret で、次の名前で4つ登録する
   - `X_API_KEY` / `X_API_SECRET` / `X_ACCESS_TOKEN` / `X_ACCESS_SECRET`
5. Actionsタブから「毎日更新」を手動実行（Run workflow）してテスト投稿を確認する

キー未設定の間は投稿はスキップされ、サイトの更新だけが動きます。

## 広告について

`index.html` 内の `<div class="ad-slot">`（上部・下部の2か所）に広告タグを貼り付けると表示されます。空のままなら何も表示されません。

## 出典

気象庁ホームページ「過去の気象データ検索」（大阪）のデータを加工して作成。平年値は1991〜2020年の30年平均。
