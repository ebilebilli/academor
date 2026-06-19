import re

from urllib.parse import urlencode

from django.db.models import Q, Prefetch
from django.urls import reverse
from django.utils import translation
from django.utils.translation import gettext as _, ngettext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.templatetags.static import static

from projects.models import *
from projects.utils.cache_utils import cached_query, cached_page_data
from projects.utils.i18n import normalize_lang, resolve_public_language
from projects.utils.media_cache_bust import media_url, image_spec_url, build_srcset
from projects.utils.seo_text import richtext_plain_text
from projects.service_category_icons import resolve_service_category_icon
from projects.study_abroad_advantage_icons import build_static_study_abroad_advantages_block
from projects.utils.pricing import (
    apply_percent_discount,
    fetch_active_sale_discounts_by_service_id,
    format_decimal_price,
    get_sale_percent_for_service,
)


def _session_set_lang(session, lang):
    """Write language to session only when it actually differs — prevents DB writes on every request."""
    changed = False
    if session.get('django_language') != lang:
        session['django_language'] = lang
        changed = True
    if session.get('language') != lang:
        session['language'] = lang
        changed = True
    if changed:
        session.modified = True


def get_language_from_request(request):
    """
    Active UI language for views and @cached_page_data keys.

    Uses the same resolution order as CustomLocaleMiddleware so Django cache
    entries always match the language shown in templates ({% trans %} / nav).

    URL ?lang= is ignored after the user picked a language in the navbar — otherwise
    redirect ?next= could immediately override the new choice.
    """
    if not request.session.get('language_user_chosen'):
        for key in ('lang', 'language'):
            lang = normalize_lang(request.GET.get(key, ''))
            if lang:
                _session_set_lang(request.session, lang)
                request.session['language_user_chosen'] = True
                request.session.modified = True
                translation.activate(lang)
                return lang

    lang = resolve_public_language(request)
    translation.activate(lang)
    return lang


def get_localized_field_name(field_base, lang):
    if lang == 'en':
        return f'{field_base}_en'
    elif lang == 'ru':
        return f'{field_base}_ru'
    else:
        return f'{field_base}_az'


def _localized_value(obj, base_field, lang, default_lang='az'):
    order = {
        'az': ('az', 'en', 'ru'),
        'en': ('en', 'az', 'ru'),
        'ru': ('ru', 'az', 'en'),
    }.get((lang or '').lower(), ('az', 'en', 'ru'))
    for code in order:
        val = getattr(obj, f'{base_field}_{code}', None)
        if val is not None and str(val).strip():
            return str(val).strip()
    fallback = getattr(obj, f'{base_field}_{default_lang}', None)
    return str(fallback).strip() if fallback else ''


def apply_university_study_abroad_localized_name(university_dict, lang):
    """
    Refresh `study_abroad['name']` from AbroadModel using name_az / name_en / name_ru.

    Called after cached `get_university_detail_view_context` so the label always matches
    the active UI language for this request (avoids stale country name if session lang
    changed without a cache miss).
    """
    if not university_dict:
        return
    block = university_dict.get('study_abroad')
    if not block or not block.get('slug'):
        return
    row = (
        AbroadModel.objects.filter(slug=block['slug'], is_active=True)
        .only('name_az', 'name_en', 'name_ru')
        .first()
    )
    if row:
        block['name'] = _localized_value(row, 'name', lang)


_category_media_prefetch = Prefetch(
    'medias',
    queryset=Media.objects.filter(image__isnull=False).exclude(image='').order_by('id'),
)


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_project_categories(lang='az', show_on_main_page=None, tag_slug=None):
    """Aktiv service kateqoriyaları (courses)."""
    qs = Service.objects.filter(is_active=True).order_by('order', 'id').prefetch_related(
        _category_media_prefetch,
        'price_packages',
        'tags',
    )
    if show_on_main_page is not None:
        qs = qs.filter(show_on_main_page=show_on_main_page)
    if tag_slug:
        qs = qs.filter(tags__slug=tag_slug, tags__is_active=True).distinct()
    return qs


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_active_project_category_by_slug(slug):
    """Tək aktiv kateqoriya (detal səhifə) — şəkillər id sırası ilə."""
    if not slug:
        return None
    return (
        Service.objects.filter(slug=slug, is_active=True)
        .prefetch_related(
            _category_media_prefetch,
            'instructors',
            'price_packages',
            'tags',
        )
        .first()
    )


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_about(lang='az'):
    about = About.objects.prefetch_related(
        Prefetch('medias', queryset=Media.objects.filter(
            Q(image__isnull=False) | Q(video__isnull=False)
        ))
    ).first()
    return about


def get_team_members(is_active=True):
    """Active team rows — fresh read (homepage/team pages; not cached)."""
    queryset = Team.objects.all()
    if is_active is not None and hasattr(Team, 'is_active'):
        queryset = queryset.filter(is_active=is_active)
    return list(queryset.order_by('order', 'id'))


def serialize_team_member(member, lang='az'):
    if member is None:
        return None
    social_urls = [
        getattr(member, 'facebook', None) or '',
        getattr(member, 'instagram', None) or '',
        getattr(member, 'linkedin', None) or '',
        getattr(member, 'youtube', None) or '',
        getattr(member, 'tiktok', None) or '',
    ]
    social_count = sum(1 for u in social_urls if u.strip())
    desc_html = _localized_value(member, 'description', lang)
    image_full = media_url(member.image) if member.image else None
    image_card = image_spec_url(member.image_card) if member.image else None
    image_detail = image_spec_url(member.image_detail) if member.image else None
    return {
        'id': member.id,
        'slug': member.slug,
        'image': image_detail or image_card or image_full,
        'image_card': image_card or image_full,
        'image_full': image_full,
        'image_srcset': build_srcset(
            (image_card, 400),
            (image_detail, 640),
        ) if member.image else None,
        'name': member.name,
        'role': member.role,
        'description': desc_html or None,
        'instagram': getattr(member, 'instagram', None),
        'facebook': getattr(member, 'facebook', None),
        'linkedin': getattr(member, 'linkedin', None),
        'tiktok': getattr(member, 'tiktok', None),
        'youtube': getattr(member, 'youtube', None),
        'descriptor': media_url(member.descriptor) if member.descriptor else None,
        'social_count': social_count,
    }


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_reviews(is_active=True, limit=30):
    queryset = Review.objects.all()
    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)
    return list(queryset.order_by('-created_at')[:limit])


