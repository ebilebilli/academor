"""Per-route default SEO (title, description, keywords) by language.

Used when a view does not set page_title / page_description / page_keywords.
Home uses SEO_HOME from context_processors instead (no entry for home-page).
"""

from __future__ import annotations

from django.conf import settings

# Appended to Azerbaijani keywords on all AZ routes (core commercial / local phrases).
_AZ_KW_CORE = (
    "ingilis dili kursları, ingilis dili öyrənmək, ingilis dili Bakı, ingilis dili kurs, "
    "xaricdə təhsil, bakıda ingilis dili, ingilis dilində dərslər, ingilis dili dərsləri, "
    "ingilis kursu Bakı, ingilis dilində öyrənmək, ingilis dili hazırlığı, ingilis dili mərkəzi Bakı"
)

_EN_KW_CORE = (
    "english language courses, learn english, english in baku, english course, study abroad, "
    "english classes baku, english lessons baku, learn english baku, english language school baku, "
    "english courses azerbaijan, study english baku, english tuition baku, english training baku"
)

_RU_KW_CORE = (
    "курсы английского языка, выучить английский, английский язык баку, курс английского, "
    "обучение за рубежом, курсы английского в баку, изучение английского в баку, "
    "школа английского баку, уроки английского баку, английский для взрослых баку, "
    "языковые курсы баку, подготовка по английскому баку, английский азербайджан"
)

