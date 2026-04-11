from django.conf import settings

from projects.seo_page_defaults import get_page_seo_defaults
from projects.utils.queries import (
    get_background_image,
    get_contact,
    get_nav_courses,
    get_nav_abroad_items,
    serialize_contact,
)


SEO_HOME = {
    "en": {
        "title": "Academor English Courses | IELTS, Speaking, GMAT, GRE, Study Abroad",
        "description": (
            "Learn English fast and effectively with Academor in Baku, Azerbaijan. "
            "General English, Speaking, IELTS, GMAT, GRE preparation and study abroad support."
        ),
        "keywords": (
            "english language courses, learn english, english in baku, english course, study abroad, "
            "english classes baku, english lessons baku, learn english baku, english language school baku, "
            "english courses azerbaijan, study english baku, english tuition baku, english training baku, "
            "english course baku, english speaking classes baku, ielts preparation baku, "
            "general english baku, gmat preparation baku, gre course baku, "
            "yos preparation, ales course, study abroad support azerbaijan"
        ),
        "h1": "Academor English Courses - Your Path to Success",
    },
    "az": {
        "title": "Academor English Courses | IELTS, Speaking, GMAT, GRE, Xaricdə Təhsil",
        "description": (
            "Academor ilə ingilis dilini sürətli və effektiv öyrən! General English, "
            "Speaking dərsləri, IELTS, GMAT, GRE hazırlığı və xaricdə təhsil dəstəyi. "
            "Bakı, Azərbaycan."
        ),
        "keywords": (
            "ingilis dili kursları, ingilis dili öyrənmək, ingilis dili Bakı, ingilis dili kurs, "
            "xaricdə təhsil, bakıda ingilis dili, ingilis dilində dərslər, ingilis dili dərsləri, "
            "ingilis kursu Bakı, ingilis dili öyrənmək kursu, ingilis dili hazırlığı, "
            "ingilis dili kursu, english course baku, IELTS hazırlıq kursu, speaking dərsləri, "
            "general english dərsləri, GMAT hazırlıq, GRE kursu, YÖS hazırlıq, "
            "ALES kursu, bakıda ən yaxşı ingilis dili kursu, IELTS kursu qiymetleri baku, "
            "speaking club baku, online ingilis dili dərsləri azərbaycan, "
            "xaricdə təhsil üçün hazırlıq kursu, GMAT və GRE hazırlıq kursu baku, "
            "YÖS imtahanına hazırlıq kursu, ALES kursu azərbaycan, "
            "ingilis dili danışıq dərsləri bakı, ingilis dilində öyrənmək, ingilis dili mərkəzi Bakı"
        ),
        "h1": "Academor English Courses - Sənin Uğura Gedən Yolun",
    },
    "ru": {
        "title": "Academor English Courses | IELTS, Speaking, GMAT, GRE, Обучение за рубежом",
        "description": (
            "Изучайте английский быстрее и эффективнее с Academor в Баку, Азербайджан. "
            "General English, Speaking, подготовка к IELTS, GMAT, GRE и поддержка по обучению за рубежом."
        ),
        "keywords": (
            "курсы английского языка, выучить английский, английский язык баку, курс английского, "
            "обучение за рубежом, курсы английского в баку, изучение английского в баку, "
            "школа английского баку, уроки английского баку, английский для взрослых баку, "
            "языковые курсы баку, подготовка по английскому баку, английский азербайджан, "
            "english course baku, курсы английского в баку, подготовка ielts баку, "
            "speaking club baku, gmat gre подготовка баку, обучение за рубежом азербайджан"
        ),
        "h1": "Academor English Courses - Твой путь к успеху",
    },
}

SEO_LOCALE = {"en": "en_US", "az": "az_AZ", "ru": "ru_RU"}


def _request_lang(request):
    lang = (getattr(request, 'LANGUAGE_CODE', '') or '').lower().split('-')[0]
    if lang in {'az', 'en', 'ru'}:
        return lang
    session_lang = (request.session.get('django_language') or request.session.get('language') or '').lower().split('-')[0]
    if session_lang in {'az', 'en', 'ru'}:
        return session_lang
    default_lang = getattr(settings, 'LANGUAGE_CODE', 'az')
    return default_lang if default_lang in {'az', 'en', 'ru'} else 'az'


def site_seo_context(request):
    lang = _request_lang(request)
    data = SEO_HOME.get(lang) or SEO_HOME["en"]
    rm = getattr(request, "resolver_match", None)
    url_name = getattr(rm, "url_name", None) or ""
    page_defaults = get_page_seo_defaults(url_name, lang)
    return {
        "seo_home_title": data["title"],
        "seo_home_description": data["description"],
        "site_seo_keywords": data["keywords"],
        "seo_home_h1": data["h1"],
        "seo_og_locale": SEO_LOCALE.get(lang, "en_US"),
        "seo_geo_region": "AZ",
        "seo_geo_placename": "Baku",
        "default_seo_title": page_defaults.get("title"),
        "default_seo_description": page_defaults.get("description"),
        "default_seo_keywords": page_defaults.get("keywords"),
    }


def site_footer_context(request):
    lang = _request_lang(request)
    contact = get_contact(lang)
    rm = getattr(request, 'resolver_match', None)
    nav_url_name = getattr(rm, 'url_name', '') if rm else ''
    nav_course_slug = ''
    nav_abroad_pk = None
    if rm and getattr(rm, 'kwargs', None):
        nav_course_slug = rm.kwargs.get('slug') or ''
        nav_abroad_pk = rm.kwargs.get('pk')
    return {
        'footer_contact': serialize_contact(contact, lang) if contact else None,
        'footer_background_image': get_background_image('footer'),
        'nav_courses': get_nav_courses(lang),
        'nav_abroad_items': get_nav_abroad_items(lang=lang, is_active=True),
        'nav_url_name': nav_url_name,
        'nav_course_slug': nav_course_slug,
        'nav_abroad_pk': nav_abroad_pk,
    }