def serialize_review(review):
    if review is None:
        return None
    return {
        'id': review.id,
        'name': review.name,
        'message': review.message,
        'rating': review.rating,
        'created_at': review.created_at,
    }


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_blog_posts(is_active=True, on_main_page=None, tag_slug=None, tag_slugs=None):
    queryset = BlogPost.objects.prefetch_related('images', 'tags')
    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)
    if on_main_page is not None:
        queryset = queryset.filter(on_main_page=on_main_page)
    slugs = list(tag_slugs or [])
    if tag_slug:
        slugs = [tag_slug]
    if slugs:
        queryset = queryset.filter(
            tags__slug__in=slugs,
            tags__is_active=True,
        ).distinct()
    return list(queryset.order_by('-on_top', '-date', '-id'))


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_blog_post_by_slug(slug, is_active=True):
    queryset = BlogPost.objects.prefetch_related('images', 'tags').filter(slug=slug)
    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)
    return queryset.first()


def _active_tags_for_instance(instance):
    return sorted(
        (t for t in instance.tags.all() if t.is_active),
        key=lambda t: (t.order, t.name_az or ''),
    )


def serialize_content_tag(tag, lang='az'):
    """Public blog tag chip/link (includes URL)."""
    if tag is None:
        return None
    return {
        'id': tag.id,
        'slug': tag.slug,
        'name': _localized_value(tag, 'name', lang),
        'url': reverse('projects:blog-tag-page', kwargs={'slug': tag.slug}),
    }


def _serialize_service_tags_for_seo(category, lang='az'):
    """Service/course tags for meta keywords only — no public URL."""
    return [
        {
            'id': t.id,
            'slug': t.slug,
            'name': _localized_value(t, 'name', lang),
        }
        for t in _active_tags_for_instance(category)
    ]


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_content_tag_by_slug(slug, is_active=True):
    if not slug:
        return None
    qs = ContentTag.objects.filter(slug=slug)
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    return qs.first()


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_active_content_tags():
    return list(
        ContentTag.objects.filter(is_active=True, blog_posts__is_active=True)
        .distinct()
        .order_by('order', 'name_az', 'id')
    )


def serialize_blog_post(post, lang='az'):
    if post is None:
        return None
    image_rows = [img for img in post.images.all() if img.image]
    images = [media_url(img.image) for img in image_rows]
    video = media_url(post.video) if post.video else None
    if post.cover:
        cover_full = media_url(post.cover)
        cover_large = image_spec_url(post.cover_display) or cover_full
        cover_card = image_spec_url(post.cover_card) or cover_large
        cover_srcset = build_srcset((cover_card, 400), (cover_large, 800))
    else:
        first_img = image_rows[0] if image_rows else None
        cover_card = image_spec_url(first_img.image_card) if first_img else None
        cover_large = image_spec_url(first_img.image_large) if first_img else None
        cover_full = images[0] if images else None
        cover_srcset = build_srcset(
            (cover_card, 400),
            (cover_large, 800),
        ) if first_img else None
    desc_html = _localized_value(post, 'description', lang) or None
    desc_plain = richtext_plain_text(desc_html) if desc_html else ''
    uses_gallery_cover = not post.cover and not video and bool(images)
    gallery_images = images[1:] if uses_gallery_cover else images
    return {
        'id': post.id,
        'slug': post.slug,
        'name': _localized_value(post, 'name', lang),
        'description': desc_html,
        'description_plain': desc_plain or None,
        'date': post.date,
        'created_at': post.created_at,
        'on_top': post.on_top,
        'on_main_page': post.on_main_page,
        'video': video,
        'cover': cover_large or cover_card or cover_full,
        'cover_full': cover_full,
        'cover_srcset': cover_srcset,
        'images': images,
        'gallery_images': gallery_images,
        'tags': [
            serialize_content_tag(t, lang)
            for t in _active_tags_for_instance(post)
        ],
    }


def _fresh_abroad_advantages_context(lang):
    """Study-abroad icon row — cached query, merged after page blob (home + /abroad/)."""
    return {
        'abroad_advantages': get_study_abroad_advantages_block(lang=lang),
    }


def _sale_promo_image(sale):
    prefetched = getattr(sale, '_prefetched_objects_cache', {}).get('medias')
    if prefetched is not None:
        medias = list(prefetched)
    else:
        medias = list(sale.medias.exclude(image='').order_by('id'))
    for media in medias:
        if media.image:
            return media_url(media.image)
    return None


_SALE_END_DATE_MONTHS = {
    'az': (
        '', 'Yanvar', 'Fevral', 'Mart', 'Aprel', 'May', 'İyun',
        'İyul', 'Avqust', 'Sentyabr', 'Oktyabr', 'Noyabr', 'Dekabr',
    ),
    'ru': (
        '', 'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
        'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря',
    ),
}

_SALE_PERCENT_LABELS = {
    'az': '% endirim',
    'en': '% discount',
    'ru': '% скидка',
}


def _sale_percent_label(lang='az') -> str:
    return _SALE_PERCENT_LABELS.get(normalize_lang(lang), _SALE_PERCENT_LABELS['en'])


def _sale_discount_badge_aria(percent, lang='az') -> str:
    lang = normalize_lang(lang)
    if lang == 'az':
        return f'{percent} faiz endirim'
    if lang == 'ru':
        return f'Скидка {percent}%'
    return f'{percent} percent discount'


def _format_sale_end_date(end_date, lang='az'):
    if not end_date:
        return None
    lang = normalize_lang(lang)
    if lang in _SALE_END_DATE_MONTHS:
        months = _SALE_END_DATE_MONTHS[lang]
        return f'{end_date.day} {months[end_date.month]} {end_date.year}'
    return end_date.strftime('%B %d, %Y')


