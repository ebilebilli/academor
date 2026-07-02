#!/usr/bin/env python3
"""Fill empty portal-related msgstr entries in az/ru django.po from JSON maps."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCALE = ROOT / "locale"


def load_map(lang):
    path = LOCALE / f"_{lang}_missing_for_portal.json"
    if not path.exists():
        return {}
    items = json.loads(path.read_text(encoding="utf-8"))
    # JSON is a list of English msgids only — caller must supply translations separately.
    return {item: item for item in items}


def apply_translations(lang, translations):
    po_path = LOCALE / lang / "LC_MESSAGES" / "django.po"
    text = po_path.read_text(encoding="utf-8")
    blocks = text.split("\n\n")
    updated = 0

    def escape_po(value):
        return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")

    new_blocks = []
    for block in blocks:
        if "templates/portals/" not in block and "portals/static/portals/" not in block:
            new_blocks.append(block)
            continue
        if not re.search(r'^msgstr ""$', block, re.M):
            new_blocks.append(block)
            continue
        match = re.search(r'^msgid "(.*)"', block, re.M | re.S)
        if not match:
            new_blocks.append(block)
            continue
        msgid = match.group(1)
        if msgid not in translations:
            new_blocks.append(block)
            continue
        msgstr = escape_po(translations[msgid])
        block = re.sub(r'^msgstr ""$', f'msgstr "{msgstr}"', block, count=1, flags=re.M)
        updated += 1
        new_blocks.append(block)

    po_path.write_text("\n\n".join(new_blocks), encoding="utf-8")
    print(f"{lang}: updated {updated} entries")


if __name__ == "__main__":
    az_path = LOCALE / "portal_translations_az.json"
    ru_path = LOCALE / "portal_translations_ru.json"
    if az_path.exists():
        apply_translations("az", json.loads(az_path.read_text(encoding="utf-8")))
    if ru_path.exists():
        apply_translations("ru", json.loads(ru_path.read_text(encoding="utf-8")))
