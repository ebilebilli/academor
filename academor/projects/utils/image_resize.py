"""
Resize uploaded images in-place (WebP output) so browsers never fetch oversized pixels.

Used on save for small display fields (e.g. university logos shown at 80–192 px).
"""
from __future__ import annotations

import os
from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image, ImageOps


def resize_image_field(
    field_file,
    *,
    max_width: int,
    max_height: int,
    quality: int = 82,
    force: bool = False,
) -> bool:
    """
    Downscale *field_file* when larger than max_width × max_height.

    Replaces the in-memory upload with a WebP version before Django saves to storage.
    Returns True when the image was resized/re-encoded.
    """
    if field_file is None or not getattr(field_file, 'name', None):
        return False

    try:
        field_file.open('rb')
        img = Image.open(field_file)
        img.load()
    except Exception:
        return False
    finally:
        try:
            field_file.close()
        except Exception:
            pass

    width, height = img.size
    if not force and width <= max_width and height <= max_height:
        return False

    img = ImageOps.exif_transpose(img)
    if img.mode not in ('RGB', 'RGBA'):
        img = img.convert('RGBA' if 'A' in img.getbands() else 'RGB')

    if width > max_width or height > max_height:
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
