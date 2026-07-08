#!/usr/bin/env python3
"""Fill empty portal-related msgstr entries in az/en/ru django.po from JSON maps.

Usage (local):
    cd academor
    python scripts/apply_portal_i18n.py

Usage (Docker):
    docker compose exec web python academor/scripts/apply_portal_i18n.py
    python academor/manage.py compilemessages
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCALE = ROOT / "locale"


def extract_msgid(block):
    multiline = re.search(r'^msgid ""\n((?:".*"\n)+)', block, re.M)
    if multiline:
        return "".join(re.findall(r'"(.*)"', multiline.group(1)))
    # Match single-line msgid only — do not use re.S or greedy .* would swallow msgstr.
    match = re.search(r'^msgid "((?:\\.|[^"\\])*)"\s*$', block, re.M)
    return match.group(1) if match else ""


def escape_po(value):
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def apply_translations(lang, translations):
    po_path = LOCALE / lang / "LC_MESSAGES" / "django.po"
    if not po_path.exists():
        print(f"{lang}: skipped — {po_path} not found", file=sys.stderr)
        return 0

    text = po_path.read_text(encoding="utf-8")
    blocks = text.split("\n\n")
    updated = 0
    new_blocks = []

    for block in blocks:
        if "templates/portals/" not in block and "portals/static/portals/" not in block and "portals/" not in block:
            new_blocks.append(block)
            continue
        if not re.search(r'^msgstr ""$', block, re.M):
            new_blocks.append(block)
            continue
        msgid = extract_msgid(block)
        if not msgid or msgid not in translations:
            new_blocks.append(block)
            continue
        msgstr = escape_po(translations[msgid])
        block = re.sub(r'^msgstr ""$', f'msgstr "{msgstr}"', block, count=1, flags=re.M)
        updated += 1
        new_blocks.append(block)

    po_path.write_text("\n\n".join(new_blocks), encoding="utf-8")
    print(f"{lang}: updated {updated} entries")
    return updated


def main():
    total = 0
    for lang in ("az", "en", "ru"):
        path = LOCALE / f"portal_translations_{lang}.json"
        if not path.exists():
            print(f"{lang}: skipped — {path.name} not found")
            continue
        translations = json.loads(path.read_text(encoding="utf-8"))
        total += apply_translations(lang, translations)
    print(f"Done — {total} entries updated total")


if __name__ == "__main__":
    main()
