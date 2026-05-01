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
