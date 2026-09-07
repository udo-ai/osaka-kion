# -*- coding: utf-8 -*-
"""data/*.json を1つの js/data.js にまとめるスクリプト。

サイトをサーバーなし（index.htmlをダブルクリック）でも開けるように、
データをJavaScriptファイルとして読み込む形式に変換します。

使い方:
    python build_data_js.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUT = ROOT / "js" / "data.js"


def main():
    combined = {}
    normals = None
    for f in sorted(DATA_DIR.glob("*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        if f.stem == "normals":
            normals = data
        else:
            combined[str(data["year"])] = data
    js = "// 自動生成ファイル（scripts/build_data_js.py で再生成できます）\n"
    js += "window.KION_DATA = " + json.dumps(combined, ensure_ascii=False) + ";\n"
    if normals is not None:
        js += "window.KION_NORMALS = " + json.dumps(normals, ensure_ascii=False) + ";\n"
    OUT.write_text(js, encoding="utf-8")
    print(f"{OUT.name} を生成しました（{len(combined)}年分, {OUT.stat().st_size // 1024}KB）")


if __name__ == "__main__":
    main()
