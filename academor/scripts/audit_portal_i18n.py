#!/usr/bin/env python3
"""List portal-related msgids with empty translations in az/ru po files."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCALE = ROOT / "locale"


def portal_missing(lang):
    po_path = LOCALE / lang / "LC_MESSAGES" / "django.po"
    text = po_path.read_text(encoding="utf-8")
    blocks = text.split("\n\n")
    missing = []
    for block in blocks:
        if "templates/portals/" not in block and "portals/static/portals/" not in block:
            continue
        if not re.search(r'^msgstr ""$', block, re.M):
            continue
        match = re.search(r'^msgid "(.*)"', block, re.M | re.S)
        if not match:
            continue
        msgid = match.group(1)
        if msgid:
            missing.append(msgid)
    return missing


if __name__ == "__main__":
    for lang in ("az", "ru"):
        items = portal_missing(lang)
        print(f"{lang}: {len(items)} missing")
        for item in items[:30]:
            print(f"  - {item[:90]}")
