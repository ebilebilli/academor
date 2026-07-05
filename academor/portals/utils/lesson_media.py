"""Lesson attachment helpers — PDF/image URLs and video embed detection."""

from urllib.parse import parse_qs, urlparse

from portals.utils.media_cache_bust import media_url


def extract_youtube_video_id(url):
    if not url:
        return None
    parsed = urlparse(url.strip())
    host = (parsed.netloc or '').lower().removeprefix('www.')
    if host == 'youtu.be':
        video_id = parsed.path.lstrip('/').split('/')[0]
        return video_id or None
    if 'youtube' in host:
        parts = [part for part in parsed.path.split('/') if part]
        if len(parts) >= 2 and parts[0] in ('embed', 'shorts', 'live'):
            return parts[1]
        query = parse_qs(parsed.query)
        values = query.get('v') or []
        return values[0] if values else None
    return None


def youtube_embed_url(url):
    video_id = extract_youtube_video_id(url)
    if not video_id:
        return None
    return f'https://www.youtube.com/embed/{video_id}'


def _video_link_label(url):
    url = (url or '').strip()
    if not url:
        return ''
    if extract_youtube_video_id(url):
        return 'YouTube'
    if len(url) > 56:
        return url[:53] + '...'
    return url


def _serialize_attachments(lesson):
    attachments = []
    related = getattr(lesson, 'attachments', None)
    if related is None:
        return attachments
    for attachment in related.all():
        if attachment.kind == 'video':
            url = (attachment.video_url or '').strip() or None
            if not url:
                continue
            attachments.append({
                'kind': attachment.kind,
                'url': url,
                'label': _video_link_label(url),
                'video_embed_url': youtube_embed_url(url),
                'video_is_youtube': bool(youtube_embed_url(url)),
                'youtube_thumbnail_url': (
                    f'https://img.youtube.com/vi/{extract_youtube_video_id(url)}/hqdefault.jpg'
                    if extract_youtube_video_id(url) else None
                ),
            })
            continue
        url = media_url(attachment.file) if attachment.file else None
        if not url:
            continue
        attachments.append({
            'kind': attachment.kind,
            'url': url,
            'label': attachment.file.name.rsplit('/', 1)[-1],
        })
    return attachments


def _file_basename(field_file):
    if not field_file or not getattr(field_file, 'name', None):
        return ''
    return field_file.name.rsplit('/', 1)[-1]


def build_lesson_edit_materials(lesson):
    """Existing PDF/image/video rows for the teacher lesson edit form."""
    if not lesson or not lesson.pk:
        return []

    items = []
    seen_urls = set()
    seen_file_labels = set()

    legacy_video = (lesson.video_url or '').strip()
    if legacy_video and legacy_video not in seen_urls:
        seen_urls.add(legacy_video)
        items.append({
            'id': 'legacy-video',
            'kind': 'video',
            'label': _video_link_label(legacy_video),
            'url': legacy_video,
        })

    related = getattr(lesson, 'attachments', None)
    if related is not None:
        for attachment in related.all():
            if attachment.kind == 'video':
                url = (attachment.video_url or '').strip()
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)
                items.append({
                    'id': f'attachment-{attachment.pk}',
                    'kind': attachment.kind,
                    'label': _video_link_label(url),
                    'url': url,
                    'attachment_pk': attachment.pk,
                })
                continue

            label = _file_basename(attachment.file)
            url = media_url(attachment.file) if attachment.file else None
            if not url or label in seen_file_labels:
                continue
            seen_urls.add(url)
            seen_file_labels.add(label)
            items.append({
                'id': f'attachment-{attachment.pk}',
                'kind': attachment.kind,
                'label': label,
                'url': url,
                'attachment_pk': attachment.pk,
            })

    if lesson.pdf_file:
        label = _file_basename(lesson.pdf_file)
        url = media_url(lesson.pdf_file)
        if url and label not in seen_file_labels:
            seen_urls.add(url)
            seen_file_labels.add(label)
            items.insert(0, {
                'id': 'legacy-pdf',
                'kind': 'pdf',
                'label': label,
                'url': url,
            })

    if lesson.image:
        label = _file_basename(lesson.image)
        url = media_url(lesson.image)
        if url and label not in seen_file_labels:
            seen_urls.add(url)
            seen_file_labels.add(label)
            items.insert(0, {
                'id': 'legacy-image',
                'kind': 'image',
                'label': label,
                'url': url,
            })

    return items


def _collect_unique_file_materials(lesson, kind, legacy_field):
    items = []
    seen_labels = set()
    related = getattr(lesson, 'attachments', None)
    if related is not None:
        for attachment in related.filter(kind=kind):
            if not attachment.file:
                continue
            label = _file_basename(attachment.file)
            url = media_url(attachment.file)
            if not url or label in seen_labels:
                continue
            seen_labels.add(label)
            items.append({'url': url, 'label': label})

    legacy = getattr(lesson, legacy_field)
    if legacy:
        label = _file_basename(legacy)
        url = media_url(legacy)
        if url and label not in seen_labels:
            seen_labels.add(label)
            items.insert(0, {'url': url, 'label': label})
    return items


def build_lesson_media(lesson):
    pdf_items = _collect_unique_file_materials(lesson, 'pdf', 'pdf_file')
    image_items = _collect_unique_file_materials(lesson, 'image', 'image')
    attachments = _serialize_attachments(lesson)
    extra_videos = [row for row in attachments if row['kind'] == 'video']

    pdf_url = pdf_items[0]['url'] if pdf_items else None
    extra_pdfs = pdf_items[1:]
    image_url = image_items[0]['url'] if image_items else None
    extra_images = image_items[1:]
    video_url = (lesson.video_url or '').strip() or None
    if video_url:
        primary_video_urls = {video_url}
        extra_videos = [
            row for row in extra_videos
            if row.get('url') not in primary_video_urls
        ]
    youtube_id = extract_youtube_video_id(video_url) if video_url else None
    video_embed_url_value = youtube_embed_url(video_url) if video_url else None
    has_pdf = bool(pdf_url) or bool(extra_pdfs)
    has_image = bool(image_url) or bool(extra_images)
    has_video = bool(video_url) or bool(extra_videos)
    return {
        'pdf_url': pdf_url,
        'image_url': image_url,
        'video_url': video_url,
        'video_embed_url': video_embed_url_value,
        'video_is_youtube': bool(video_embed_url_value),
        'youtube_video_id': youtube_id,
        'youtube_thumbnail_url': (
            f'https://img.youtube.com/vi/{youtube_id}/hqdefault.jpg' if youtube_id else None
        ),
        'has_pdf': has_pdf,
        'has_video': has_video,
        'has_image': has_image,
        'attachments': attachments,
        'extra_pdfs': extra_pdfs,
        'extra_images': extra_images,
        'extra_videos': extra_videos,
        'has_materials': bool(pdf_url or video_url or image_url or attachments),
    }
