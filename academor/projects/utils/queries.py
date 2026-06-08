import re

from django.db.models import Q, Prefetch
from django.utils import translation
from django.utils.translation import gettext as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.templatetags.static import static

from projects.models import *
from projects.utils.cache_utils import cached_query, cached_page_data
from projects.utils.i18n import normalize_lang, resolve_public_language
from projects.utils.media_cache_bust import media_url
from projects.utils.seo_text import richtext_plain_text
from projects.service_category_icons import resolve_service_category_icon


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
def get_project_categories(lang='az', show_on_main_page=None):
    """Aktiv service kateqoriyaları (courses)."""
    qs = Service.objects.filter(is_active=True).order_by('order', 'id').prefetch_related(
        _category_media_prefetch,
        'price_packages',
    )
    if show_on_main_page is not None:
        qs = qs.filter(show_on_main_page=show_on_main_page)
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


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_team_members(is_active=True):
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
    return {
        'id': member.id,
        'slug': member.slug,
        'image': media_url(member.image) if member.image else None,
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
def get_blog_posts(is_active=True, on_main_page=None):
    queryset = BlogPost.objects.prefetch_related('images')
    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)
    if on_main_page is not None:
        queryset = queryset.filter(on_main_page=on_main_page)
    return list(queryset.order_by('-on_top', '-date', '-id'))


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_blog_post_by_slug(slug, is_active=True):
    queryset = BlogPost.objects.prefetch_related('images').filter(slug=slug)
    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)
    return queryset.first()


def serialize_blog_post(post, lang='az'):
    if post is None:
        return None
    images = [media_url(img.image) for img in post.images.all() if img.image]
    desc_html = _localized_value(post, 'description', lang) or None
    desc_plain = richtext_plain_text(desc_html) if desc_html else ''
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
        'cover': images[0] if images else None,
        'images': images,
    }


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