def serialize_sale(sale, lang='az'):
    """Homepage promotion banner payload — cache: ``invalidate_sale_cache()`` via Sale signals."""
    services = [
        service for service in sale.services.all()
        if service.is_active
    ]
    desc_html = _localized_value(sale, 'description', lang) or None
    desc_plain = richtext_plain_text(desc_html) if desc_html else ''
    name = _localized_value(sale, 'name', lang)
    has_discount = sale.percent is not None
    return {
        'id': sale.id,
        'name': name,
        'description': desc_html,
        'description_plain': desc_plain or None,
        'percent': sale.percent,
        'has_discount': has_discount,
        'percent_label': _sale_percent_label(lang) if has_discount else None,
        'discount_badge_aria': _sale_discount_badge_aria(sale.percent, lang) if has_discount else None,
        'end_date': sale.end_date.isoformat() if sale.end_date else None,
        'end_date_display': _format_sale_end_date(sale.end_date, lang),
        'apply_to_service_prices': sale.apply_to_service_prices,
        'image': _sale_promo_image(sale),
        'image_alt': name or _('Special offer'),
        'service_count': len(services),
        'services': [
            {
                'slug': service.slug,
                'name': _service_category_display_name(service, lang),
            }
            for service in services
        ],
    }


def _fetch_serialized_active_sales(lang='az'):
    """Active homepage sale banners — fresh DB read (is_active, show_on_homepage, not expired)."""
    from django.utils import timezone

    today = timezone.localdate()
    sales = (
        Sale.objects.filter(is_active=True, show_on_homepage=True)
        .filter(Q(end_date__isnull=True) | Q(end_date__gte=today))
        .prefetch_related(
            Prefetch(
                'services',
                queryset=Service.objects.filter(is_active=True).order_by('order', 'id'),
            ),
            Prefetch(
                'medias',
                queryset=Media.objects.exclude(image='').order_by('id'),
            ),
        )
        .order_by('-created_at')
    )
    return [serialize_sale(sale, lang=lang) for sale in sales]


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_serialized_active_sales(lang='az'):
    """Cached sale banners — bump via ``invalidate_sale_cache()``."""
    return _fetch_serialized_active_sales(lang)


def _fresh_home_sales_context(lang='az'):
    """Homepage sales — bypass query cache so admin edits show on next reload."""
    return {'sales': _fetch_serialized_active_sales(lang)}


def _fresh_home_team_context(lang='az'):
    """Homepage team cards — fresh read, not inside the cached page blob."""
    return {
        'team': [serialize_team_member(m, lang=lang) for m in get_team_members()],
    }


def _serialized_categories_with_fresh_sales(lang, show_on_main_page=None):
    """Service cards with current sale prices — always a fresh discount lookup."""
    categories = get_project_categories(lang, show_on_main_page=show_on_main_page)
    discounts_map = fetch_active_sale_discounts_by_service_id()
    return [
        serialize_project_category(category, lang, discounts_map=discounts_map)
        for category in categories
    ]


def serialize_homepage_price_package(package, lang='az', discounts_map=None):
    """Featured price card for the homepage carousel (may span multiple courses)."""
    if discounts_map is None:
        discounts_map = fetch_active_sale_discounts_by_service_id()
    course = package.course
    sale_percent = get_sale_percent_for_service(course.id, discounts_map)
    data = serialize_price_package(package, lang, sale_percent=sale_percent)
    detail_url = reverse('projects:course-detail', kwargs={'slug': course.slug})
    data['course'] = {
        'id': course.id,
        'slug': course.slug,
        'name': _service_category_display_name(course, lang),
        'icon': resolve_service_category_icon(
            getattr(course, 'card_icon', '') or '',
            course.slug or '',
        ),
        'detail_url': detail_url,
    }
    data['buy_url'] = (
        detail_url
        + '?'
        + urlencode({'package': package.id, 'pay': '1'})
        + '#course-pay'
    )
    data['payment_start_url'] = reverse(
        'payment_start_course',
        kwargs={'slug': course.slug},
    )
    return data


def _fetch_serialized_homepage_price_packages(lang='az'):
    packages = (
        CoursePricePackage.objects.filter(
            is_active=True,
            show_on_homepage=True,
            price__gt=0,
            course__is_active=True,
        )
        .select_related('course')
        .order_by('order', 'id')
    )
    discounts_map = fetch_active_sale_discounts_by_service_id()
    return [
        serialize_homepage_price_package(package, lang, discounts_map=discounts_map)
        for package in packages
    ]


def _fresh_home_featured_prices_context(lang='az'):
    """Homepage featured price carousel — fresh read, not inside the cached page blob."""
    return {
        'home_featured_prices': _fetch_serialized_homepage_price_packages(lang),
    }


def _fresh_home_categories_context(lang='az'):
    """Homepage service cards — override stale categories from the page cache blob."""
    return {
        'categories': _serialized_categories_with_fresh_sales(
            lang,
            show_on_main_page=True,
        ),
    }


def _merge_fresh_sale_categories(ctx, lang, show_on_main_page=None):
    """Replace serialized categories in a page context with fresh sale pricing."""
    ctx['categories'] = _serialized_categories_with_fresh_sales(
        lang,
        show_on_main_page=show_on_main_page,
    )
    slug = (ctx.get('filters') or {}).get('slug')
    if slug:
        for cat in ctx['categories']:
            if cat.get('slug') == slug:
                ctx['selected_category'] = cat
                break
    return ctx


def get_home_sales_context(lang='az'):
    """Homepage sale section — cached per language."""
    return {'sales': get_serialized_active_sales(lang)}


