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
        "title": "Academor | English lessons, IELTS, GMAT, SAT, GRE, YÖS, ALES, Study abroad, Only Speaking",
        "description": (
            "Learn English fast and effectively with Academor in Baku, Azerbaijan. "
            "English lessons, IELTS, GMAT, SAT, GRE, YÖS, ALES, study abroad support and Only Speaking."
        ),
        "keywords": (
            "english lessons, english language courses, learn english, english in baku, english course, study abroad, "
            "english classes baku, english lessons baku, learn english baku, english language school baku, "
            "english courses azerbaijan, study english baku, english tuition baku, english training baku, "
            "english course baku, english speaking classes baku, ielts preparation baku, "
            "general english baku, gmat preparation baku, gre course baku, sat preparation baku, "
            "yos preparation, ales course, study abroad support azerbaijan, only speaking"
        ),
        "h1": "Academor English Courses - Your Path to Success",
    },
    "az": {
        "title": (
            "İngilis dili dərsləri, IELTS, GMAT, SAT, GRE, YÖS, ALES, Xaricdə təhsil, Only Speaking | Academor"
        ),
        "description": (
            "Academor Bakıda: ingilis dili dərsləri, IELTS, GMAT, SAT, GRE, YÖS və ALES hazırlığı, "
            "xaricdə təhsil dəstəyi və Only Speaking. Sürətli və effektiv öyrənmə — Azərbaycan."
        ),
        "keywords": (
            "ingilis dili dərsləri, IELTS, GMAT, SAT, GRE, YÖS, ALES, xaricdə təhsil, Only Speaking, "
            "ingilis dili kursları, ingilis dili öyrənmək, ingilis dili Bakı, ingilis dili kurs, "
            "bakıda ingilis dili, ingilis dilində dərslər, ingilis kursu Bakı, ingilis dili hazırlığı, "
            "IELTS hazırlıq kursu, speaking dərsləri, general english dərsləri, GMAT hazırlıq, GRE kursu, "
            "SAT hazırlıq, YÖS hazırlıq, ALES kursu, bakıda ən yaxşı ingilis dili kursu, "
            "online ingilis dili dərsləri azərbaycan, xaricdə təhsil üçün hazırlıq kursu, "
            "ingilis dili mərkəzi Bakı"
        ),
        "h1": (
            "İngilis dili dərsləri, IELTS, GMAT, SAT, GRE, YÖS, ALES, xaricdə təhsil və Only Speaking"
        ),
    },
    "ru": {
        "title": (
            "Academor | Уроки английского, IELTS, GMAT, SAT, GRE, YÖS, ALES, обучение за рубежом, Only Speaking"
        ),
        "description": (
            "Изучайте английский быстрее и эффективнее с Academor в Баку, Азербайджан. "
            "Уроки английского, IELTS, GMAT, SAT, GRE, YÖS, ALES, поддержка по обучению за рубежом и Only Speaking."
        ),
        "keywords": (
            "уроки английского, курсы английского языка, выучить английский, английский язык баку, курс английского, "
            "обучение за рубежом, курсы английского в баку, изучение английского в баку, "
            "школа английского баку, уроки английского баку, английский для взрослых баку, "
            "языковые курсы баку, подготовка по английскому баку, английский азербайджан, "
            "english course baku, подготовка ielts баку, подготовка sat баку, "
            "gmat gre подготовка баку, yos ales подготовка, обучение за рубежом азербайджан, only speaking"
        ),
        "h1": "Academor English Courses - Твой путь к успеху",
    },
}

SEO_LOCALE = {"en": "en_US", "az": "az_AZ", "ru": "ru_RU"}


def _site_content_lang():
    code = getattr(settings, "LANGUAGE_CODE", "az")
    return code if code in {"az", "en", "ru"} else "az"


def _seo_lang(request):
    """Meta title/description üçün dil: yalnız istifadəçi dil seçəndə en/ru; əks halda əsas dil (az).

    Beləliklə Google və ilk ziyarətçilər üçün default snippet azərbaycanca qalır; brauzer dilinə görə
    sessiyaya yazılan avtomatik \"en\" SEO-nu ingiliscə etməz.
    """
    if request.session.get("language_user_chosen"):
        v = (request.session.get("django_language") or "").lower().split("-")[0]
        if v in {"az", "en", "ru"}:
            return v
    return _site_content_lang()


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
    lang = _seo_lang(request)
    site_lang = _site_content_lang()
    # Saytın əsas dili (az) — naməlum dildə ingiliscə yox, azərbaycanca fallback
    data = SEO_HOME.get(lang) or SEO_HOME.get(site_lang) or SEO_HOME["az"]
    rm = getattr(request, "resolver_match", None)
    url_name = getattr(rm, "url_name", None) or ""
    page_defaults = get_page_seo_defaults(url_name, lang)
    return {
        "seo_home_title": data["title"],
        "seo_home_description": data["description"],
        "site_seo_keywords": data["keywords"],
        "seo_home_h1": data["h1"],
        "seo_og_locale": SEO_LOCALE.get(lang, "az_AZ"),
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
    nav_abroad_slug = ''
    if rm and getattr(rm, 'kwargs', None):
        if nav_url_name == 'course-detail':
            nav_course_slug = rm.kwargs.get('slug') or ''
        elif nav_url_name == 'abroad-detail':
            nav_abroad_slug = rm.kwargs.get('slug') or ''
    return {
        'footer_contact': serialize_contact(contact, lang) if contact else None,
        'footer_background_image': get_background_image('footer'),
        'nav_courses': get_nav_courses(lang),
        'nav_abroad_items': get_nav_abroad_items(lang=lang, is_active=True),
        'nav_url_name': nav_url_name,
        'nav_course_slug': nav_course_slug,
        'nav_abroad_slug': nav_abroad_slug,
    }
