#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# test

import fitz 
import re
import json
import csv
from pathlib import Path
from typing import List, Dict

# ---------- 配置 ----------
BASE_DIR = Path("~/tools/fuck_18031/18031")
PDF_FILES = [
    BASE_DIR / "BS EN 18031-1-2024.pdf",
    BASE_DIR / "BS EN 18031-2-2024.pdf",
    BASE_DIR / "BS EN 18031-3-2024.pdf"
]
OUT_JSON = BASE_DIR / "en18031_einfo.json"
OUT_CSV  = BASE_DIR / "en18031_einfo.csv"
# ---------------------------

# 正则：匹配 E.info 字段名 & 值
EINFO_RE = re.compile(
    r'(?P<field>E\.info[^\s:：]*)[\s:：]*(?P<value>.+?)(?=\n|$)',
    re.IGNORECASE
)

def extract_from_pdf(pdf_path: Path) -> List[Dict]:
    """
    从单份 PDF 提取 E.info 字段
    返回 list[dict]
    """
    part_match = re.search(r'18031-(\d)', pdf_path.name)
    if not part_match:
        print(f"[!] 无法从文件名推断 Part：{pdf_path.name}")
        return []
    part_no = part_match.group(1)

    doc = fitz.open(pdf_path)
    records = []

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        text = page.get_text("text")
        lines = text.splitlines()
        for lineno, line in enumerate(lines, 1):
            for m in EINFO_RE.finditer(line):
                clause_match = re.search(r'(\d+(?:\.\d+)+)', line)
                clause = clause_match.group(1) if clause_match else ""
                records.append({
                    "part": part_no,
                    "clause": clause,
                    "page": page_idx + 1,
                    "lineno": lineno,
                    "field": m.group("field").strip(),
                    "value": m.group("value").strip()
                })
    return records

def main():
    all_records: List[Dict] = []
    for pdf in PDF_FILES:
        if pdf.exists():
            print(f"[+] 处理 {pdf.name} …")
            all_records.extend(extract_from_pdf(pdf))
        else:
            print(f"[!] 文件不存在：{pdf}")

    # 写 JSON
    with open(OUT_JSON, 'w', encoding='utf-8') as fj:
        json.dump(all_records, fj, ensure_ascii=False, indent=2)
    # 写 CSV
    if all_records:
        with open(OUT_CSV, 'w', newline='', encoding='utf-8-sig') as fc:
            writer = csv.DictWriter(fc, fieldnames=all_records[0].keys())
            writer.writeheader()
            writer.writerows(all_records)

    print(f"[✓] 共提取 {len(all_records)} 条 E.info 记录")
    print(f"    JSON -> {OUT_JSON}")
    print(f"    CSV  -> {OUT_CSV}")

if __name__ == '__main__':
    main()