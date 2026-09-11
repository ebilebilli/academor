"""Shrink the portal icon webfonts to only the glyphs the portal actually renders.

Both icon fonts are preloaded on every portal page, which made them the largest
asset cost in the portal shell:

  * Tabler        867.6 KB font, ~5900 glyphs, ~80 used
  * Bootstrap     131 KB font + 97 KB CSS, 2078 glyphs, ~80 used

Tabler uses a hand-maintained CSS file as the source of truth, so this reads the
codepoints straight out of it. Bootstrap Icons ships the full upstream CSS, so
this scans the project for `bi-*` class names and generates a trimmed stylesheet
next to it.

Run after adding or removing icons, then commit the regenerated font/CSS:

    pip install fonttools brotli
    python scripts/subset_icon_fonts.py

IMPORTANT: the fonts are subset in place, so the working copy is no longer the
pristine upstream file. If you add an icon whose glyph was dropped by an earlier
run, this script fails with a clear message — restore the original first:

    git checkout <first-commit-that-added-it> -- <font path>

fonttools/brotli are build-time only and deliberately not in requirements.txt.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
STATIC_ROOT = REPO_ROOT / 'academor' / 'portals' / 'static' / 'portals'
TEMPLATE_ROOT = REPO_ROOT / 'academor' / 'templates'

TABLER_CSS = STATIC_ROOT / 'css' / 'portal-tabler-icons.css'
TABLER_FONT = STATIC_ROOT / 'vendors' / 'tabler-icons' / 'fonts' / 'tabler-icons.woff2'

BOOTSTRAP_DIR = STATIC_ROOT / 'vendors' / 'bootstrap-icons'
BOOTSTRAP_VENDOR_CSS = BOOTSTRAP_DIR / 'bootstrap-icons.css'
BOOTSTRAP_FONT = BOOTSTRAP_DIR / 'fonts' / 'bootstrap-icons.woff2'
BOOTSTRAP_SUBSET_CSS = STATIC_ROOT / 'css' / 'portal-bootstrap-icons.css'

TABLER_RULE_RE = re.compile(r'\.(ti-[a-z0-9-]+):before\s*\{\s*content:\s*"\\([0-9a-fA-F]+)"')
BOOTSTRAP_RULE_RE = re.compile(r'\.(bi-[a-z0-9-]+)::before\s*\{\s*content:\s*"\\([0-9a-fA-F]+)"')


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8', errors='ignore')


def _scan_for_classes(prefix: str) -> set[str]:
    """Find every `prefix-name` token used in templates, JS and CSS."""
    pattern = re.compile(rf'\b{prefix}-[a-z0-9-]+\b')
    found: set[str] = set()
    roots = [
        (TEMPLATE_ROOT, '*.html'),
        (STATIC_ROOT / 'js', '*.js'),
        (STATIC_ROOT / 'css', '*.css'),
    ]
    for root, glob in roots:
        if not root.exists():
            continue
        for path in root.rglob(glob):
            found.update(pattern.findall(_read(path)))
    return found


def _font_codepoints(font_path: Path) -> set[int]:
    from fontTools.ttLib import TTFont

    font = TTFont(font_path)
    available: set[int] = set()
    for table in font['cmap'].tables:
        available.update(table.cmap.keys())
    return available


def _run_subset(font_path: Path, codepoints: list[str], label: str) -> None:
    present = _font_codepoints(font_path)
    missing = [cp for cp in codepoints if int(cp, 16) not in present]
    if missing:
        raise SystemExit(
            f'{label}: {len(missing)} glyph(s) are not in {font_path.name}: '
            + ', '.join(f'U+{cp.upper()}' for cp in missing)
            + '\nThe font has probably already been subset. Restore the pristine '
            'upstream file from git history before re-running.'
        )

    before = font_path.stat().st_size
    output = font_path.with_suffix('.subset.woff2')
    subprocess.run(
        [
            sys.executable,
            '-m',
            'fontTools.subset',
            str(font_path),
            '--unicodes=' + ','.join(f'U+{cp.upper()}' for cp in codepoints),
            '--flavor=woff2',
            '--layout-features=',
            '--no-hinting',
            '--desubroutinize',
            f'--output-file={output}',
        ],
        check=True,
    )
    after = output.stat().st_size
    output.replace(font_path)

    survived = _font_codepoints(font_path)
    dropped = [cp for cp in codepoints if int(cp, 16) not in survived]
    if dropped:
        raise SystemExit(
            f'{label}: subsetting dropped glyphs that are still referenced: '
            + ', '.join(f'U+{cp.upper()}' for cp in dropped)
        )

    print(
        f'{label}: {len(codepoints)} glyphs — '
        f'{before / 1024:.1f} KB -> {after / 1024:.1f} KB '
        f'({100 - after / before * 100:.1f}% smaller)'
    )


def subset_tabler() -> None:
    mapping = dict(TABLER_RULE_RE.findall(_read(TABLER_CSS)))
    if not mapping:
        raise SystemExit(f'No icon rules found in {TABLER_CSS}')

    used = _scan_for_classes('ti')
    undefined = sorted(name for name in used if name not in mapping and name != 'ti-icon')
    if undefined:
        print(
            f'  warning: {len(undefined)} ti-* class(es) used but not defined in '
            f'{TABLER_CSS.name} — they will render blank: ' + ', '.join(undefined)
        )

    _run_subset(TABLER_FONT, sorted(mapping.values()), 'tabler')


def subset_bootstrap() -> None:
    mapping = dict(BOOTSTRAP_RULE_RE.findall(_read(BOOTSTRAP_VENDOR_CSS)))
    if not mapping:
        raise SystemExit(f'No icon rules found in {BOOTSTRAP_VENDOR_CSS}')

    used = sorted(name for name in _scan_for_classes('bi') if name in mapping)
    if not used:
        raise SystemExit('No bi-* classes found in the project')

    lines = [
        '/* Generated by scripts/subset_icon_fonts.py — do not edit by hand. */',
        '/* Bootstrap Icons v1.13.1, MIT. Only the icons this project renders. */',
        '@font-face {',
        '  font-display: swap;',
        '  font-family: "bootstrap-icons";',
        '  src: url("../vendors/bootstrap-icons/fonts/bootstrap-icons.woff2") format("woff2");',
        '}',
        '',
        '.bi::before,',
        '[class^="bi-"]::before,',
        '[class*=" bi-"]::before {',
        '  display: inline-block;',
        '  font-family: bootstrap-icons !important;',
        '  font-style: normal;',
        '  font-weight: normal !important;',
        '  font-variant: normal;',
        '  text-transform: none;',
        '  line-height: 1;',
        '  vertical-align: -.125em;',
        '  -webkit-font-smoothing: antialiased;',
        '  -moz-osx-font-smoothing: grayscale;',
        '}',
        '',
    ]
    lines += [f'.{name}::before {{ content: "\\{mapping[name]}"; }}' for name in used]
    BOOTSTRAP_SUBSET_CSS.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    vendor_kb = BOOTSTRAP_VENDOR_CSS.stat().st_size / 1024
    subset_kb = BOOTSTRAP_SUBSET_CSS.stat().st_size / 1024
    print(
        f'bootstrap css: {len(used)} of {len(mapping)} icons — '
        f'{vendor_kb:.1f} KB -> {subset_kb:.1f} KB'
    )

    _run_subset(BOOTSTRAP_FONT, sorted(mapping[name] for name in used), 'bootstrap')


def main() -> int:
    subset_tabler()
    subset_bootstrap()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
