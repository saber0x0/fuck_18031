#!/usr/bin/env python3
import re
from pathlib import Path

BASE_DIR = Path(".")
TXT_FILES = [
    BASE_DIR / "BS EN 18031-1-2024_name.txt",
    BASE_DIR / "BS EN 18031-2-2024_name.txt",
    BASE_DIR / "BS EN 18031-3-2024_name.txt",
]

EINFO_RE = re.compile(r"(E\.Info\.\S+)", re.IGNORECASE)

for txt in TXT_FILES:
    if not txt.exists():
        continue

    content = txt.read_text(encoding="utf-8")

    raw = EINFO_RE.findall(content)

    clean = [r.strip() for r in raw]

    seen, unique = set(), []
    for item in clean:
        if item and item not in seen:
            seen.add(item)
            unique.append(item)

    out = txt.with_name(txt.stem + "_E_info.txt")
    out.write_text("\n".join(unique), encoding="utf-8")
    print(f"[✓] {txt.name} → {len(unique)} 条 → {out.name}")