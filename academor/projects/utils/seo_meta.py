"""SEO helpers: absolute OG URLs, keywords merge, JSON-LD structured data."""

from __future__ import annotations

import json
from datetime import date, datetime
from typing import Any

from django.templatetags.static import static
from django.urls import reverse

from projects.utils.canonical import _canonical_origin
from projects.utils.i18n import normalize_lang


def absolute_public_url(path_or_url: str | None) -> str | None:
    if not path_or_url:
        return None
    value = str(path_or_url).strip()
    if not value:
        return None
    if value.startswith('http://') or value.startswith('https://'):
        return value
    origin = _canonical_origin()
    if value.startswith('/'):
        return f'{origin}{value}'
    return f'{origin}/{value}'


def default_og_image_url() -> str:
    return absolute_public_url(static('assets/img/banner.webp')) or ''


def resolve_og_image_url(*, lcp_image_url: str | None = None, og_image_url: str | None = None) -> str:
    for candidate in (og_image_url, lcp_image_url):
        resolved = absolute_public_url(candidate)
        if resolved:
            return resolved
    return default_og_image_url()


def merge_keywords(*parts: str | None, max_len: int = 1200) -> str:
    seen: set[str] = set()
    tokens: list[str] = []
    for part in parts:
        if not part:
            continue
        for raw in str(part).split(','):
            token = raw.strip()
            if not token:
                continue
            key = token.lower()
            if key in seen:
                continue
            seen.add(key)
            tokens.append(token)
    merged = ', '.join(tokens)
    if len(merged) <= max_len:
        return merged
    return merged[: max_len - 1].rstrip(', ')


def tags_keywords(tags: list[dict] | None) -> str:
    if not tags:
        return ''
    return ', '.join(t['name'] for t in tags if t.get('name'))