def _fresh_home_blog_context(lang):
    """Home hero + blog section bypass the cached page blob so edits show on the next reload."""
    posts = list(
        BlogPost.objects.filter(is_active=True, on_main_page=True)
        .prefetch_related('images')
        .order_by('-on_top', '-date', '-id')
    )
    return {
        'blog_featured': [
            serialize_blog_post(p, lang=lang) for p in posts if p.on_top
        ][:2],
        'blog_posts': [
            serialize_blog_post(p, lang=lang) for p in posts if not p.on_top
        ],
    }


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_home_about_context(lang='az'):
    """
    Homepage About block (intro, video, cover) — cached per language, not inside the page blob.

    Bumps with global cache_version when About, AboutWhyItem, or related Media rows change.
    """
    about = get_about(lang)
    serialized_about = serialize_about(about, lang) if about else None
    if serialized_about and not serialized_about.get('show_on_homepage'):
        serialized_about = None
    return {'about': serialized_about}


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def _cached_blog_list_blob(lang, tags_key=None):
    """
    Blog list + tag-filtered list shared blob.

    Cached per (lang, tags_key) where tags_key is comma-separated sorted slugs.
    """
    tags_key = (tags_key or '').strip()
    tag_slugs = [s for s in tags_key.split(',') if s] if tags_key else []
    all_posts = get_blog_posts(is_active=True, tag_slugs=tag_slugs or None)
    featured = [p for p in all_posts if p.on_top][:2]
    regular = [p for p in all_posts if not p.on_top]
    serialized_featured = [serialize_blog_post(p, lang=lang) for p in featured]
    serialized_posts = [serialize_blog_post(p, lang=lang) for p in regular]
    lcp_image_url = None
    if serialized_featured and serialized_featured[0].get('cover'):
        lcp_image_url = serialized_featured[0]['cover']
    elif serialized_posts and serialized_posts[0].get('cover'):
        lcp_image_url = serialized_posts[0]['cover']
    active_tags = []
    for slug in tag_slugs:
        tag_obj = get_content_tag_by_slug(slug)
        if tag_obj:
            active_tags.append(serialize_content_tag(tag_obj, lang))
    active_tag = active_tags[0] if len(active_tags) == 1 else None
    return {
        'featured_posts': serialized_featured,
        'posts': serialized_posts,
        'categories': [serialize_project_category(c, lang) for c in get_project_categories(lang)],
        'language': lang,
        'background_image': get_background_image('about'),
        'lcp_image_url': lcp_image_url,
        'active_tags': active_tags,
        'active_tag_slugs': tag_slugs,
        'active_tag': active_tag,
        'filter_tag_slug': tag_slugs[0] if len(tag_slugs) == 1 else None,
        'filter_tag_slugs': tag_slugs,
        'content_tags': [
            serialize_content_tag(t, lang)
            for t in get_active_content_tags()
        ],
    }


def _normalize_blog_tag_slugs(raw_slugs):
    seen = set()
    result = []
    for raw in raw_slugs:
        slug = (raw or '').strip()
        if slug and slug not in seen:
            seen.add(slug)
            result.append(slug)
    return result


def parse_blog_tag_slugs_from_request(request):
    return _normalize_blog_tag_slugs(request.GET.getlist('tag'))


def resolve_blog_filter_tag_slugs(slugs):
    valid = []
    for slug in slugs:
        if get_content_tag_by_slug(slug):
            valid.append(slug)
    return sorted(valid)


def blog_list_tags_cache_key(slugs):
    resolved = resolve_blog_filter_tag_slugs(slugs)
    return ','.join(resolved) if resolved else None


def get_blog_page_data(request, lang):
    """Full context for `/blog/` (blog.html)."""
    slugs = resolve_blog_filter_tag_slugs(parse_blog_tag_slugs_from_request(request))
    return _cached_blog_list_blob(lang, blog_list_tags_cache_key(slugs))


def get_blog_tag_page_data(request, lang, slug):
    """Full context for `/blog/tag/<slug>/`."""
    slug = (slug or '').strip()
    if not slug or not get_content_tag_by_slug(slug):
        return None
    return _cached_blog_list_blob(lang, slug)


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_blog_detail_view_context(lang, slug):
    post = get_blog_post_by_slug(slug, is_active=True)
    if not post:
        return None
    all_posts = get_blog_posts(is_active=True)
    other_posts = [p for p in all_posts if p.slug != slug][:6]
    categories = get_project_categories(lang)
    serialized_post = serialize_blog_post(post, lang=lang)
    return {
        'post': serialized_post,
        'other_posts': [serialize_blog_post(p, lang=lang) for p in other_posts],
        'categories': [serialize_project_category(c, lang) for c in categories],
        'language': lang,
        'background_image': get_background_image('about'),
        'lcp_image_url': serialized_post.get('cover') if serialized_post else None,
    }


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_tests(is_active=True):
    queryset = Test.objects.all()
    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)
    return list(queryset.order_by('-created_at'))


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_test_by_id(test_id: int, is_active=True):
    try:
        qs = Test.objects.prefetch_related(
            Prefetch(
                'questions',
                queryset=Question.objects.prefetch_related('options').all(),
            )
        )
        if is_active is not None:
            qs = qs.filter(is_active=is_active)
        return qs.get(id=test_id)
    except Test.DoesNotExist:
        return None


def _norm_ui_lang(lang):
    if not lang:
        return getattr(settings, 'LANGUAGE_CODE', 'az')
    return str(lang).lower().split('-')[0][:2]


def localized_test_title(test, lang='en'):
    if test is None:
        return ''
    lang = _norm_ui_lang(lang)
    order = {
        'az': ('title_az', 'title_en', 'title_ru'),
        'en': ('title_en', 'title_az', 'title_ru'),
        'ru': ('title_ru', 'title_en', 'title_az'),
    }.get(lang, ('title_en', 'title_az', 'title_ru'))
    for attr in order:
        val = (getattr(test, attr, None) or '').strip()
        if val:
            return val
    return ''


def localized_test_description(test, lang='en'):
    if test is None:
        return ''
    lang = _norm_ui_lang(lang)
    order = {
        'az': ('description_az', 'description_en', 'description_ru'),
        'en': ('description_en', 'description_az', 'description_ru'),
        'ru': ('description_ru', 'description_en', 'description_az'),
    }.get(lang, ('description_en', 'description_az', 'description_ru'))
    for attr in order:
        val = getattr(test, attr, None)
        if val is not None and str(val).strip():
            return str(val).strip()
    return ''


def serialize_test_for_taking(test, lang='en'):
    if test is None:
        return None
    return {
        'id': test.id,
        'title': localized_test_title(test, lang),
        'description': localized_test_description(test, lang),
        'questions': [
            {
                'id': q.id,
                'text': q.text,
                'options': [
                    {'id': o.id, 'text': o.text}
                    for o in q.options.all()
                ],
            }
            for q in test.questions.all()
        ],
    }