SEO_PAGE_DEFAULTS: dict[str, dict[str, dict[str, str]]] = {
    "en": {
        "courses-page": {
            "title": "English Courses & Programs | Academor — Baku",
            "description": (
                "Browse Academor courses in Baku: General English, Speaking, IELTS, GMAT, GRE, "
                "YÖS, ALES and more. Find the right level and start learning."
            ),
            "keywords": (
                "academor courses, english courses baku, ielts preparation, speaking classes, "
                "gmat gre baku, course levels, " + _EN_KW_CORE
            ),
        },
        "course-detail": {
            "description": (
                "Program details, format, and how to join this Academor English course in Baku, Azerbaijan."
            ),
            "keywords": (
                "academor course, english program baku, course details, enrollment, ielts speaking gmat, "
                + _EN_KW_CORE
            ),
        },
        "mock-tests-page": {
            "title": "Mock Tests | Academor — IELTS & SAT Practice",
            "description": (
                "Buy IELTS and SAT mock test packages at Academor in Baku. "
                "Practice exams with portal access and scored feedback."
            ),
            "keywords": (
                "ielts mock test baku, sat mock test, academor mock exams, practice test azerbaijan, "
                + _EN_KW_CORE
            ),
        },
        "mock-test-detail": {
            "description": (
                "Mock test package options, pricing, and checkout for this Academor practice exam program."
            ),
            "keywords": (
                "mock test package, ielts sat practice baku, academor, exam simulation, " + _EN_KW_CORE
            ),
        },
        "about-page": {
            "title": "About Us | Academor — English & Study Abroad in Baku",
            "description": (
                "Learn about Academor: our teaching approach, exam preparation, and study abroad support "
                "for learners in Baku and Azerbaijan."
            ),
            "keywords": "about academor, english school baku, language center azerbaijan, our story, " + _EN_KW_CORE,
        },
        "services-page": {
            "title": "Services | Academor — Courses, Exams & Support",
            "description": (
                "Explore Academor services: course formats, exam prep, speaking practice, "
                "and guidance for studying abroad from Baku."
            ),
            "keywords": "academor services, english training baku, exam preparation, study abroad help, " + _EN_KW_CORE,
        },
        "abroad-page": {
            "title": "Study Abroad | Academor — Programs from Baku",
            "description": (
                "Study abroad options with Academor: destinations, university profiles, "
                "and step-by-step support for students from Azerbaijan."
            ),
            "keywords": "study abroad baku, academor abroad, universities overseas, azerbaijan students, " + _EN_KW_CORE,
        },
        "abroad-detail": {
            "description": (
                "Details for this study abroad pathway: requirements, timeline, and how Academor supports you from Baku."
            ),
            "keywords": "study abroad program, academor, university placement, baku azerbaijan, " + _EN_KW_CORE,
        },
        "abroad-university-detail": {
            "description": (
                "University profile: programs, highlights, and how Academor supports your application from Baku."
            ),
            "keywords": "university profile, study abroad baku, academor, " + _EN_KW_CORE,
        },
        "contact-page": {
            "title": "Contact | Academor — Baku",
            "description": (
                "Contact Academor in Baku: address, phone, hours, and online form for course and exam questions."
            ),
            "keywords": "contact academor, english school baku address, phone, visit us, " + _EN_KW_CORE,
        },
        "team-page": {
            "title": "Our Team | Academor — Teachers & Advisors",
            "description": (
                "Meet Academor teachers and advisors who deliver English courses, IELTS/GMAT/GRE prep, "
                "and study abroad guidance in Baku."
            ),
            "keywords": "academor team, english teachers baku, ielts instructors, advisors, " + _EN_KW_CORE,
        },
        "team-detail": {
            "description": (
                "Instructor profile at Academor: experience, subjects, and how this teacher supports your goals in Baku."
            ),
            "keywords": "academor teacher, english tutor baku, instructor profile, " + _EN_KW_CORE,
        },
        "tests-page": {
            "title": "English Tests | Academor — Practice & Placement",
            "description": (
                "Take practice or placement tests with Academor to check your English level before you choose a course."
            ),
            "keywords": "english test baku, placement test, academor tests, level check, " + _EN_KW_CORE,
        },
        "test-take": {
            "description": (
                "Complete your English test with Academor online. Your results help us suggest the right course level."
            ),
            "keywords": "online english test, academor placement, level assessment, " + _EN_KW_CORE,
        },
        "blog-page": {
            "title": "Blog | Academor — English & Study Abroad Tips",
            "description": (
                "Read Academor blog articles: English learning tips, IELTS and exam prep, study abroad guidance "
                "and news for learners in Baku and Azerbaijan."
            ),
            "keywords": "academor blog, english tips baku, ielts articles, study abroad blog, " + _EN_KW_CORE,
        },
        "blog-detail": {
            "keywords": "academor blog article, english learning baku, study tips, " + _EN_KW_CORE,
        },
        "blog-tag-page": {
            "description": "Blog articles tagged with this topic at Academor, Baku.",
            "keywords": "academor blog, english articles baku, " + _EN_KW_CORE,
        },
    },
    "az": {
        "courses-page": {
            "title": "İngilis dili kursları və proqramlar | Academor — Bakı",
            "description": (
                "Academor-da kursları kəşf edin: General English, Speaking, IELTS, GMAT, GRE, YÖS, ALES və s. "
                "Səviyyənizə uyğun proqram seçin, Bakı."
            ),
            "keywords": (
                "academor kurslar, ingilis dili bakı, IELTS hazırlıq, speaking dərsləri, "
                "GMAT GRE, kurs səviyyələri, " + _AZ_KW_CORE
            ),
        },
        "course-detail": {
            "description": (
                "Bu Academor proqramı haqqında məlumat: məzmun, format və qeydiyyat. Bakı, Azərbaycan."
            ),
            "keywords": (
                "kurs təsviri, academor, ingilis proqramı bakı, qeydiyyat, IELTS speaking, " + _AZ_KW_CORE
            ),
        },
        "mock-tests-page": {
            "title": "Mock testlər | Academor — IELTS və SAT",
            "description": (
                "Academor-da IELTS və SAT mock test paketləri: portal girişi, praktika imtahanları və qiymətləndirmə."
            ),
            "keywords": (
                "ielts mock test bakı, sat mock test, academor mock imtahan, praktika testi, " + _AZ_KW_CORE
            ),
        },
        "mock-test-detail": {
            "description": (
                "Bu mock test proqramı üçün paketlər, qiymətlər və ödəniş — Academor, Bakı."
            ),
            "keywords": (
                "mock test paketi, ielts sat praktika bakı, academor, imtahan simulyasiyası, " + _AZ_KW_CORE
            ),
        },
        "about-page": {
            "title": "Haqqımızda | Academor — Bakı",
            "description": (
                "Academor haqqında: tədris yanaşması, imtahan hazırlığı və xaricdə təhsil dəstəyi — Bakı və Azərbaycan."
            ),
            "keywords": "academor haqqında, ingilis mərkəzi bakı, dil kursu, missiya, " + _AZ_KW_CORE,
        },
        "services-page": {
            "title": "Xidmətlər | Academor",
            "description": (
                "Academor xidmətləri: dərs formatları, imtahan hazırlığı, danışıq praktikası və xaricdə təhsil məsləhəti."
            ),
            "keywords": "academor xidmətlər, ingilis təlimi bakı, imtahan dəstəyi, " + _AZ_KW_CORE,
        },
        "abroad-page": {
            "title": "Xaricdə təhsil | Academor — Bakı",
            "description": (
                "Academor ilə xaricdə təhsil: istiqamətlər, universitet profilləri və Azərbaycan tələbələri üçün addım-addım dəstək."
            ),
            "keywords": "xaricdə təhsil bakı, academor, universitet seçimi, qəbul dəstəyi, " + _AZ_KW_CORE,
        },
        "abroad-university-detail": {
            "description": (
                "Universitet profili: proqramlar və Academor-un Bakıdan müraciət və qəbul dəstəyi."
            ),
            "keywords": "universitet profili, xaricdə təhsil bakı, academor, " + _AZ_KW_CORE,
        },
        "abroad-detail": {
            "description": (
                "Bu xaricdə təhsil istiqaməti üzrə təfərrüatlar, tələblər və Academor-un Bakıdan dəstəyi."
            ),
            "keywords": "xaricdə təhsil proqramı, academor, universitet, bakı, " + _AZ_KW_CORE,
        },
        "contact-page": {
            "title": "Əlaqə | Academor — Bakı",
            "description": (
                "Academor ilə əlaqə: ünvan, telefon, iş saatları və kurs / imtahan sualları üçün online form."
            ),
            "keywords": "academor əlaqə, ünvan bakı, telefon, yazın, " + _AZ_KW_CORE,
        },
        "team-page": {
            "title": "Komandamız | Academor — müəllimlər və məsləhətçilər",
            "description": (
                "Academor müəllim və məsləhətçiləri: ingilis dərsləri, IELTS/GMAT/GRE hazırlığı və xaricdə təhsil — Bakı."
            ),
            "keywords": "academor komanda, ingilis müəllimi bakı, müəllim heyəti, " + _AZ_KW_CORE,
        },
        "team-detail": {
            "description": (
                "Academor müəllimi: təcrübə, ixtisas və Bakıda tədris dəstəyi haqqında qısa məlumat."
            ),
            "keywords": "academor müəllim, ingilis təlimçi bakı, profil, " + _AZ_KW_CORE,
        },
        "tests-page": {
            "title": "Testlər | Academor — səviyyə və praktika",
            "description": (
                "Academor testləri ilə ingilis səviyyənizi yoxlayın; kurs seçiminə kömək edən praktika və yerləşdirmə testləri."
            ),
            "keywords": "ingilis testi bakı, səviyyə testi, academor test, " + _AZ_KW_CORE,
        },
        "test-take": {
            "description": (
                "Academor online ingilis testini tamamlayın; nəticələr uyğun kurs səviyyəsi təklif etməyə kömək edir."
            ),
            "keywords": "online ingilis testi, academor, səviyyə yoxlaması, " + _AZ_KW_CORE,
        },
        "blog-page": {
            "title": "Bloq | Academor — ingilis dili və xaricdə təhsil",
            "description": (
                "Academor bloqu: ingilis dili məsləhətləri, IELTS və imtahan hazırlığı, xaricdə təhsil xəbərləri "
                "— Bakı və Azərbaycan üçün."
            ),
            "keywords": "academor bloq, ingilis məqalələri bakı, IELTS məsləhətləri, xaricdə təhsil bloq, " + _AZ_KW_CORE,
        },
        "blog-detail": {
            "keywords": "academor bloq məqalə, ingilis dili bakı, təhsil məsləhətləri, " + _AZ_KW_CORE,
        },
        "blog-tag-page": {
            "description": "Bu mövzuya aid Academor bloq məqalələri — Bakı.",
            "keywords": "academor bloq, ingilis məqalələri bakı, " + _AZ_KW_CORE,
        },
    },
    "ru": {
        "courses-page": {
            "title": "Курсы английского и программы | Academor — Баку",
            "description": (
                "Курсы Academor в Баку: General English, Speaking, IELTS, GMAT, GRE, YÖS, ALES и др. "
                "Выберите уровень и формат обучения."
            ),
            "keywords": (
                "курсы academor, английский баку, подготовка ielts, speaking, gmat gre, уровни, " + _RU_KW_CORE
            ),
        },
        "course-detail": {
            "description": (
                "Описание программы Academor: содержание, формат и запись на курс в Баку, Азербайджан."
            ),
            "keywords": "программа academor, курс английского баку, запись, ielts, " + _RU_KW_CORE,
        },
        "mock-tests-page": {
            "title": "Пробные тесты | Academor — IELTS и SAT",
            "description": (
                "Пакеты пробных тестов IELTS и SAT в Academor, Баку: доступ в портал, практика и оценка."
            ),
            "keywords": (
                "ielts mock test баку, sat mock test, academor пробный экзамен, " + _RU_KW_CORE
            ),
        },
        "mock-test-detail": {
            "description": (
                "Пакеты, цены и оплата для этой программы пробных тестов Academor."
            ),
            "keywords": (
                "пакет mock test, ielts sat практика баку, academor, " + _RU_KW_CORE
            ),
        },
        "about-page": {
            "title": "О нас | Academor — Баку",
            "description": (
                "Об Academor: методика, подготовка к экзаменам и поддержка при обучении за рубежом в Баку и Азербайджане."
            ),
            "keywords": "о academor, школа английского баку, языковой центр, " + _RU_KW_CORE,
        },
        "services-page": {
            "title": "Услуги | Academor",
            "description": (
                "Услуги Academor: форматы занятий, подготовка к экзаменам, разговорная практика и консультации по учёбе за рубежом."
            ),
            "keywords": "услуги academor, обучение английскому баку, экзамены, " + _RU_KW_CORE,
        },
        "abroad-page": {
            "title": "Обучение за рубежом | Academor — Баку",
            "description": (
                "Программы обучения за рубежом с Academor: направления, профили вузов и сопровождение из Азербайджана."
            ),
            "keywords": "учёба за рубежом баку, academor, поступление за границу, " + _RU_KW_CORE,
        },
        "abroad-detail": {
            "description": (
                "Детали программы обучения за рубежом: требования, этапы и поддержка Academor из Баку."
            ),
            "keywords": "программа за рубежом, academor, университет, баку, " + _RU_KW_CORE,
        },
        "abroad-university-detail": {
            "description": (
                "Профиль вуза: программы и сопровождение заявки от Academor в Баку."
            ),
            "keywords": "профиль вуза, учёба за рубежом баку, academor, " + _RU_KW_CORE,
        },
        "contact-page": {
            "title": "Контакты | Academor — Баку",
            "description": (
                "Связаться с Academor в Баку: адрес, телефон, часы работы и форма для вопросов по курсам и экзаменам."
            ),
            "keywords": "контакты academor, адрес баку, телефон, запись, " + _RU_KW_CORE,
        },
        "team-page": {
            "title": "Команда | Academor — преподаватели и консультанты",
            "description": (
                "Преподаватели и консультанты Academor: курсы английского, IELTS/GMAT/GRE и обучение за рубежом в Баку."
            ),
            "keywords": "команда academor, преподаватели английского баку, " + _RU_KW_CORE,
        },
        "team-detail": {
            "description": (
                "Профиль преподавателя Academor: опыт, предметы и как он помогает достичь целей в Баку."
            ),
            "keywords": "преподаватель academor, репетитор английского баку, " + _RU_KW_CORE,
        },
        "tests-page": {
            "title": "Тесты по английскому | Academor",
            "description": (
                "Пробные и определяющие тесты Academor: проверьте уровень английского перед выбором курса."
            ),
            "keywords": "тест английского баку, определение уровня, academor, " + _RU_KW_CORE,
        },
        "test-take": {
            "description": (
                "Пройдите онлайн-тест Academor; результаты помогут подобрать подходящий уровень курса."
            ),
            "keywords": "онлайн тест английского, academor, уровень, " + _RU_KW_CORE,
        },
        "blog-page": {
            "title": "Блог | Academor — английский и учёба за рубежом",
            "description": (
                "Блог Academor: советы по английскому, подготовка к IELTS и экзаменам, обучение за рубежом — "
                "для учащихся в Баку и Азербайджане."
            ),
            "keywords": "блог academor, статьи английский баку, ielts советы, учёба за рубежом блог, " + _RU_KW_CORE,
        },
        "blog-detail": {
            "keywords": "статья блога academor, английский баку, советы по учёбе, " + _RU_KW_CORE,
        },
        "blog-tag-page": {
            "description": "Статьи блога Academor с этой меткой — Баку.",
            "keywords": "блог academor, статьи английский баку, " + _RU_KW_CORE,
        },
    },
}


