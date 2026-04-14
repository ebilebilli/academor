import re

from django.db.models import Q, Prefetch
from django.utils.html import strip_tags
from django.utils import translation
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.templatetags.static import static

from projects.models import *
from projects.utils.cache_utils import cached_query, get_query_cache_key, cached_page_data
from django.core.cache import cache


def get_language_from_request(request):
    lang = request.GET.get('lang', '').lower() or request.GET.get('language', '').lower()
    if lang in ['az', 'en', 'ru']:
        request.session['django_language'] = lang
        request.session['language'] = lang
        request.session['language_user_chosen'] = True
        request.session.modified = True
        translation.activate(lang)
        return lang
    
    lang = request.session.get('django_language', '').lower()
    if lang in ['az', 'en', 'ru']:
        translation.activate(lang)
        return lang
    
    lang = request.session.get('language', '').lower()
    if lang in ['az', 'en', 'ru']:
        request.session['django_language'] = lang
        request.session.modified = True
        translation.activate(lang)
        return lang
    
    lang = getattr(request, 'LANGUAGE_CODE', settings.LANGUAGE_CODE)
    if lang in ['az', 'en', 'ru']:
        request.session['django_language'] = lang
        request.session['language'] = lang
        request.session.modified = True
        translation.activate(lang)
        return lang

    default_lang = getattr(settings, 'LANGUAGE_CODE', 'az')
    if default_lang not in ('az', 'en', 'ru'):
        default_lang = 'az'
    request.session['django_language'] = default_lang
    request.session['language'] = default_lang
    request.session.modified = True
    translation.activate(default_lang)
    return default_lang


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


_category_media_prefetch = Prefetch(
    'medias',
    queryset=Media.objects.filter(image__isnull=False).exclude(image='').order_by('id'),
)


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_project_categories(lang='az'):
    """Aktiv service kateqoriyaları (courses)."""
    return ServiceCategory.objects.filter(is_active=True).order_by('order', 'id').prefetch_related(
        _category_media_prefetch,
    )


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_active_project_category_by_slug(slug):
    """Tək aktiv kateqoriya (detal səhifə) — şəkillər id sırası ilə."""
    if not slug:
        return None
    return (
        ServiceCategory.objects.filter(slug=slug, is_active=True)
        .prefetch_related(_category_media_prefetch)
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
def get_partners(lang='az', is_active=True):
    queryset = Instructor.objects.prefetch_related(
        Prefetch('medias', queryset=Media.objects.filter(image__isnull=False))
    )
    
    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)
    
    return list(queryset.order_by('-created_at'))


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_team_members(is_active=True):
    queryset = Team.objects.all()
    if is_active is not None and hasattr(Team, 'is_active'):
        queryset = queryset.filter(is_active=is_active)
    return list(queryset.order_by('order', 'id'))


def serialize_team_member(member):
    if member is None:
        return None
    return {
        'id': member.id,
        'image': member.image.url if member.image else None,
        'name': member.name,
        'role': member.role,
        'description': member.description,
        'instagram': getattr(member, 'instagram', None),
        'facebook': getattr(member, 'facebook', None),
        'linkedin': getattr(member, 'linkedin', None),
        'tiktok': getattr(member, 'tiktok', None),
        'youtube': getattr(member, 'youtube', None),
        'descriptor': member.descriptor.url if getattr(member, 'descriptor', None) else None,
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
        'created_at': review.created_at,
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
        return media.image.url
    return None


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_home_background_images(limit=6):
    """Ana səhifə hero karuseli üçün background image-ləri qaytarır (maksimum 6 ədəd)"""
    media_list = Media.objects.filter(
        is_home_page_background_image=True,
        image__isnull=False
    ).order_by('-created_at')[:limit]
    
    return [media.image.url for media in media_list if media.image]


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
    taglines = Tagline.objects.all()
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
def get_service_highlights(is_active=True):
    qs = ServiceHighlight.objects.all()
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    return list(qs.order_by('order', 'id'))


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_serialized_service_highlights(lang='az', is_active=True):
    return [serialize_service_highlight(s, lang) for s in get_service_highlights(is_active=is_active)]


def serialize_service_highlight(item, lang='az'):
    if item is None:
        return None
    return {
        'id': item.id,
        'title': _localized_value(item, 'title', lang),
        'description': _localized_value(item, 'description', lang),
        'order': item.order,
    }


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_study_abroad_section(lang='az'):
    obj = StudyAbroadSection.objects.first()
    if not obj:
        return None
    return _localized_value(obj, 'text', lang)


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_abroad_items(is_active=True):
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
        'created_at',
    )
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    return list(qs.order_by('id'))


def serialize_abroad_item(item, lang='az'):
    if item is None:
        return None
    return {
        'id': item.id,
        'slug': item.slug,
        'name': _localized_value(item, 'name', lang),
        'description': _localized_value(item, 'description', lang),
        'img': item.img.url if item.img else None,
        'detail_page_img': item.detail_page_img.url if item.detail_page_img else None,
        'is_active': item.is_active,
        'created_at': item.created_at,
    }


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_universities(is_active=True):
    qs = University.objects.only('id', 'flag', 'is_active')
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    return list(qs.order_by('id'))