def serialize_test_for_list(test, lang='en'):
    """Tests listing card: localized strings + question count."""
    if test is None:
        return None
    return {
        'id': test.id,
        'title': localized_test_title(test, lang),
        'description': localized_test_description(test, lang),
        'question_count': test.questions.count(),
    }


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_contact(lang='az'):
    return Contact.objects.first()


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_background_image(page_type):
    image_map = {
        'home': 'is_home_page_background_image',
        'about': 'is_about_page_background_image',
        'contact': 'is_contact_page_background_image',
        'partner': 'is_partner_background_image',
        'project': 'is_project_page_background_image',
        'courses': 'is_courses_page_background_image',
        'tests': 'is_tests_page_background_image',
        'service': 'is_service_page_background_image',
        'footer': 'is_footer_background_image',
        'abroad': 'is_abroad_page_background_image',
    }

    if page_type not in image_map:
        return None

    media = Media.objects.filter(**{image_map[page_type]: True}).first()
    if media and media.image:
        return media_url(media.image)
    return None


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_home_background_images(limit=6):
    """Ana səhifə hero karuseli üçün background image-ləri qaytarır (maksimum 6 ədəd)"""
    media_list = Media.objects.filter(
        is_home_page_background_image=True,
        image__isnull=False
    ).order_by('-created_at')[:limit]
    
    return [media_url(m.image) for m in media_list if m.image]


def _serialize_tagline(tagline):
    if not tagline:
        return None
    text = (tagline.text or '').strip()
    if not text:
        return None
    return {'text': text}


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_page_tagline(page_key, lang='az'):
    """Per-page banner text (AZ only) — invalidate via Tagline post_save/post_delete signals."""
    del lang  # reserved for future i18n
    if not page_key:
        return None
    tagline = Tagline.objects.filter(page=page_key, is_active=True).first()
    return _serialize_tagline(tagline)


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_study_abroad_section(lang='az'):
    obj = StudyAbroadSection.objects.first()
    if not obj:
        return None
    return _localized_value(obj, 'text', lang)


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_study_abroad_advantages_block(lang='az'):
    return build_static_study_abroad_advantages_block(lang=lang)


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_abroad_items(is_active=True, show_on_main_page=None):
    qs = AbroadModel.objects.only(
        'id',
        'slug',
        'name_az',
        'name_en',
        'name_ru',
        'description_az',
        'description_en',
        'description_ru',
        'img',
        'detail_page_img',
        'is_active',
        'show_on_main_page',
        'created_at',
    )
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    if show_on_main_page is not None:
        qs = qs.filter(show_on_main_page=show_on_main_page)
    return list(qs.order_by('id'))


def serialize_abroad_item(item, lang='az'):
    if item is None:
        return None
    img_full = media_url(item.img) if item.img else None
    img_thumb = image_spec_url(item.img_thumb) if item.img else None
    detail_full = media_url(item.detail_page_img) if item.detail_page_img else None
    detail_hero = image_spec_url(item.detail_page_img_hero) if item.detail_page_img else None
    return {
        'id': item.id,
        'slug': item.slug,
        'name': _localized_value(item, 'name', lang),
        'description': _localized_value(item, 'description', lang),
        'img': img_thumb or img_full,
        'img_full': img_full,
        'detail_page_img': detail_hero or detail_full or img_thumb or img_full,
        'detail_page_img_full': detail_full or img_full,
        'is_active': item.is_active,
        'created_at': item.created_at,
    }


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_universities(is_active=True, study_abroad_show_on_main_page=None):
    qs = University.objects.only(
        'id',
        'flag',
        'is_active',
        'name',
        'slug',
        'study_abroad_id',
    )
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    if study_abroad_show_on_main_page is True:
        qs = qs.filter(
            study_abroad_id__isnull=False,
            study_abroad__show_on_main_page=True,
            study_abroad__is_active=True,
        )
    elif study_abroad_show_on_main_page is False:
        qs = qs.filter(
            Q(study_abroad_id__isnull=True)
            | Q(study_abroad__show_on_main_page=False)
        )
    return list(qs.order_by('id'))


def serialize_university(item):
    if item is None:
        return None
    row = {
        'id': item.id,
        'flag': media_url(item.flag) if item.flag else None,
    }
    name = (getattr(item, 'name', None) or '').strip()
    if name:
        row['name'] = name
    slug = getattr(item, 'slug', None) or ''
    if slug:
        row['slug'] = slug
    return row


def _serialize_university_for_abroad_country_page(u):
    """Template dict for partner cards on a study-abroad country detail page."""
    name = (u.name or '').strip() or None
    return {
        'id': u.id,
        'name': name,
        'flag': media_url(u.flag) if u.flag else None,
        'slug': (u.slug or '').strip(),
    }


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_serialized_abroad_items(lang='az', is_active=True, show_on_main_page=None):
    return [
        serialize_abroad_item(i, lang=lang)
        for i in get_abroad_items(is_active=is_active, show_on_main_page=show_on_main_page)
    ]


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_nav_abroad_items(lang='az', is_active=True):
    return [serialize_abroad_item(i, lang=lang) for i in get_abroad_items(is_active=is_active)]


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_nav_abroad_items_with_universities(lang='az', is_active=True):
    """Header dropdown: hər ölkə üçün aktiv universitet siyahısı (id, slug, name)."""
    items = get_abroad_items(is_active=is_active)
    if not items:
        return []
    item_ids = [i.id for i in items]
    uni_qs = (
        University.objects.filter(
            study_abroad_id__in=item_ids,
            is_active=True,
        )
        .exclude(slug__isnull=True)
        .exclude(slug='')
        .only('id', 'name', 'slug', 'study_abroad_id')
        .order_by('id')
    )
    unis_by_country = {}
    for u in uni_qs:
        name = (u.name or '').strip()
        if not name:
            continue
        unis_by_country.setdefault(u.study_abroad_id, []).append({
            'id': u.id,
            'slug': u.slug,
            'name': name,
        })
    result = []
    for i in items:
        data = serialize_abroad_item(i, lang=lang)
        if not data:
            continue
        data['universities'] = unis_by_country.get(i.id, [])
        result.append(data)
    return result


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_serialized_universities(is_active=True, study_abroad_show_on_main_page=None):
    return [
        serialize_university(u)
        for u in get_universities(
            is_active=is_active,
            study_abroad_show_on_main_page=study_abroad_show_on_main_page,
        )
    ]


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_site_faq_entries(is_active=True):
    qs = SiteFaqEntry.objects.only(
        'id',
        'question_az',
        'question_en',
        'question_ru',
        'answer_az',
        'answer_en',
        'answer_ru',
        'order',
        'is_active',
    )
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    return list(qs.order_by('order', 'id'))


