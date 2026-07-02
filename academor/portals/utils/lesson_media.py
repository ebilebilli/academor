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
    return f'https://www.youtube-nocookie.com/embed/{video_id}'


def build_lesson_media(lesson):
    pdf_url = media_url(lesson.pdf_file) if lesson.pdf_file else None
    image_url = media_url(lesson.image) if lesson.image else None
    video_url = (lesson.video_url or '').strip() or None
    video_embed_url = youtube_embed_url(video_url) if video_url else None
    return {
        'pdf_url': pdf_url,
        'image_url': image_url,
        'video_url': video_url,
        'video_embed_url': video_embed_url,
        'video_is_youtube': bool(video_embed_url),
        'has_pdf': bool(pdf_url),
        'has_video': bool(video_url),
        'has_image': bool(image_url),
        'has_materials': bool(pdf_url or video_url or image_url),
    }
