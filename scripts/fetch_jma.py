# -*- coding: utf-8 -*-
"""気象庁「過去の気象データ検索」から大阪の日別気温を取得してJSON化するスクリプト。

対象: 大阪観測所 (prec_no=62, block_no=47772)
取得項目: 日ごとの平均気温・最高気温・最低気温
出力: ../data/<year>.json （年ごとに1ファイル）

使い方:
    python fetch_jma.py            # 2016〜2025年を取得
    python fetch_jma.py 2024       # 指定年のみ取得

気象庁サーバーへの負荷に配慮し、1リクエストごとに1秒待機します。
"""
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

BASE_URL = (
    "https://www.data.jma.go.jp/obd/stats/etrn/view/daily_s1.php"
    "?prec_no=62&block_no=47772&year={year}&month={month}&view="
)
OUT_DIR = Path(__file__).resolve().parent.parent / "data"
YEARS = range(2016, 2026)

# データ行のセル位置（0始まり）: 6=平均気温, 7=最高気温, 8=最低気温
COL_AVG, COL_MAX, COL_MIN = 6, 7, 8


def fetch_html(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.read().decode("utf-8", errors="replace")


def parse_value(cell: str):
    """セル文字列を数値化する。欠損（×, ///, 空欄）は None。

    「8.4 )」「8.4 ]」のような準正常値の記号は取り除いて数値として扱う。
    """
    cell = cell.strip()
    m = re.match(r"-?\d+(\.\d+)?", cell)
    return float(m.group(0)) if m else None


def parse_month(html: str):
    table = re.search(r"<table[^>]*id='tablefix1'.*?</table>", html, re.S)
    if not table:
        # 未来の月などデータが存在しない場合は空扱い
        return [], [], []
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", table.group(0), re.S)
    avg, tmax, tmin = [], [], []
    for row in rows:
        cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S)
        cells = [re.sub(r"<[^>]+>", "", c).strip() for c in cells]
        # 先頭セルが日付（1〜31の整数）の行だけがデータ行
        if not cells or not re.fullmatch(r"\d{1,2}", cells[0]):
            continue
        avg.append(parse_value(cells[COL_AVG]))
        tmax.append(parse_value(cells[COL_MAX]))
        tmin.append(parse_value(cells[COL_MIN]))
    return avg, tmax, tmin


def fetch_year(year: int) -> dict:
    months = []
    for month in range(1, 13):
        url = BASE_URL.format(year=year, month=month)
        print(f"  {year}年{month}月 を取得中...")
        html = fetch_html(url)
        avg, tmax, tmin = parse_month(html)
        months.append({"month": month, "avg": avg, "max": tmax, "min": tmin})
        time.sleep(1)  # サーバー負荷への配慮
    return {"year": year, "source": "気象庁ホームページ", "months": months}


def main():
    years = [int(sys.argv[1])] if len(sys.argv) > 1 else list(YEARS)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for year in years:
        print(f"{year}年:")
        data = fetch_year(year)
        out = OUT_DIR / f"{year}.json"
        out.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        total_days = sum(len(m["avg"]) for m in data["months"])
        print(f"  -> {out.name} 保存（{total_days}日分）")
    print("完了")


if __name__ == "__main__":
    main()