def serialize_site_faq_entry(entry, lang='az'):
    if entry is None:
        return None
    return {
        'id': entry.id,
        'question': _localized_value(entry, 'question', lang),
        'answer': _localized_value(entry, 'answer', lang),
    }


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_serialized_site_faq_entries(lang='az', is_active=True):
    result = []
    for entry in get_site_faq_entries(is_active=is_active):
        row = serialize_site_faq_entry(entry, lang=lang)
        if row and row['question'].strip() and row['answer'].strip():
            result.append(row)
    return result


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def _price_package_display_name(package, lang='az'):
    name_field = get_localized_field_name('name', lang)
    for candidate in (
        getattr(package, name_field, None),
        package.name_az,
        package.name_en,
        package.name_ru,
    ):
        if candidate is not None and str(candidate).strip():
            return str(candidate).strip()
    return ''


def price_package_display_name(package, lang='az'):
    return _price_package_display_name(package, lang)


def _format_lesson_minutes_display(minutes, lang='az'):
    if not minutes:
        return ''
    with translation.override(lang):
        return ngettext(
            '%(counter)s minute',
            '%(counter)s minutes',
            minutes,
        ) % {'counter': minutes}


def _format_months_display(months, lang='az'):
    if not months:
        return ''
    with translation.override(lang):
        return ngettext(
            '%(counter)s month',
            '%(counter)s months',
            months,
        ) % {'counter': months}


def format_months_display(months, lang='az'):
    return _format_months_display(months, lang)


def serialize_price_package(package, lang='az', sale_percent=None):
    original_price = package.price
    price = original_price
    has_discount = bool(sale_percent)
    if has_discount:
        price = apply_percent_discount(original_price, sale_percent)

    return {
        'id': package.id,
        'name': _price_package_display_name(package, lang),
        'months': package.months,
        'months_display': _format_months_display(package.months, lang),
        'lesson_count': package.lesson_count,
        'lesson_minutes': package.lesson_minutes,
        'lesson_minutes_display': _format_lesson_minutes_display(
            package.lesson_minutes,
            lang,
        ),
        'price': price,
        'price_display': format_decimal_price(price),
        'original_price': original_price if has_discount else None,
        'original_price_display': format_decimal_price(original_price) if has_discount else None,
        'discount_percent': sale_percent if has_discount else None,
        'has_discount': has_discount,
        'is_premium': bool(package.is_premium),
        'package_tab': package.package_tab,
    }


def _service_category_display_name(category, lang='az'):
    """Localized name with fallbacks — DB allows NULL per language field."""
    name_field = get_localized_field_name('name', lang)
    for candidate in (
        getattr(category, name_field, None),
        category.name_az,
        category.name_en,
        category.name_ru,
    ):
        if candidate is not None and str(candidate).strip():
            return str(candidate).strip()
    slug = getattr(category, 'slug', None) or ''
    slug = slug.strip()
    if slug:
        return slug.replace('-', ' ').title()
    return ''


def serialize_project_category(category, lang='az', discounts_map=None):
    if discounts_map is None:
        discounts_map = fetch_active_sale_discounts_by_service_id()

    desc_field = get_localized_field_name('description', lang)
    first_image = None
    for media in category.medias.all():
        if media.image:
            first_image = media_url(media.image)
            break

    raw_desc = getattr(category, desc_field, None)
    if raw_desc is None:
        raw_desc = category.description_az or ''

    active_packages = [
        p for p in category.price_packages.all()
        if p.is_active and p.price and p.price > 0
    ]
    min_price = None
    if active_packages:
        min_price = min(p.price for p in active_packages)
    elif category.price and category.price > 0:
        min_price = category.price

    sale_percent = get_sale_percent_for_service(category.id, discounts_map)
    original_min_price = min_price
    if min_price is not None and sale_percent:
        min_price = apply_percent_discount(min_price, sale_percent)

    return {
        'id': category.id,
        'slug': category.slug,
        'name': _service_category_display_name(category, lang),
        'icon': resolve_service_category_icon(
            getattr(category, 'card_icon', '') or '',
            category.slug or '',
        ),
        'image': first_image,
        'description_html': raw_desc or '',
        'price': int(min_price) if min_price is not None and min_price == int(min_price) else min_price,
        'original_price': (
            int(original_min_price)
            if sale_percent and original_min_price is not None and original_min_price == int(original_min_price)
            else original_min_price if sale_percent else None
        ),
        'discount_percent': sale_percent,
        'on_sale': bool(sale_percent),
        'sale_percent_label': _sale_percent_label(lang) if sale_percent else None,
        'sale_badge_aria': _sale_discount_badge_aria(sale_percent, lang) if sale_percent else None,
        'has_discount': bool(sale_percent and min_price is not None),
        'has_payment': bool(active_packages),
        'tags': _serialize_service_tags_for_seo(category, lang),
    }


def serialize_project_category_detail(category, lang='az'):
    """Kurs detalı: bütün şəkil URL-ləri (siyahı səhifələrdə yalnız `image` istifadə olunur)."""
    if category is None:
        return None
    data = serialize_project_category(category, lang)
    data['images'] = [
        media_url(media.image)
        for media in category.medias.all()
        if media.image
    ]

    dur_field = get_localized_field_name('duration_months', lang)
    les_field = get_localized_field_name('lesson_count', lang)
    data['duration_months'] = (
        getattr(category, dur_field, None)
        or getattr(category, 'duration_months_az', None)
        or getattr(category, 'duration_months_en', None)
        or getattr(category, 'duration_months_ru', None)
        or ''
    )
    data['lesson_hours'] = (
        getattr(category, les_field, None)
        or getattr(category, 'lesson_count_az', None)
        or getattr(category, 'lesson_count_en', None)
        or getattr(category, 'lesson_count_ru', None)
        or ''
    )
    data['has_certificate'] = category.has_certificate
    data['is_online'] = category.is_online
    data['is_offline'] = category.is_offline
    discounts_map = fetch_active_sale_discounts_by_service_id()
    sale_percent = get_sale_percent_for_service(category.id, discounts_map)
    packages = [
        serialize_price_package(p, lang, sale_percent=sale_percent)
        for p in category.price_packages.filter(is_active=True, price__gt=0).order_by('order', 'id')
    ]
    data['price_packages'] = packages
    data['has_payment'] = bool(packages)
    if packages:
        min_pkg_price = min(p['price'] for p in packages)
        data['price'] = (
            int(min_pkg_price)
            if min_pkg_price == int(min_pkg_price)
            else min_pkg_price
        )
    else:
        data['price'] = category.price
    data['instructors'] = [
        serialize_team_member(member, lang)
        for member in category.instructors.all().order_by('order', 'id')
    ]

    return data


