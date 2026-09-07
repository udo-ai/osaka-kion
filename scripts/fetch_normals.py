# -*- coding: utf-8 -*-
"""気象庁「日ごとの平年値」（大阪）を取得して data/normals.json を作るスクリプト。

平年値は1991〜2020年の30年平均。最高気温・最低気温の日別平年値を取得します。
2月は29日分（2月29日を含む）あります。

使い方:
    python fetch_normals.py
"""
import json
import re
import time
import urllib.request
from pathlib import Path

BASE_URL = (
    "https://www.data.jma.go.jp/obd/stats/etrn/view/nml_sfc_d.php"
    "?prec_no=62&block_no=47772&year=&month={month}&day=&view="
)
OUT = Path(__file__).resolve().parent.parent / "data" / "normals.json"

# データ行のセル位置（0始まり）: 0=日, 1=降水量, 2=平均気温, 3=最高気温, 4=最低気温
COL_NMAX, COL_NMIN = 3, 4


def fetch_html(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.read().decode("utf-8", errors="replace")


def parse_value(cell: str):
    m = re.match(r"-?\d+(\.\d+)?", cell.strip())
    return float(m.group(0)) if m else None


def parse_month(html: str):
    table = re.search(r"<table[^>]*id='tablefix1'.*?</table>", html, re.S)
    if not table:
        raise ValueError("データ表（tablefix1）が見つかりません")
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", table.group(0), re.S)
    nmax, nmin = [], []
    for row in rows:
        cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S)
        cells = [re.sub(r"<[^>]+>", "", c).strip() for c in cells]
        # 先頭セルが「1日」「12日」のような日付の行だけがデータ行
        if not cells or not re.fullmatch(r"\d{1,2}日", cells[0]):
            continue
        nmax.append(parse_value(cells[COL_NMAX]))
        nmin.append(parse_value(cells[COL_NMIN]))
    return nmax, nmin


def main():
    months = []
    for month in range(1, 13):
        print(f"{month}月の平年値を取得中...")
        nmax, nmin = parse_month(fetch_html(BASE_URL.format(month=month)))
        months.append({"month": month, "nmax": nmax, "nmin": nmin})
        time.sleep(1)  # サーバー負荷への配慮
    data = {
        "source": "気象庁ホームページ（日ごとの平年値・大阪）",
        "period": "1991-2020",
        "months": months,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    total = sum(len(m["nmax"]) for m in months)
    print(f"-> {OUT.name} 保存（{total}日分）")


if __name__ == "__main__":
    main()
