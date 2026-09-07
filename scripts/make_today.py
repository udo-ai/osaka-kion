# -*- coding: utf-8 -*-
"""「一言比較データ」を生成するスクリプト（毎日GitHub Actionsから実行）。

昨日（日本時間）の大阪の最高・最低気温と平年値の差を計算し、
  - js/today.js      … ページ表示用データ
  - post.txt         … X（旧Twitter）投稿用の文面
  - index.html       … <title> と meta description を書き換え（SEO対策）
を出力・更新します。

使い方:
    python make_today.py
"""
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
SITE_URL = "https://udo-ai.github.io/osaka-kion/"

JST = timezone(timedelta(hours=9))
WEEKDAYS = "月火水木金土日"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def get_day_values(date):
    """指定日の実測値（最高・最低）を返す。データが無ければ None。"""
    path = DATA_DIR / f"{date.year}.json"
    if not path.exists():
        return None
    months = load_json(path)["months"]
    m = months[date.month - 1]
    i = date.day - 1
    if i >= len(m["max"]) or m["max"][i] is None or m["min"][i] is None:
        return None
    return {"tmax": m["max"][i], "tmin": m["min"][i]}


def get_normals(date):
    """指定日の平年値（最高・最低）を返す。"""
    months = load_json(DATA_DIR / "normals.json")["months"]
    m = months[date.month - 1]
    i = min(date.day - 1, len(m["nmax"]) - 1)
    return {"nmax": m["nmax"][i], "nmin": m["nmin"][i]}


def signed(diff: float) -> str:
    """平年比の表記。+1.9 / -0.4 / ±0.0"""
    if abs(diff) < 0.05:
        return "±0.0"
    return ("+" if diff > 0 else "-") + f"{abs(diff):.1f}"


def main():
    # 昨日から最大7日さかのぼって、実測値のある直近の日を使う
    today = datetime.now(JST).date()
    target, values = None, None
    for back in range(1, 8):
        d = today - timedelta(days=back)
        v = get_day_values(d)
        if v:
            target, values = d, v
            break
    if not target:
        raise SystemExit("直近7日分の実測データが見つかりません")

    n = get_normals(target)
    dmax = values["tmax"] - n["nmax"]
    dmin = values["tmin"] - n["nmin"]
    label = f"{target.month}月{target.day}日"
    wd = WEEKDAYS[target.weekday()]

    headline = (
        f"{label}の大阪：最高 {values['tmax']:.1f}℃（平年比 {signed(dmax)}℃）・"
        f"最低 {values['tmin']:.1f}℃（平年比 {signed(dmin)}℃）"
    )

    # --- js/today.js（ページ表示用） ---
    today_js = {
        "date": target.isoformat(),
        "label": label,
        "weekday": wd,
        "tmax": values["tmax"],
        "tmin": values["tmin"],
        "dmax": round(dmax, 1),
        "dmin": round(dmin, 1),
        "headline": headline,
    }
    (ROOT / "js" / "today.js").write_text(
        "// 自動生成ファイル（scripts/make_today.py）\n"
        "window.KION_TODAY = " + json.dumps(today_js, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )

    # --- post.txt（X投稿用） ---
    post = (
        f"【大阪の気温】{label}({wd})\n"
        f"最高 {values['tmax']:.1f}℃（平年比 {signed(dmax)}℃）\n"
        f"最低 {values['tmin']:.1f}℃（平年比 {signed(dmin)}℃）\n"
        f"過去10年の気温グラフはこちら↓\n"
        f"{SITE_URL}\n"
        f"#大阪 #気温"
    )
    (ROOT / "post.txt").write_text(post, encoding="utf-8")

    # --- index.html の <title> と meta description を書き換え ---
    index = ROOT / "index.html"
    html = index.read_text(encoding="utf-8")
    updown = "高め" if dmax > 0.05 else ("低め" if dmax < -0.05 else "平年並み")
    new_title = f"大阪市の気温グラフ｜{label}の最高気温は平年比{signed(dmax)}℃（{updown}）"
    new_desc = (
        f"{headline}。大阪市の過去10年（2016年〜）の最高気温・最低気温を、"
        "平年値（1991〜2020年平均）と重ねた月ごとの折れ線グラフで毎日更新しています。"
        "出典：気象庁ホームページ。"
    )
    html = re.sub(r"<title>.*?</title>", f"<title>{new_title}</title>", html, count=1)
    html = re.sub(
        r'<meta name="description" content=".*?">',
        f'<meta name="description" content="{new_desc}">',
        html,
        count=1,
    )
    index.write_text(html, encoding="utf-8")

    print(headline)
    print("-> js/today.js, post.txt, index.html を更新しました")


if __name__ == "__main__":
    main()