def _about_plain_excerpt(html, max_chars=300):
    """Plain teaser from CKEditor HTML (decoded entities, no double-escaping in templates)."""
    text = richtext_plain_text(html)
    if not text:
        return ''
    if len(text) <= max_chars:
        return text
    cut = text[:max_chars].rsplit(' ', 1)[0]
    return (cut or text[:max_chars]).rstrip(',;—') + '…'


def _richtext_ratio_excerpt(html, ratio=0.5):
    """Plain teaser at a fraction of full rich-text length (e.g. home page hero)."""
    text = richtext_plain_text(html)
    if not text:
        return ''
    max_chars = max(1, int(len(text) * ratio))
    return _about_plain_excerpt(html, max_chars=max_chars)


def serialize_about_why_item(item, lang='az'):
    return {
        'id': item.id,
        'icon': (item.icon or 'fa-star').strip(),
        'title': _localized_value(item, 'title', lang),
        'text': _localized_value(item, 'text', lang),
    }


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_serialized_about_why_items(lang='az', is_active=True):
    qs = AboutWhyItem.objects.all()
    if is_active:
        qs = qs.filter(is_active=True)
    return [serialize_about_why_item(row, lang) for row in qs.order_by('order', 'id')]


def serialize_about_media_strip_item(media, lang='az'):
    name = _localized_value(media, 'gallery_name', lang)
    first = (name or '').strip().split()
    return {
        'id': media.id,
        'name': name,
        'role': _localized_value(media, 'gallery_role', lang),
        'tag': _localized_value(media, 'gallery_tag', lang),
        'image': media_url(media.image) if media.image else None,
        'first_name': first[0] if first else (name or ''),
    }


def get_about_page_gallery_items(lang='az', limit=8):
    """About page strip gallery from About → Media inline (images only, max 8)."""
    about = get_about(lang)
    if not about:
        return []
    medias = (
        about.medias.filter(image__isnull=False)
        .exclude(image='')
        .order_by('gallery_order', 'created_at', 'id')[:limit]
    )
    return [serialize_about_media_strip_item(media, lang) for media in medias]


def serialize_about(about, lang='az'):
    if about is None:
        return None

    desc_field = get_localized_field_name('description', lang)
    raw_desc = getattr(about, desc_field, about.description_az) or ''

    medias = [
        {
            'id': media.id,
            'image': media_url(media.image) if media.image else None,
            'video': media_url(media.video) if media.video else None,
        }
        for media in about.medias.all()
    ]
    first_image = next((m['image'] for m in medias if m.get('image')), None)

    video = media_url(about.video) if about.video else None
    if not video:
        video = next((m['video'] for m in medias if m.get('video')), None)

    video_cover_full = media_url(about.video_cover) if about.video_cover else None
    video_cover = image_spec_url(about.video_cover_display) if about.video_cover else None
    if not video_cover:
        video_cover = video_cover_full
    if not video_cover:
        video_cover = first_image

    return {
        'id': about.id,
        'description': raw_desc,
        'description_excerpt': _about_plain_excerpt(raw_desc),
        'description_excerpt_short': _about_plain_excerpt(raw_desc, max_chars=200),
        'show_on_homepage': about.show_on_homepage,
        'first_image': first_image,
        'video': video,
        'video_cover': video_cover,
        'medias': medias,
    }


def _whatsapp_me_digits(value):
    if not value:
        return None
    digits = re.sub(r'\D', '', str(value))
    return digits or None


def _tel_href(value):
    if not value:
        return None
    s = ''.join(c for c in str(value) if c.isdigit() or c == '+')
    return s if s else None


def serialize_contact(contact, lang='az'):
    if contact is None:
        return None
    
    address_field = get_localized_field_name('address', lang)
    
    return {
        'id': contact.id,
        'address': getattr(contact, address_field, contact.address_az),
        'phone': contact.phone,
        'whatsapp_number': contact.whatsapp_number,
        'whatsapp_number_2': contact.whatsapp_number_2,
        'whatsapp_number_me': _whatsapp_me_digits(contact.whatsapp_number),
        'whatsapp_number_2_me': _whatsapp_me_digits(contact.whatsapp_number_2),
        'phone_three': contact.phone_three,
        'phone_href': _tel_href(contact.phone),
        'phone_three_href': _tel_href(contact.phone_three),
        'email': contact.email,
        'email_2': contact.email_2,
        'email_3': contact.email_3,
        'instagram': contact.instagram,
        'facebook': contact.facebook,
        'youtube': contact.youtube,
        'linkedn': contact.linkedn,
        'tiktok': contact.tiktok,
        'map_embed_url': (contact.map_embed_url or '').strip() or None,
    }


def paginate_queryset(queryset, page, per_page):
    paginator = Paginator(queryset, per_page)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    return page_obj, paginator


def get_pagination_data(page_obj, paginator):
    return {
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'total_count': paginator.count,
        'per_page': paginator.per_page,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
    }


@cached_page_data(timeout='CACHE_TIMEOUT_MEDIUM')
def _get_home_page_data_cached(request, lang):
    category_slug = request.GET.get('slug')
    is_active = request.GET.get('is_active', 'true').lower() == 'true'

    contact = get_contact(lang)
    serialized_contact = serialize_contact(contact, lang) if contact else None
    
    # Hero carousel üçün 6 ədəd background image (köhnə fallback)
    hero_background_images = get_home_background_images(limit=6)

    abroad_intro_text = get_study_abroad_section(lang=lang)

    return {
        'use_h2_for_section_titles': True,
        'projects': [],
        'categories': [],
        'contact': serialized_contact,
        'projects_pagination': None,
        'filters': {
            'slug': category_slug,
            'is_completed': None,
            'is_active': is_active,
        },
        'background_image': get_background_image('home'),
        'hero_background_images': hero_background_images,
        'abroad_items': get_serialized_abroad_items(
            lang=lang, is_active=True, show_on_main_page=True
        ),
        'universities': get_serialized_universities(is_active=True),
        'abroad_intro_text': abroad_intro_text,
        'abroad_intro_teaser': _richtext_ratio_excerpt(abroad_intro_text, ratio=0.5),
        'reviews': [serialize_review(r) for r in get_reviews()],
        'site_faqs': get_serialized_site_faq_entries(lang=lang, is_active=True),
    }


