"""
Append ?v=<mtime> to uploaded file URLs so browsers refetch after an in-place replace
(same path on disk, unchanged URL without a cache buster).
"""
from __future__ import annotations

import os


def media_url(file_field):
    """
    Return the field's public URL with a cache-busting query when mtime is available.
    Works with ImageField, FileField, VideoField on default storage / local disk.
    """
    if file_field is None:
        return None
    name = getattr(file_field, 'name', None) or ''
    if not name:
        return None
    try:
        base = file_field.url
    except ValueError:
        return None
    v = _upload_version(file_field)
    if not v:
        return base
    sep = '&' if '?' in base else '?'
    return f'{base}{sep}v={v}'


def image_spec_url(spec_field):
    """
    Public URL for an imagekit ImageSpecField, with cache busting from the source upload mtime.
    """
    if spec_field is None:
        return None
    source = getattr(spec_field, 'source', None)
    if source is None or not getattr(source, 'name', None):
        return None
    try:
        base = spec_field.url
    except (ValueError, FileNotFoundError, OSError):
        return None
    v = _upload_version(source)
    if not v:
        return base
    sep = '&' if '?' in base else '?'
    return f'{base}{sep}v={v}'


def build_srcset(*entries):
    """
    Build a srcset string from (url, width) pairs. Skips empty URLs.
    """
    parts = []
    for entry in entries:
        if not entry:
            continue
        if isinstance(entry, (tuple, list)) and len(entry) >= 2:
            url, width = entry[0], entry[1]
        else:
            continue
        if url and width:
            parts.append(f'{url} {width}w')
    return ', '.join(parts) if parts else None


def _upload_version(file_field) -> int:
    storage = file_field.storage
    name = file_field.name
    try:
        mtime = storage.get_modified_time(name)
        return int(mtime.timestamp())
    except Exception:
        pass
    try:
        return int(os.path.getmtime(file_field.path))
    except Exception:
        return 0