def serialize_university(item):
    if item is None:
        return None
    return {
        'id': item.id,
        'flag': item.flag.url if item.flag else None,
    }


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_serialized_abroad_items(lang='az', is_active=True):
    return [serialize_abroad_item(i, lang=lang) for i in get_abroad_items(is_active=is_active)]


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_nav_abroad_items(lang='az', is_active=True):
    return [serialize_abroad_item(i, lang=lang) for i in get_abroad_items(is_active=is_active)]


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_serialized_universities(is_active=True):
    return [serialize_university(u) for u in get_universities(is_active=is_active)]


@cached_query(timeout='CACHE_TIMEOUT_LONG')
def get_serialized_partners(lang='az', is_active=True):
    return [serialize_partner(p, lang) for p in get_partners(lang=lang, is_active=is_active)]


def serialize_project_category(category, lang='az'):
    name_field = get_localized_field_name('name', lang)
    desc_field = get_localized_field_name('description', lang)
    first_image = None
    for media in category.medias.all():
        if media.image:
            first_image = media.image.url
            break

    raw_desc = getattr(category, desc_field, None)
    if raw_desc is None:
        raw_desc = category.description_az or ''

    return {
        'id': category.id,
        'slug': category.slug,
        'name': getattr(category, name_field, category.name_az),
        'image': first_image,
        'description_html': raw_desc or '',
    }


def serialize_project_category_detail(category, lang='az'):
    """Kurs detalı: bütün şəkil URL-ləri (siyahı səhifələrdə yalnız `image` istifadə olunur)."""
    if category is None:
        return None
    data = serialize_project_category(category, lang)
    data['images'] = [
        media.image.url
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

    return data


def _about_plain_excerpt(html, max_chars=300):
    if not html:
        return ''
    text = strip_tags(str(html))
    text = ' '.join(text.split())
    if len(text) <= max_chars:
        return text
    cut = text[:max_chars].rsplit(' ', 1)[0]
    return (cut or text[:max_chars]).rstrip(',;—') + '…'


def serialize_about(about, lang='az'):
    if about is None:
        return None

    desc_field = get_localized_field_name('description', lang)
    raw_desc = getattr(about, desc_field, about.description_az) or ''

    medias = [
        {
            'id': media.id,
            'image': media.image.url if media.image else None,
            'video': media.video.url if media.video else None,
        }
        for media in about.medias.all()
    ]
    first_image = next((m['image'] for m in medias if m.get('image')), None)

    return {
        'id': about.id,
        'description': raw_desc,
        'description_excerpt': _about_plain_excerpt(raw_desc),
        'first_image': first_image,
        'medias': medias,
    }


def serialize_partner(partner, lang='az'):
    if partner is None:
        return None
    
    name_field = get_localized_field_name('name', lang)
    
    media = next((m for m in partner.medias.all()), None)
    
    return {
        'id': partner.id,
        'name': getattr(partner, name_field, partner.name_az),
        'instagram': partner.instagram,
        'facebook': partner.facebook,
        'linkedn': partner.linkedn,
        'is_active': partner.is_active,
        'created_at': partner.created_at,
        'logo': media.image.url if media and media.image else None,
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
def get_home_page_data(request, lang):
    category_slug = request.GET.get('slug')
    is_active = request.GET.get('is_active', 'true').lower() == 'true'

    categories = get_project_categories(lang)
    serialized_categories = [
        serialize_project_category(category, lang)
        for category in categories
    ]
    
    about = get_about(lang)
    serialized_about = serialize_about(about, lang) if about else None
    
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
                static('assets/img/carousel-2.jpg'),
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

    serialized_service_highlights = get_serialized_service_highlights(lang=lang, is_active=True)

    return {
        'use_h2_for_section_titles': True,
        'projects': [],
        'categories': serialized_categories,
        'partners': [],
        'about': serialized_about,
        'contact': serialized_contact,
        'projects_pagination': None,
        'partners_pagination': None,
        'filters': {
            'slug': category_slug,
            'is_completed': None,
            'is_active': is_active,
        },
        'background_image': get_background_image('home'),
        'hero_background_images': hero_background_images,
        'motto': motto,
        'hero_slides': hero_slides,
        'service_highlights': serialized_service_highlights,
        'abroad_items': get_serialized_abroad_items(lang=lang, is_active=True),
        'universities': get_serialized_universities(is_active=True),
        'team': [serialize_team_member(m) for m in get_team_members()],
        'reviews': [serialize_review(r) for r in get_reviews()],
    }


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
    return {
        'abroad_item': item_data,
        'contact': serialize_contact(contact, lang) if contact else None,
        'categories': [serialize_project_category(category, lang) for category in categories],
        'background_image': get_background_image('abroad') or get_background_image('about'),
        'page_title': f'{item_data["name"]} | Academor',
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