def get_home_page_data(request, lang):
    ctx = _get_home_page_data_cached(request, lang)
    ctx.update(_fresh_home_blog_context(lang))
    ctx.update(_fresh_home_team_context(lang))
    ctx.update(_fresh_home_categories_context(lang))
    ctx.update(_fresh_home_featured_prices_context(lang))
    ctx.update(_fresh_home_sales_context(lang))
    ctx.update(get_home_about_context(lang))
    ctx.update(_fresh_abroad_advantages_context(lang))
    featured = ctx.get('blog_featured') or []
    if featured and featured[0].get('cover'):
        ctx['lcp_image_url'] = featured[0]['cover']
    return ctx


@cached_page_data(timeout='CACHE_TIMEOUT_LONG')
def get_abroad_page_data(request, lang):
    """Study Abroad listing — full page context (cached; invalidated via AbroadModel / University signals)."""
    contact = get_contact(lang)
    categories = get_project_categories(lang)
    return {
        'contact': serialize_contact(contact, lang) if contact else None,
        'categories': [serialize_project_category(category, lang) for category in categories],
        'abroad_items': get_serialized_abroad_items(lang=lang, is_active=True),
        'universities': get_serialized_universities(is_active=True),
        'background_image': get_background_image('abroad') or get_background_image('about'),
        'abroad_intro_text': get_study_abroad_section(lang=lang),
        'abroad_hero_on_listing_page': True,
    }


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_abroad_detail_view_context(lang, slug):
    """Study Abroad detail — cached per (lang, slug); None if not found."""
    items = get_abroad_items(is_active=True)
    item = next((i for i in items if i.slug == slug), None)
    if not item:
        return None
    item_data = serialize_abroad_item(item, lang=lang)
    contact = get_contact(lang)
    categories = get_project_categories(lang)
    uni_qs = (
        University.objects.filter(study_abroad_id=item.id, is_active=True)
        .only('id', 'name', 'slug', 'flag')
        .order_by('id')
    )
    universities_for_country = [_serialize_university_for_abroad_country_page(u) for u in uni_qs]
    return {
        'abroad_item': item_data,
        'universities': universities_for_country,
        'contact': serialize_contact(contact, lang) if contact else None,
        'categories': [serialize_project_category(category, lang) for category in categories],
        'background_image': get_background_image('abroad') or get_background_image('about'),
        'page_title': f'{item_data["name"]} | Academor',
    }


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_university_detail_view_context(lang, slug):
    """University detail page — cached per (lang, slug); None if not found."""
    translation.activate(lang)
    u = (
        University.objects.filter(slug=slug, is_active=True)
        .select_related('study_abroad')
        .first()
    )
    if not u:
        return None
    contact = get_contact(lang)
    categories = get_project_categories(lang)
    abroad = u.study_abroad
    study_block = None
    if abroad and abroad.is_active:
        study_block = {
            'slug': abroad.slug,
            'name': _localized_value(abroad, 'name', lang),
        }
    display_name = (u.name or '').strip() or _('University')
    university_data = {
        'id': u.id,
        'name': display_name,
        'slug': u.slug,
        'description': _localized_value(u, 'description', lang) or '',
        'flag': media_url(u.flag) if u.flag else None,
        'website': (u.website or '').strip() or None,
        'study_abroad': study_block,
    }
    return {
        'university': university_data,
        'contact': serialize_contact(contact, lang) if contact else None,
        'categories': [serialize_project_category(category, lang) for category in categories],
        'background_image': get_background_image('abroad') or get_background_image('about'),
        'page_title': f'{display_name} | Academor',
    }


def _get_project_list_data_impl(request, lang):
    category_slug = request.GET.get('slug')
    is_active = request.GET.get('is_active', 'true').lower() == 'true'

    categories = get_project_categories(lang)
    serialized_categories = [
        serialize_project_category(category, lang)
        for category in categories
    ]

    selected_category = None
    if category_slug:
        try:
            category_obj = next((cat for cat in categories if cat.slug == category_slug), None)
            if category_obj:
                selected_category = serialize_project_category(category_obj, lang)
        except (ValueError, TypeError):
            pass

    contact = get_contact(lang)
    serialized_contact = serialize_contact(contact, lang) if contact else None

    empty_pagination = {
        'current_page': 1,
        'total_pages': 1,
        'total_count': 0,
        'per_page': 10,
        'has_next': False,
        'has_previous': False,
    }

    lcp_image_url = None
    if selected_category and selected_category.get('image'):
        lcp_image_url = selected_category['image']
    elif serialized_categories:
        lcp_image_url = serialized_categories[0].get('image')

    return {
        'projects': [],
        'categories': serialized_categories,
        'selected_category': selected_category,
        'contact': serialized_contact,
        'pagination': empty_pagination,
        'filters': {
            'slug': category_slug,
            'is_completed': None,
            'is_active': is_active,
        },
        'background_image': get_background_image('courses'),
        'abroad_items': get_serialized_abroad_items(lang=lang, is_active=True),
        'lcp_image_url': lcp_image_url,
    }


@cached_page_data(timeout='CACHE_TIMEOUT_MEDIUM')
def _get_courses_list_data_cached(request, lang):
    return _get_project_list_data_impl(request, lang)


def get_courses_list_data(request, lang):
    ctx = _get_courses_list_data_cached(request, lang)
    _merge_fresh_sale_categories(ctx, lang)
    return ctx


@cached_page_data(timeout='CACHE_TIMEOUT_MEDIUM')
def _get_project_list_data_cached(request, lang):
    return _get_project_list_data_impl(request, lang)


def get_project_list_data(request, lang):
    ctx = _get_project_list_data_cached(request, lang)
    _merge_fresh_sale_categories(ctx, lang)
    return ctx


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_nav_courses(lang='az'):
    """Aktiv kateqoriyalar — header Courses dropdown (slug + ad)."""
    cats = get_project_categories(lang)
    return [serialize_project_category(c, lang) for c in cats]

