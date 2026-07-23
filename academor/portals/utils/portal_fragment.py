"""Shrink full portal HTML responses for AJAX fragment navigation."""

from __future__ import annotations

import re

FRAGMENT_HEADER = 'X-Portal-Fragment'


def is_portal_fragment_request(request) -> bool:
    return (
        request.path.startswith('/portal/')
        and request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        and request.headers.get(FRAGMENT_HEADER) == '1'
    )


def _extract(pattern: str, html: str, flags: int = re.IGNORECASE | re.DOTALL):
    match = re.search(pattern, html, flags)
    return match.group(1).strip() if match else ''


def _extract_head_assets(html: str) -> str:
    """Keep page-specific stylesheets not part of the global portal shell."""
    base_assets = (
        'tokens.css',
        'bootstrap.min.css',
        'bootstrap-icons.css',
        'portal-tabler-icons.css',
        'inter-font.css',
        'style.css',
        'portal-redesign.css',
        'portal-shell.css',
    )
    links = []
    for match in re.finditer(
        r'<link\b[^>]*rel=["\']stylesheet["\'][^>]*>',
        html,
        re.IGNORECASE,
    ):
        tag = match.group(0)
        if '/portals/' not in tag:
            continue
        if any(asset in tag for asset in base_assets):
            continue
        links.append(tag)
    return '\n'.join(links)


def _extract_nav_snapshot(html: str) -> str:
    """Keep sidebar/mobile nav active states for AJAX link sync."""
    sidebar = _extract(
        r'(<aside\b[^>]*\bid=["\']adminSidebar["\'][^>]*>.*?</aside>)',
        html,
    )
    mobile = _extract(
        r'(<nav\b[^>]*\bclass=["\'][^"\']*mobile-bottom-nav[^"\']*["\'][^>]*>.*?</nav>)',
        html,
    )
    if not sidebar and not mobile:
        return ''

    parts = ['<div hidden id="portal-nav-snapshot" aria-hidden="true">']
    if sidebar:
        parts.append(sidebar)
    if mobile:
        parts.append(mobile)
    parts.append('</div>')
    return '\n'.join(parts)


def _extract_body_scripts(html: str) -> str:
    scripts = []
    for match in re.finditer(
        r'<script\b[^>]*src=["\']([^"\']+)["\'][^>]*>\s*</script>',
        html,
        re.IGNORECASE,
    ):
        src = match.group(1)
        if '/portals/' not in src:
            continue
        if any(
            core in src
            for core in (
                'bootstrap.bundle',
                '/main.js',
                'portal-nav-ajax.js',
                'portal-init.js',
                'portal-badges.js',
                'portal-lottie.js',
            )
        ):
            continue
        scripts.append(match.group(0))
    return '\n'.join(scripts)


def build_fragment_document(html: str) -> str:
    title = _extract(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
    lang = _extract(
        r'<html\b[^>]*\blang=["\']([^"\']+)["\']',
        html,
        re.IGNORECASE,
    ) or 'az'
    content = _extract(
        r'<main\b[^>]*\bdata-portal-content-root\b[^>]*>(.*?)</main>',
        html,
    )
    if not content:
        return html

    head_assets = _extract_head_assets(html)
    body_scripts = _extract_body_scripts(html)
    nav_snapshot = _extract_nav_snapshot(html)
    if nav_snapshot:
        content = f'{content}\n{nav_snapshot}'

    parts = [
        '<!DOCTYPE html>',
        '<html lang="' + lang + '">',
        '<head>',
        f'<title>{title}</title>' if title else '<title>Portal</title>',
    ]
    if head_assets:
        parts.append(head_assets)
    parts.extend([
        '</head>',
        '<body>',
        f'<main class="dashboard-content" data-portal-content-root>{content}</main>',
    ])
    if body_scripts:
        parts.append(body_scripts)
    parts.extend(['</body>', '</html>'])
    return '\n'.join(parts)
