#!/usr/bin/env python3
import fitz  # PyMuPDF
from pathlib import Path

BASE_DIR = Path(".")
PDFS = [
    BASE_DIR / "BS EN 18031-1-2024.pdf",
    BASE_DIR / "BS EN 18031-2-2024.pdf",
    BASE_DIR / "BS EN 18031-3-2024.pdf",
]

for pdf in PDFS:
    if not pdf.exists():
        print(f"[!] 跳过缺失文件 {pdf.name}")
        continue
    doc = fitz.open(pdf)
    out_txt = pdf.with_suffix(".txt")
    with open(out_txt, "w", encoding="utf-8") as f:
        for page in doc:
            f.write(page.get_text("text"))
    print(f"[✓] {pdf.name} → {out_txt.name}")