@cached_page_data(timeout='CACHE_TIMEOUT_MEDIUM')
def get_blog_page_data(request, lang):
    """
    Full context for `/blog/` (blog.html).

    Cached per (request GET params, lang) with TTL ``CACHE_TIMEOUT_MEDIUM``.
    Depends on cached ``get_blog_posts(is_active=True)`` (featured = ``on_top``[:2]; rest = regular posts)
    plus ``get_project_categories`` / ``get_background_image``. Any ``BlogPost`` or ``BlogPostImage``
    change bumps global ``cache_version`` via signals in ``projects.signals`` so listings stay current.
    """
    all_posts = get_blog_posts(is_active=True)
    featured = [p for p in all_posts if p.on_top][:2]
    regular = [p for p in all_posts if not p.on_top]
    categories = get_project_categories(lang)
    return {
        'featured_posts': [serialize_blog_post(p, lang=lang) for p in featured],
        'posts': [serialize_blog_post(p, lang=lang) for p in regular],
        'categories': [serialize_project_category(c, lang) for c in categories],
        'language': lang,
        'background_image': get_background_image('about'),
    }


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_blog_detail_view_context(lang, slug):
    post = get_blog_post_by_slug(slug, is_active=True)
    if not post:
        return None
    all_posts = get_blog_posts(is_active=True)
    other_posts = [p for p in all_posts if p.slug != slug][:6]
    categories = get_project_categories(lang)
    return {
        'post': serialize_blog_post(post, lang=lang),
        'other_posts': [serialize_blog_post(p, lang=lang) for p in other_posts],
        'categories': [serialize_project_category(c, lang) for c in categories],
        'language': lang,
        'background_image': get_background_image('about'),
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


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_motto(lang='az'):
    motto = Tagline.objects.first()
    if not motto:
        return None

    small_field = get_localized_field_name('heading_small', lang)
    main_field = get_localized_field_name('heading_main', lang)
    body_field = get_localized_field_name('body', lang)

    return {
        'heading_small': getattr(motto, small_field, motto.heading_small_az),
        'heading_main': getattr(motto, main_field, motto.heading_main_az),
        'body': getattr(motto, body_field, motto.body_az),
    }


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_mottos(lang='az'):
    """Bütün Tagline obyektlərini carousel slide kimi qaytarır."""
    taglines = Tagline.objects.all().order_by('pk')
    small_field = get_localized_field_name('heading_small', lang)
    main_field = get_localized_field_name('heading_main', lang)
    body_field = get_localized_field_name('body', lang)
    result = []
    for t in taglines:
        result.append({
            'heading_small': getattr(t, small_field, t.heading_small_az),
            'heading_main': getattr(t, main_field, t.heading_main_az),
            'body': getattr(t, body_field, t.body_az),
        })
    return result


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_study_abroad_section(lang='az'):
    obj = StudyAbroadSection.objects.first()
    if not obj:
        return None
    return _localized_value(obj, 'text', lang)


def serialize_study_abroad_advantage(item, lang='az'):
    if item is None:
        return None
    icon = (item.icon or 'fa-star').strip()
    if icon.startswith('fa '):
        icon = icon.replace('fa ', 'fa-', 1).replace(' ', '')
    return {
        'id': item.id,
        'icon': icon,
        'title': _localized_value(item, 'title', lang),
    }


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_study_abroad_advantages_block(lang='az'):
    section = StudyAbroadSection.objects.first()
    if not section:
        return None
    title = (_localized_value(section, 'advantages_title', lang) or '').strip()
    if not title:
        title = _('Advantages of Studying Abroad')
    items = [
        serialize_study_abroad_advantage(row, lang)
        for row in section.advantage_items.filter(is_active=True).order_by('order', 'id')
    ]
    if not title and not items:
        return None
    return {
        'title': title,
        'items': items,
    }


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
    return {
        'id': item.id,
        'slug': item.slug,
        'name': _localized_value(item, 'name', lang),
        'description': _localized_value(item, 'description', lang),
        'img': media_url(item.img) if item.img else None,
        'detail_page_img': media_url(item.detail_page_img) if item.detail_page_img else None,
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


def serialize_price_package(package, lang='az'):
    price = package.price
    if price == price.to_integral_value():
        price_display = str(int(price))
    else:
        price_display = str(price).rstrip('0').rstrip('.')
    return {
        'id': package.id,
        'name': _price_package_display_name(package, lang),
        'duration': package.duration or '',
        'lesson_count': package.lesson_count,
        'lesson_minutes': package.lesson_minutes,
        'price': price,
        'price_display': price_display,
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


def serialize_project_category(category, lang='az'):
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
        'has_payment': bool(active_packages),
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
    packages = [
        serialize_price_package(p, lang)
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

    video_cover = media_url(about.video_cover) if about.video_cover else None
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

    categories = get_project_categories(lang, show_on_main_page=True)
    serialized_categories = [
        serialize_project_category(category, lang)
        for category in categories
    ]

    contact = get_contact(lang)
    serialized_contact = serialize_contact(contact, lang) if contact else None
    
    # Hero carousel üçün 6 ədəd background image (köhnə fallback)
    hero_background_images = get_home_background_images(limit=6)

    # Motto modelindən deviz (köhnə fallback — background_image branch üçün)
    motto = get_motto(lang)

    # Tagline(lar) varsa: hər biri üçün slayd (şəkil siyahısı boş olsa belə — tək home bg və ya statik fallback)
    mottos = get_mottos(lang)

    def _hero_image_urls_for_taglines():
        urls = [u for u in hero_background_images if u]
        if not urls:
            single_home = get_background_image('home')
            if single_home:
                urls = [single_home]
        if not urls:
            urls = [
                static('assets/img/new_baner.png'),
                static('assets/img/banner-landscape-1536x1024.webp'),
            ]
        return urls

    hero_slides = []
    if mottos:
        imgs = _hero_image_urls_for_taglines()
        for i, motto_dict in enumerate(mottos):
            hero_slides.append({
                'image_url': imgs[i % len(imgs)],
                'heading_small': motto_dict['heading_small'],
                'heading_main': motto_dict['heading_main'],
                'body': motto_dict['body'],
            })

    return {
        'use_h2_for_section_titles': True,
        'projects': [],
        'categories': serialized_categories,
        'contact': serialized_contact,
        'projects_pagination': None,
        'filters': {
            'slug': category_slug,
            'is_completed': None,
            'is_active': is_active,
        },
        'background_image': get_background_image('home'),
        'hero_background_images': hero_background_images,
        'motto': motto,
        'hero_slides': hero_slides,
        'abroad_items': get_serialized_abroad_items(
            lang=lang, is_active=True, show_on_main_page=True
        ),
        'universities': get_serialized_universities(is_active=True),
        'abroad_intro_text': get_study_abroad_section(lang=lang),
        'abroad_advantages': get_study_abroad_advantages_block(lang=lang),
        'team': [serialize_team_member(m, lang=lang) for m in get_team_members()],
        'reviews': [serialize_review(r) for r in get_reviews()],
        'site_faqs': get_serialized_site_faq_entries(lang=lang, is_active=True),
    }


def get_home_page_data(request, lang):
    ctx = _get_home_page_data_cached(request, lang)
    ctx.update(_fresh_home_blog_context(lang))
    ctx.update(get_home_about_context(lang))
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
        'abroad_advantages': get_study_abroad_advantages_block(lang=lang),
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
    }


@cached_page_data(timeout='CACHE_TIMEOUT_MEDIUM')
def get_project_list_data(request, lang):
    # Backward-compatible name (used by older views/links)
    return _get_project_list_data_impl(request, lang)


@cached_page_data(timeout='CACHE_TIMEOUT_MEDIUM')
def get_courses_list_data(request, lang):
    # Preferred name for the new "courses" route/view
    return _get_project_list_data_impl(request, lang)


@cached_query(timeout='CACHE_TIMEOUT_MEDIUM')
def get_nav_courses(lang='az'):
    """Aktiv kateqoriyalar — header Courses dropdown (slug + ad)."""
    cats = get_project_categories(lang)
    return [serialize_project_category(c, lang) for c in cats]