def _iso_datetime(value: date | datetime | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return value.isoformat()


def organization_json_ld(*, canonical_url: str, lang: str = 'az') -> dict[str, Any]:
    lang = normalize_lang(lang)
    names = {
        'az': 'Academor — ingilis dili və xaricdə təhsil mərkəzi, Bakı',
        'en': 'Academor — English language school and study abroad support, Baku',
        'ru': 'Academor — языковой центр и поддержка обучения за рубежом, Баку',
    }
    return {
        '@context': 'https://schema.org',
        '@type': 'Organization',
        'name': 'Academor',
        'url': canonical_url.rstrip('/') + '/',
        'logo': default_og_image_url(),
        'description': names.get(lang, names['az']),
        'address': {
            '@type': 'PostalAddress',
            'addressLocality': 'Baku',
            'addressCountry': 'AZ',
        },
    }


def website_json_ld(*, canonical_url: str) -> dict[str, Any]:
    origin = canonical_url.rstrip('/')
    return {
        '@context': 'https://schema.org',
        '@type': 'WebSite',
        'name': 'Academor',
        'url': f'{origin}/',
        'potentialAction': {
            '@type': 'SearchAction',
            'target': f'{origin}/blog/?q={{search_term_string}}',
            'query-input': 'required name=search_term_string',
        },
    }


def blog_posting_json_ld(
    *,
    canonical_url: str,
    headline: str,
    description: str,
    image_url: str | None,
    date_published: date | datetime | None,
    keywords: str = '',
) -> dict[str, Any]:
    data: dict[str, Any] = {
        '@context': 'https://schema.org',
        '@type': 'BlogPosting',
        'mainEntityOfPage': {'@type': 'WebPage', '@id': canonical_url},
        'headline': headline,
        'description': description,
        'url': canonical_url,
        'author': {'@type': 'Organization', 'name': 'Academor'},
        'publisher': {
            '@type': 'Organization',
            'name': 'Academor',
            'logo': {'@type': 'ImageObject', 'url': default_og_image_url()},
        },
    }
    published = _iso_datetime(date_published)
    if published:
        data['datePublished'] = published
        data['dateModified'] = published
    if image_url:
        data['image'] = [image_url]
    if keywords:
        data['keywords'] = keywords
    return data


def course_json_ld(
    *,
    canonical_url: str,
    name: str,
    description: str,
    image_url: str | None,
    keywords: str = '',
) -> dict[str, Any]:
    data: dict[str, Any] = {
        '@context': 'https://schema.org',
        '@type': 'Course',
        'name': name,
        'description': description,
        'url': canonical_url,
        'provider': {'@type': 'Organization', 'name': 'Academor', 'url': _canonical_origin() + '/'},
    }
    if image_url:
        data['image'] = image_url
    if keywords:
        data['keywords'] = keywords
    return data


def collection_page_json_ld(
    *,
    canonical_url: str,
    name: str,
    description: str,
) -> dict[str, Any]:
    return {
        '@context': 'https://schema.org',
        '@type': 'CollectionPage',
        'name': name,
        'description': description,
        'url': canonical_url,
    }


def dumps_structured_data(*items: dict[str, Any] | None) -> str:
    payload = [item for item in items if item]
    if not payload:
        return ''
    if len(payload) == 1:
        return json.dumps(payload[0], ensure_ascii=False)
    return json.dumps(payload, ensure_ascii=False)


def build_detail_seo_context(
    *,
    page_title: str,
    page_description: str,
    lcp_image_url: str | None = None,
    og_type: str = 'website',
    page_keywords: str | None = None,
    published_date: date | datetime | None = None,
    structured_data_json: str = '',
) -> dict[str, Any]:
    og_image = resolve_og_image_url(lcp_image_url=lcp_image_url)
    ctx: dict[str, Any] = {
        'page_title': page_title,
        'page_description': page_description[:320],
        'og_image_url': og_image,
        'og_type': og_type,
        'structured_data_json': structured_data_json,
    }
    if page_keywords:
        ctx['page_keywords'] = page_keywords[:1200]
    if published_date:
        ctx['og_article_published_time'] = _iso_datetime(published_date)
    if lcp_image_url and not ctx.get('lcp_image_url'):
        ctx['lcp_image_url'] = lcp_image_url
    return ctx


def blog_detail_seo(
    *,
    canonical_url: str,
    post: dict,
    lang: str,
    default_keywords: str | None = None,
) -> dict[str, Any]:
    tag_kw = tags_keywords(post.get('tags'))
    keywords = merge_keywords(default_keywords, tag_kw)
    headline = post.get('name') or ''
    description = (post.get('description_plain') or headline)[:320]
    image = resolve_og_image_url(lcp_image_url=post.get('cover'))
    structured = dumps_structured_data(
        blog_posting_json_ld(
            canonical_url=canonical_url,
            headline=headline,
            description=description,
            image_url=image,
            date_published=post.get('date') or post.get('created_at'),
            keywords=keywords,
        ),
    )
    return build_detail_seo_context(
        page_title=f'{headline} | Academor',
        page_description=description,
        lcp_image_url=post.get('cover'),
        og_type='article',
        page_keywords=keywords,
        published_date=post.get('date') or post.get('created_at'),
        structured_data_json=structured,
    )


def course_detail_seo(
    *,
    canonical_url: str,
    course: dict,
    default_keywords: str | None = None,
) -> dict[str, Any]:
    tag_kw = tags_keywords(course.get('tags'))
    keywords = merge_keywords(default_keywords, tag_kw)
    name = course.get('name') or ''
    from projects.utils.seo_text import meta_plain_excerpt

    description = meta_plain_excerpt(course.get('description_html') or '')[:320]
    image = resolve_og_image_url(lcp_image_url=course.get('image'))
    structured = dumps_structured_data(
        course_json_ld(
            canonical_url=canonical_url,
            name=name,
            description=description or name,
            image_url=image,
            keywords=keywords,
        ),
    )
    return build_detail_seo_context(
        page_title=f'{name} | Academor',
        page_description=description or name,
        lcp_image_url=course.get('image'),
        og_type='website',
        page_keywords=keywords,
        structured_data_json=structured,
    )


def tag_archive_seo(
    *,
    canonical_url: str,
    tag_name: str,
    section_label: str,
    description: str,
    default_keywords: str | None = None,
) -> dict[str, Any]:
    keywords = merge_keywords(default_keywords, tag_name)
    structured = dumps_structured_data(
        collection_page_json_ld(
            canonical_url=canonical_url,
            name=f'{tag_name} — {section_label}',
            description=description,
        ),
    )
    return build_detail_seo_context(
        page_title=f'{tag_name} — {section_label} | Academor',
        page_description=description[:320],
        page_keywords=keywords,
        structured_data_json=structured,
    )
