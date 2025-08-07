#!/usr/bin/env python3
import re
from pathlib import Path

BASE_DIR = Path(".")
TXT_FILES = [
    BASE_DIR / "BS EN 18031-1-2024.txt",
    BASE_DIR / "BS EN 18031-2-2024.txt",
    BASE_DIR / "BS EN 18031-3-2024.txt",
]

BRACKET_RE = re.compile(r"\[([^\[\]]+)\]", re.DOTALL)

for txt in TXT_FILES:
    if not txt.exists():
        continue

    content = txt.read_text(encoding="utf-8")

    raw_list = BRACKET_RE.findall(content)

    clean_list = [
        re.sub(r"-?\n\s*", "", block).strip()   # 去掉 -↵ 或 ↵
        for block in raw_list
    ]


    DIGIT_ONLY = re.compile(r"^-?\d+(?:\.\d+)?$")
    seen = set()
    final = [
        x for x in clean_list
        if x and not DIGIT_ONLY.fullmatch(x.strip()) and not (x in seen or seen.add(x))
    ]

    out = txt.with_name(txt.stem + "_name.txt")
    out.write_text("\n".join(final), encoding="utf-8")
    print(f"[✓] {txt.name} → {len(final)} 条 → {out.name}")