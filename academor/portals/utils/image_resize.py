"""
Resize uploaded images in-place (WebP output) so browsers never fetch oversized pixels.

Used on save for small display fields (e.g. university logos shown at 80–192 px).
"""
from __future__ import annotations

import os
from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image, ImageOps


def _restore_upload_bytes(field_file, raw: bytes) -> None:
    """Put upload bytes back so Django can read them during model save."""
    try:
        field_file.seek(0)
    except Exception:
        field_file.save(
            os.path.basename(field_file.name),
            ContentFile(raw),
            save=False,
        )


def resize_image_field(
    field_file,
    *,
    max_width: int,
    max_height: int,
    quality: int = 82,
    force: bool = False,
) -> bool:
    """
    Downscale *field_file* when larger than max_width × max_height and encode as WebP.

    Replaces the in-memory upload with a WebP version before Django saves to storage.
    Returns True when the image was resized/re-encoded.
    """
    if field_file is None or not getattr(field_file, 'name', None):
        return False

    try:
        field_file.open('rb')
        raw = field_file.read()
    except Exception:
        return False

    try:
        img = Image.open(BytesIO(raw))
        img.load()
    except Exception:
        _restore_upload_bytes(field_file, raw)
        return False

    width, height = img.size
    needs_resize = width > max_width or height > max_height
    already_webp = os.path.splitext(field_file.name or '')[1].lower() == '.webp'
    if not force and not needs_resize and already_webp:
        _restore_upload_bytes(field_file, raw)
        return False

    img = ImageOps.exif_transpose(img)
    if img.mode not in ('RGB', 'RGBA'):
        img = img.convert('RGBA' if 'A' in img.getbands() else 'RGB')

    if needs_resize:
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

    buffer = BytesIO()
    save_kwargs = {'format': 'WEBP', 'quality': quality, 'method': 6}
    if img.mode == 'RGBA':
        save_kwargs['lossless'] = False
    img.save(buffer, **save_kwargs)
    buffer.seek(0)

    base_name = os.path.splitext(os.path.basename(field_file.name))[0]
    new_name = f'{base_name}.webp'
    field_file.save(new_name, ContentFile(buffer.read()), save=False)
    return True