GENERIC_ROUTE_DESCRIPTION_FALLBACK = {
    "en": (
        "Academor — English lessons, exams (IELTS, GMAT, GRE, SAT, YÖS, ALES) and study-abroad "
        "support from Baku, Azerbaijan."
    ),
    "az": (
        "Academor Bakıdan ingilis dili, imtahan hazırlığı (IELTS, GMAT və s.) və xaricdə təhsil dəstəyi təklif edir."
    ),
    "ru": (
        "Academor — занятия английским, подготовка к экзаменам (IELTS, GMAT и др.) и поддержка учёбы "
        "за рубежом в Баку, Азербайджан."
    ),
}


def get_page_seo_defaults(url_name: str, lang: str) -> dict[str, str]:
    if not url_name or url_name == "home-page":
        return {}
    site_lang = getattr(settings, "LANGUAGE_CODE", "az")
    if site_lang not in SEO_PAGE_DEFAULTS:
        site_lang = "az"
    lang_key = lang if lang in SEO_PAGE_DEFAULTS else site_lang
    table = SEO_PAGE_DEFAULTS.get(lang_key) or SEO_PAGE_DEFAULTS.get(site_lang) or SEO_PAGE_DEFAULTS["az"]
    row = table.get(url_name)
    out: dict[str, str] = dict(row) if row else {}
    if not out.get("description"):
        out["description"] = GENERIC_ROUTE_DESCRIPTION_FALLBACK.get(
            lang_key,
            GENERIC_ROUTE_DESCRIPTION_FALLBACK["az"],
        )
    return out
