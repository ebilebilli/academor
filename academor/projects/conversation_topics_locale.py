"""Azerbaijani and Russian UI copy for conversation topic *explanations*.

Vocabulary *terms* and English practice lines stay in English; glosses and
pedagogical notes are localized here."""

from __future__ import annotations


def _lang(lang: str) -> str:
    return lang if lang in ("en", "az", "ru") else "en"


def list_page_h1(lang: str) -> str:
    """Index page main heading (localized; no gettext .mo required)."""
    return _LIST_PAGE_H1[_lang(lang)]


def list_page_lead(lang: str) -> str:
    """Index page intro paragraph."""
    return _LIST_PAGE_LEAD[_lang(lang)]


def list_topics_count_label(count: int, lang: str) -> str:
    """E.g. '42 topics' / '42 mövzu' / '42 темы' (Russian plural simplified to 'N тем')."""
    lang = _lang(lang)
    if lang == "az":
        return f"{count} mövzu"
    if lang == "ru":
        return f"{count} тем"
    return f"{count} topics"


def list_page_title_site(lang: str) -> str:
    """Browser title for the topics index."""
    return _LIST_PAGE_TITLE[_lang(lang)]


def list_page_meta_description(lang: str) -> str:
    return _LIST_META_DESCRIPTION[_lang(lang)]


_LIST_PAGE_H1 = {
    "en": "English conversation topics",
    "az": "İngilis dilində danışıq mövzuları",
    "ru": "Темы для разговорной практики на английском",
}

_LIST_PAGE_LEAD = {
    "en": (
        "Pick a theme for speaking or writing. Each topic page has vocabulary with explanations, "
        "study tips, useful phrases, model sentences, questions, and short writing tasks."
    ),
    "az": (
        "Danışıq və ya yazı üçün mövzu seçin. Hər mövzunun səhifəsində izahlı lüğət, tədris qeydləri, "
        "faydalı ifadələr, nümunə cümlələr, suallar və qısa yazı tapşırıqları var."
    ),
    "ru": (
        "Выберите тему для говорения или письма. На странице каждой темы — словарь с пояснениями, "
        "учебные советы, полезные фразы, примеры предложений, вопросы и короткие письменные задания."
    ),
}

_LIST_PAGE_TITLE = {
    "en": "English conversation topics | Academor",
    "az": "İngilis dilində danışıq mövzuları | Academor",
    "ru": "Темы для разговорной практики на английском | Academor",
}

_LIST_META_DESCRIPTION = {
    "en": (
        "Vocabulary glosses, study tips, and section headings follow your site language; "
        "English headwords and practice lines stay in English for the classroom."
    ),
    "az": (
        "Lüğət izahları, tədris qeydləri və bölmə başlıqları sayt dilinizə uyğundur; "
        "ingilis sözləri və dərsdə istifadə üçün nümunə sətirlər ingilis dilində qalır."
    ),
    "ru": (
        "Пояснения к словам, учебные подсказки и заголовки — на языке сайта; "
        "английские слова и фразы для занятий остаются на английском."
    ),
}


def theme_keyword_gloss(title: str, lang: str) -> str:
    lang = _lang(lang)
    if lang == "en":
        return f'A key word connected to the theme "{title}".'
    if lang == "az":
        return f"«{title}» mövzusu ilə bağlı əsas söz."
    return f'Ключевое слово, связанное с темой «{title}».'


def gloss(en: str, lang: str) -> str:
    """Translate a vocabulary gloss; fall back to English if missing."""
    lang = _lang(lang)
    if lang == "en":
        return en
    pair = _GLOSSES.get(en)
    if not pair:
        return en
    return pair[0] if lang == "az" else pair[1]


def overview_paragraphs(title: str, cluster: str, lang: str) -> tuple[str, ...]:
    lang = _lang(lang)
    p1 = _OVERVIEW_P1[lang].format(title=title)
    p2 = _OVERVIEW_P2[lang]
    note = _CLUSTER_NOTES.get(cluster, _CLUSTER_NOTES["general"])[lang]
    tip = _STUDY_TIP[lang]
    return (p1, p2, note, tip)


_OVERVIEW_P1 = {
    "en": (
        'This speaking unit focuses on "{title}". The goal is to move beyond short answers '
        "and build paragraphs you could use in conversation, interviews, or presentations."
    ),
    "az": (
        'Bu danışıq vahidi «{title}» mövzusuna həsr olunub. Məqsəd qısa cavablardan kənara çıxmaq və '
        "danışıq, müsahibə və ya təqdimatlarda istifadə edə biləcəyiniz abzaslar qurmaqdır."
    ),
    "ru": (
        'Этот блок разговорной практики посвящён теме «{title}». Цель — выйти за рамки коротких ответов '
        "и строить развёрнутые реплики для беседы, собеседований и презентаций."
    ),
}

_OVERVIEW_P2 = {
    "en": (
        "Strong answers usually mix description (what happened), explanation (why it matters), "
        "and evaluation (what you think now). Try to use at least three new words from the list below."
    ),
    "az": (
        "Güclü cavablar adətən təsviri (nə baş verib), izahı (niyə vacibdir) və qiymətləndirməni "
        "(indi nə düşünürsünüz) birləşdirir. Aşağıdakı siyahıdan ən azı üç yeni söz işlədin."
    ),
    "ru": (
        "Сильные ответы обычно сочетают описание (что произошло), объяснение (почему это важно) "
        "и оценку (что вы думаете сейчас). Постарайтесь использовать не меньше трёх новых слов из списка ниже."
    ),
}

_STUDY_TIP = {
    "en": (
        "In class, aim for clear structure: state one main idea, give one concrete example, "
        "then invite your partner to respond with a question."
    ),
    "az": (
        "Dərsdə aydın struktur hədəfləyin: bir əsas fikir deyin, bir konkret nümunə gətirin, "
        "sonra həmsöhbətinizi sualla cavaba dəvət edin."
    ),
    "ru": (
        "На занятии держите ясную структуру: назовите одну главную мысль, приведите один конкретный пример, "
        "затем предложите собеседнику ответить вопросом."
    ),
}

_CLUSTER_NOTES: dict[str, dict[str, str]] = {
    "grammar_time": {
        "en": "Pay special attention to time expressions and how they change verb forms.",
        "az": "Zaman ifadələrinə və onların fel formalarını necə dəyişdirdiyinə xüsusi diqqət yetirin.",
        "ru": "Обратите особое внимание на выражения времени и то, как они меняют формы глаголов.",
    },
    "hypothetical_drill": {
        "en": "Practice both quick reactions and slower, reasoned answers; examiners reward both.",
        "az": "Həm tez reaksiyaları, həm də yavaş, əsaslandırılmış cavabları məşq edin; hər ikisi qiymətləndirilir.",
        "ru": "Тренируйте и быстрые реакции, и вдумчивые ответы; экзаменаторы ценят оба стиля.",
    },
    "usa_geo": {
        "en": "Balance facts you have learned with careful language—hedge when you are not sure.",
        "az": "Öyrəndiyiniz faktları ehtiyatlı dil ilə balanslaşdırın — əmin deyilsinizsə, yumşaldıcı ifadələr işlədin.",
        "ru": "Сочетайте изученные факты с осторожной формулировкой — смягчайте формулировки, если вы не уверены.",
    },
    "safety_disaster": {
        "en": "Use calm, precise vocabulary; avoid exaggeration unless you are telling a story.",
        "az": "Sakit və dəqiq leksika işlədin; hekayə danışmırsaqsınız, həddi artırmayın.",
        "ru": "Используйте спокойную и точную лексику; избегайте преувеличений, если вы не рассказываете историю.",
    },
    "media_tech": {
        "en": "Be ready to compare benefits and risks without relying only on slogans.",
        "az": "Faydaları və riskləri yalnız şüarlarla deyil, əsaslandırılmış şəkildə müqayisə etməyə hazır olun.",
        "ru": "Будьте готовы сравнивать плюсы и минусы, опираясь не только на лозунги.",
    },
    "money_consumer": {
        "en": "Numbers and examples make abstract money topics easier to follow.",
        "az": "Rəqəmlər və nümunələr pul mövzularını daha aydın edir.",
        "ru": "Цифры и примеры делают абстрактные темы про деньги понятнее.",
    },
    "leisure_travel": {
        "en": "Sensory details (sights, sounds, routines) make travel stories memorable.",
        "az": "Hiss detalları (mənzərələr, səslər, gündəlik rutin) səyahət hekayələrini yaddaqalan edir.",
        "ru": "Сенсорные детали (звуки, картинки, распорядок дня) делают рассказы о поездках запоминающимися.",
    },
    "family_social": {
        "en": "Respect privacy: share what you are comfortable discussing and invite others to do the same.",
        "az": "Məxfiliyə hörmət edin: danışmağa hazır olduğunuzu paylaşın və başqalarını da eyni şəkildə dəvət edin.",
        "ru": "Уважайте личные границы: делитесь тем, о чём готовы говорить, и предложите то же другим.",
    },
    "work_study": {
        "en": "Link habits (revision, feedback) to outcomes (grades, confidence, career).",
        "az": "Vərdişləri (təkrar, rəy) nəticələrlə (qiymət, özgüvən, karyera) əlaqələndirin.",
        "ru": "Связывайте привычки (повторение, обратная связь) с результатами (оценки, уверенность, карьера).",
    },
    "health": {
        "en": "Stay factual and kind; health topics can be sensitive for classmates.",
        "az": "Faktual və nəzakətli olun; sağlamlıq mövzuları sinif yoldaşlarınız üçün həssas ola bilər.",
        "ru": "Оставайтесь добрыми и опирайтесь на факты: темы здоровья могут быть деликатными.",
    },
    "society": {
        "en": "Acknowledge different viewpoints before you argue against them.",
        "az": "Etiraz etməzdən əvvəl fərqli baxışları etiraf edin.",
        "ru": "Признайте разные точки зрения, прежде чем возражать против них.",
    },
    "environment_science": {
        "en": "Separate what is widely accepted from what is still debated.",
        "az": "Geniş qəbul ediləni hələ mübahisəli olanından ayırın.",
        "ru": "Разделяйте общепринятое и то, что всё ещё обсуждается.",
    },
    "arts_culture": {
        "en": 'Describe what you notice before you judge whether something is "good."',
        "az": 'Bir şeyin "yaxşı" olub-olmadığına qərar verməzdən əvvəl nə gördüyünüzü təsvir edin.',
        "ru": "Сначала опишьте, что замечаете, и только потом оценивайте, «хорошо» это или нет.",
    },
    "emotion_behavior": {
        "en": "Name emotions precisely; it helps listeners understand you.",
        "az": "Emosiyaları dəqiq adlandırın; bu, dinləyicilərin sizi başa düşməsinə kömək edir.",
        "ru": "Называйте эмоции точно — так слушателям проще вас понять.",
    },
    "general": {
        "en": "Almost any topic can connect to values, habits, and future plans—use those bridges.",
        "az": "Demək olar ki, hər mövzu dəyərlər, vərdişlər və gələcək planlarla bağlana bilər — bu körpülərdən istifadə edin.",
        "ru": "Почти любую тему можно связать с ценностями, привычками и планами на будущее — используйте эти связи.",
    },
}


# English gloss (msgid) -> (Azerbaijani, Russian)
_GLOSSES: dict[str, tuple[str, str]] = {
    "make something easier to understand by explaining it": (
        "izah etməklə bir şeyi başa düşülməsi asanlaşdırmaq",
        "объяснить что-то так, чтобы это стало понятнее",
    ),
    "add more detail to what you are saying": (
        "dediklərinizə daha çox detal əlavə etmək",
        "добавить больше деталей к тому, что вы говорите",
    ),
    "a personal opinion or way of seeing a topic": (
        "şəxsi fikir və ya mövzuya baxış tərzi",
        "личное мнение или способ видеть тему",
    ),
    "something you accept as true without proof": (
        "sübut olmadan doğru qəbul etdiyiniz bir şey",
        "то, что вы принимаете за истину без доказательств",
    ),
    "a small, subtle difference in meaning or feeling": (
        "mənada və ya hisdə kiçik, incə fərq",
        "тонкое отличие в значении или оттенке чувства",
    ),
    "using careful language so you do not sound too absolute": (
        "çox kategorik səslənməmək üçün ehtiyatlı dil işlətmək",
        "осторожные формулировки, чтобы не звучать категорично",
    ),
    "a reason against an idea you have mentioned": (
        "qeyd etdiyiniz fikrə qarşı arqument",
        "довод против упомянутой вами идеи",
    ),
    "a short personal story used to illustrate a point": (
        "bir fikri nümayiş etdirmək üçün qısa şəxsi hekayə",
        "короткая личная история, иллюстрирующая мысль",
    ),
    "closely connected to the subject you are discussing": (
        "müzakirə etdiyiniz mövzuya sıx bağlı",
        "тесно связано с обсуждаемой темой",
    ),
    "something that you have lived through": (
        "özünüzün yaşadığı bir təcrübə",
        "то, что вы пережили сами",
    ),
    "what you think about a topic, not necessarily a fact": (
        "mövzuda nə düşündüyünüz; həmişə fakt olmaya bilər",
        "то, что вы думаете по теме; это не обязательно факт",
    ),
    "earlier events or context that help explain a situation": (
        "vəziyyəti izah etməyə kömək edən əvvəlki hadisələr və ya kontekst",
        "предыдущие события или контекст, помогающие объяснить ситуацию",
    ),
    "look at two things to see how they are similar or different": (
        "oxşar və ya fərqli olduqlarını görmək üçün iki şeyə baxmaq",
        "рассмотреть два объекта, чтобы увидеть сходства и различия",
    ),
    "focus on differences between two things": (
        "iki şey arasındakı fərqlərə diqqət yetirmək",
        "сосредоточиться на различиях между двумя вещами",
    ),
    "give the main ideas in a short form": (
        "əsas fikirləri qısa şəkildə vermək",
        "кратко изложить основные идеи",
    ),
    "a tendency to prefer one side or view unfairly": (
        "bir tərəfə və ya baxışa haqsız üstünlük vermə meyli",
        "несправедливая склонность к одной стороне или точке зрения",
    ),
    "help or encouragement you give to someone": (
        "kiməsə göstərdiyiniz kömək və ya təşviqat",
        "помощь или поддержка, которую вы даёте человеку",
    ),
    "limits about what behavior you accept from others": (
        "başqalarından hansı davranışı qəbul etdiyiniz haqqında hədlər",
        "границы допустимого поведения других по отношению к вам",
    ),
    "beliefs about what should happen or how people should act": (
        "nə baş verməli və ya insanların necə davranmalı olduğu haqqında inanclar",
        "представления о том, что должно происходить и как люди должны себя вести",
    ),
    "an agreement where each side gives up something": (
        "hər tərəfin bir şeydən güzəşt etdiyi razılıq",
        "соглашение, в котором каждая сторону чем-то уступает",
    ),
    "belief that someone is honest and reliable": (
        "kiminsə dürüst və etibarlı olduğuna inam",
        "уверенность, что человек честен и надёжен",
    ),
    "serious disagreement or argument": (
        "ciddi razılaşmazlıq və ya mübahisə",
        "серьёзное несогласие или спор",
    ),
    "all the people living together in one home": (
        "bir evdə birlikdə yaşayan bütün insanlar",
        "все люди, живущие вместе в одном доме",
    ),
    "the way you were cared for and taught as a child": (
        "uşaqkən qayğı görmə və təhsil alma tərziniz",
        "как вас воспитывали и чему учили в детстве",
    ),
    "a certificate, degree, or skill that proves ability": (
        "bacarığı sübut edən sertifikat, dərəcə və ya bacarıq",
        "диплом, сертификат или навык, подтверждающие компетенцию",
    ),
    "the latest time something must be finished": (
        "bir şeyin bitməli olduğu son vaxt",
        "крайний срок завершения чего-либо",
    ),
    "comments about how well you did and how to improve": (
        "nə qədər yaxşı etdiyiniz və təkmilləşmə yolları haqqında rəylər",
        "комментарии о том, как вы справились и как улучшить результат",
    ),
    "the full set of subjects or topics in a course": (
        "kursda öyrənilən fənlər və ya mövzuların tam siyahısı",
        "полный набор предметов или тем курса",
    ),
    "a person of the same age or level as you in school or work": (
        "məktəbdə və ya işdə sizinlə eyni yaş və ya səviyyədə olan şəxs",
        "человек того же возраста или уровня, что и вы в учёбе или работе",
    ),
    "using someone else's work as if it were your own": (
        "başqasının işini öz işinizmiş kimi təqdim etmək",
        "выдавать чужую работу за свою",
    ),
    "studying material again before a test": (
        "imtahandan əvvəl materialı təkrar öyrənmək",
        "повторение материала перед экзаменом",
    ),
    "a short period of training work, often for students": (
        "tez-tez tələbələr üçün qısa müddətli təcrübə işi",
        "короткий период стажировки, часто для студентов",
    ),
    "a sign that you might be ill or stressed": (
        "xəstə və ya stressli ola biləcəyinizin əlaməti",
        "признак того, что вы можете быть больны или в стрессе",
    ),
    "actions that stop a problem before it starts": (
        "problem başlamazdan əvvəl onu dayandıran tədbirlər",
        "действия, предотвращающие проблему до её появления",
    ),
    "your general state of health and happiness": (
        "sağlamlıq və xoşbəxtliyinizin ümumi vəziyyəti",
        "общее состояние здоровья и благополучия",
    ),
    "continuing for a long time, not just once": (
        "yalnız bir dəfə deyil, uzun müddət davam edən",
        "длящееся долго, а не разово",
    ),
    "the process of getting better after illness or injury": (
        "xəstəlik və ya zədədən sonra yaxşılaşma prosesi",
        "процесс восстановления после болезни или травмы",
    ),
    "the food you eat and how it affects your body": (
        "yediyiniz qida və onun bədəninizə təsiri",
        "питание и его влияние на организм",
    ),
    "involving a lot of sitting and little physical activity": (
        "çox oturmaq və az fiziki fəaliyyət deməkdir",
        "много сидения и мало физической активности",
    ),
    "ability to recover from difficulties": (
        "çətinliklərdən sonra ayağa qalma qabiliyyəti",
        "способность восстанавливаться после трудностей",
    ),
    "something that can cause harm or danger": (
        "zərər və ya təhlükə yarada bilən bir şey",
        "то, что может причинить вред или опасность",
    ),
    "organized movement of people away from danger": (
        "təhlükədən insanların təşkilı şəkildə çıxarılması",
        "организованная эвакуация людей из опасной зоны",
    ),
    "simple medical care given immediately after an injury": (
        "zədədən dərhal sonra göstərilən sadə tibbi yardım",
        "простая неотложная медицинская помощь после травмы",
    ),
    "an agreement that pays money if you have a loss": (
        "itkə düşsəniz pul ödəyən müqavilə",
        "договор, по которому выплачивают деньги при убытке",
    ),
    "basic supplies kept ready for a crisis": (
        "fövqəladə hallar üçün hazır saxlanılan əsas ləvaqemat",
        "базовый набор припасов на случай кризиса",
    ),
    "a smaller earthquake following a larger one": (
        "böyük zəlzələdən sonra gələn daha kiçik təkan",
        "более слабое землетрясение после сильного",
    ),
    "a safe place that protects you from weather or danger": (
        "hava və ya təhlükədən qoruyan təhlükəsiz yer",
        "безопасное место, защищающее от погоды или опасности",
    ),
    "steps that reduce the seriousness of a future risk": (
        "gələcək riskin ağırlığını azaldan addımlar",
        "меры, снижающие тяжесть будущего риска",
    ),
    "a set of rules a computer uses to sort or show content": (
        "kompüterin məzmunu sıralaması və ya göstərməsi üçün istifadə etdiyi qaydalar",
        "набор правил, по которым компьютер сортирует или показывает контент",
    ),
    "control over who sees your personal information": (
        "şəxsi məlumatınızı kimin görəcəyinə nəzarət",
        "контроль над тем, кто видит ваши личные данные",
    ),
    "false information spread without intending to lie": (
        "yalan demək niyyəti olmadan yayılan yanlış məlumat",
        "ложная информация, распространяемая без намерения обманывать",
    ),
    "false information spread on purpose to mislead": (
        "aldatmaq məqsədi ilə qəsdən yayılan yanlış məlumat",
        "ложная информация, распространяемая намеренно, чтобы ввести в заблуждение",
    ),
    "an alert on your phone or computer": (
        "telefon və ya kompüterdə bildiriş",
        "уведомление на телефоне или компьютере",
    ),
    "hours spent using phones, TVs, or computers": (
        "telefon, TV və ya kompüter qarşısında keçirilən saatlar",
        "часы, проведённые за телефоном, ТВ или компьютером",
    ),
    "the record of your activity left online": (
        "onlayn qalan fəaliyyət iziniz",
        "след вашей активности в интернете",
    ),
    "using digital tools to harass or threaten someone": (
        "kimisə təqib və ya hədələmək üçün rəqəmsal alətlərdən istifadə",
        "преследование или угрозы с помощью цифровых средств",
    ),
    "an unfair difference between groups": (
        "qruplar arasında ədalətsiz fərq",
        "несправедливое неравенство между группами",
    ),
    "a fixed, oversimplified idea about a group of people": (
        "insan qrupu haqqında sabit, sadələşdirilmiş fikir",
        "упрощённый стереотип о группе людей",
    ),
    "unfair negative attitudes not based on real evidence": (
        "real sübutlara əsaslanmayan ədalətsiz mənfi münasibət",
        "несправедливый негатив без реальных оснований",
    ),
    "laws made by a government": (
        "hökumət tərəfindən qəbul edilən qanunlar",
        "законы, принятые правительством",
    ),
    "organized efforts to bring social or political change": (
        "ictimai və ya siyasi dəyişiklik üçün təşkilı səylər",
        "организованные усилия ради социальных или политических перемен",
    ),
    "the process of becoming part of a larger community": (
        "daha böyük icmanın bir hissəsinə çevrilmə prosesi",
        "процесс включения в более широкое сообщество",
    ),
    "treated as unimportant and pushed to the edge of society": (
        "cəmiyyətin kənarına itələnmiş və əhəmiyyətsiz sayılmış",
        "вынесенные на периферию общества и обесцененные",
    ),
    "being responsible for your actions and their results": (
        "hərəkətləriniz və nəticələri üçün məsuliyyət daşımaq",
        "ответственность за свои действия и их последствия",
    ),
    "a planned route or list of places and times for a trip": (
        "səfər üçün planlaşdırılmış marşrut və ya yer və vaxtlar siyahısı",
        "план маршрута и расписание поездки",
    ),
    "an object you buy to remember a place you visited": (
        "getdiyiniz yeri xatırlamaq üçün aldığınız əşya",
        "предмет, купленный на память о посещённом месте",
    ),
    "tiredness after flying across many time zones": (
        "bir neçə saat qurşağından uçuşdan sonra yorğunluq",
        "усталость после перелёта через несколько часовых поясов",
    ),
    "the place where your bags are checked when you enter a country": (
        "ölkəyə daxil olanda çantalarınızın yoxlandığı yer",
        "пункт досмотра багажа при въезде в страну",
    ),
    "inexpensive lodging, often with shared rooms": (
        "tez-tez paylaşılan otaqlar olan ucuz yaşayış",
        "недорогое жильё, часто с общими комнатами",
    ),
    "a famous building or natural feature that helps you navigate": (
        "naviqasiyaya kömək edən məşhur bina və ya təbiət obyekti",
        "известное здание или природный объект, помогающий ориентироваться",
    ),
    "a short trip for pleasure, often as part of a holiday": (
        "tez-tez tətilin bir hissəsi olan qısa zövq səfəri",
        "короткая поездка для удовольствия, часто в рамках отпуска",
    ),
    "too many visitors causing harm to a place": (
        "bir yerə zərər vuran çoxsaylı turistlər",
        "чрезмерный поток туристов, вредящий месту",
    ),
    "a plan for how you will spend or save money": (
        "pulunuzu necə xərcləyəcəyiniz və ya yığacağınız haqqında plan",
        "план расходов и сбережений",
    ),
    "money you have to pay for something": (
        "bir şey üçün ödəməli olduğunuz pul",
        "деньги, которые нужно заплатить за что-то",
    ),
    "something bought for less than the usual price": (
        "adətən qiymətindən ucuz alınan şey",
        "покупка дешевле обычной цены",
    ),
    "money given back when you return a product": (
        "məhsulu qaytardıqda qaytarılan pul",
        "возврат денег при возврате товара",
    ),
    "regular payment for a continuing service": (
        "davamlı xidmət üçün müntəzəm ödəniş",
        "регулярная плата за продолжающуюся услугу",
    ),
    "buying suddenly without careful thought": (
        "düşünmədən qəfil alış",
        "импульсивная покупка без обдумывания",
    ),
    "always choosing products from the same company": (
        "həmişə eyni şirkətin məhsullarını seçmək",
        "постоянный выбор продуктов одной и той же компании",
    ),
    "legal protections for people who buy goods or services": (
        "mallar və ya xidmətlər alan insanlar üçün hüquqi müdafiə",
        "правовая защита покупателей товаров и услуг",
    ),
    "something that causes a strong emotional reaction": (
        "güclü emosional reaksiya yaradan bir şey",
        "то, что вызывает сильную эмоциональную реакцию",
    ),
    "a healthy way you deal with stress or pain": (
        "stress və ya ağrı ilə mübarizədə sağlam üsul",
        "здоровый способ справляться со стрессом или болью",
    ),
    "understanding and sharing another person's feelings": (
        "başqa birinin hisslərini başa düşmək və paylaşmaq",
        "понимание и разделение чувств другого человека",
    ),
    "accepted rules for polite behavior in a society": (
        "cəmiyyətdə nəzakətli davranış üçün qəbul edilmiş qaydalar",
        "принятые нормы вежливого поведения в обществе",
    ),
    "the way your voice sounds, showing attitude or emotion": (
        "münasibət və ya emosiya göstərən səsinizin sədası",
        "тембр и интонация голоса, передающие отношение или эмоцию",
    ),
    "messages sent by posture, gestures, and facial expressions": (
        "durğu, jestlər və üz ifadələri ilə ötürülən mesajlar",
        "сигналы осанки, жестов и мимики",
    ),
    "long-lasting angry feelings after unfair treatment": (
        "ədalətsiz rəftardan sonra uzun müddət qalan qəzəb",
        "длительное чувство обиды после несправедливого обращения",
    ),
    "understanding your own emotions and habits": (
        "öz emosiyalarınızı və vərdişlərinizi başa düşmək",
        "понимание собственных эмоций и привычек",
    ),
    "harmful substances added to air, water, or soil": (
        "hava, su və ya torpağa əlavə edilən zərərli maddələr",
        "вредные вещества, попадающие в воздух, воду или почву",
    ),
    "energy from sources that are naturally replaced": (
        "təbii olaraq bərpa olunan mənbələrdən enerji",
        "энергия из возобновляемых природных источников",
    ),
    "total greenhouse gases caused by a person or activity": (
        "şəxs və ya fəaliyyətin törətdiyi ümumi istixana qazları",
        "совокупный выброс парниковых газов от человека или деятельности",
    ),
    "the variety of living species in an area": (
        "bir ərazidə yaşayan növlərin müxtəlifliyi",
        "разнообразие живых видов в регионе",
    ),
    "using resources in a way that protects the future": (
        "gələcəyi qoruyaraq resurslardan istifadə",
        "использование ресурсов с заботой о будущем",
    ),
    "a new idea, device, or method that improves something": (
        "bir şeyi təkmilləşdirən yeni fikir, cihaz və ya üsul",
        "новая идея, устройство или метод, улучшающие что-то",
    ),
    "ideas about what is morally right or wrong in research": (
        "tədqiqatda nəyin əxlaqi cəhətdən düzgün və ya yanlış olduğu haqqında fikirlər",
        "представления о морально допустимом в исследованиях",
    ),
    "a testable prediction in a scientific investigation": (
        "elmi araşdırmada yoxlanıla bilən proqnoz",
        "проверяемое предположение в научном исследовании",
    ),
    "the way parts are arranged in a picture, song, or text": (
        "şəkildə, mahnıda və ya mətnində hissələrin düzülüşü",
        "расположение частей в картине, музыке или тексте",
    ),
    "your personal explanation of the meaning of art": (
        "incəsənətin mənasını şəxsən izah etməyiniz",
        "ваше личное толкование смысла произведения",
    ),
    "a category such as comedy, thriller, or portrait": (
        "komediya, triller və ya portret kimi janr",
        "категория вроде комедии, триллера или портрета",
    ),
    "a public show of paintings, photos, or objects": (
        "rəsm, foto və ya əşyaların ictimai sərgisi",
        "публичная выставка картин, фото или предметов",
    ),
    "official control over what art or media may appear": (
        "hansı incəsənət və ya media görünə biləcəyinə rəsmi nəzarət",
        "официальный контроль над тем, какое искусство или медиа допускается",
    ),
    "traditions and objects passed down from past generations": (
        "əvvəlki nəsillərdən ötürülən ənənələr və əşyalar",
        "традиции и предметы, передаваемые из поколения в поколение",
    ),
    "related to beauty or taste in art and design": (
        "incəsənət və dizaynda gözəllik və ya zövq ilə bağlı",
        "связанное с красотой и вкусом в искусстве и дизайне",
    ),
    "something that gives you new creative ideas": (
        "sizə yeni yaradıcı fikirlər verən bir şey",
        "то, что вдохновляет на новые творческие идеи",
    ),
    "form a picture or idea in your mind": (
        "ağlınızda şəkil və ya fikir formalaşdırmaq",
        "представить образ или идею в уме",
    ),
    "a situation imagined to explore possibilities, not real": (
        "mümkünlükləri araşdırmaq üçün təsəvvür olunan, real olmayan vəziyyət",
        "воображаемая ситуация для обсуждения возможностей, не реальность",
    ),
    "decide which things are most important first": (
        "əvvəlcə hansı şeylərin ən vacib olduğuna qərar vermək",
        "решить, что важнее всего сделать в первую очередь",
    ),
    "accepting a disadvantage to gain an advantage": (
        "üstünlük qazanmaq üçün çatışmazlığı qəbul etmək",
        "принять минус ради получения плюса",
    ),
    "a result that follows from an action or choice": (
        "hərəkət və ya seçimin nəticəsi",
        "результат действия или выбора",
    ),
    "something you like more than other options": (
        "digər variantlardan daha çox bəyəndiyiniz şey",
        "то, что вы предпочитаете другим вариантам",
    ),
    "how likely something is to happen": (
        "bir şeyin baş verəcəyinin nə qədər ehtimal olduğu",
        "насколько вероятно, что что-то произойдёт",
    ),
    "reasons you give to support a decision": (
        "qərarı dəstəkləmək üçün gətirdiyiniz səbəblər",
        "аргументы в пользу принятого решения",
    ),
    "how often something happens": (
        "bir şeyin nə tez-tez baş verdiyi",
        "как часто что-то происходит",
    ),
    "how long something continues": (
        "bir şeyin nə qədər davam etdiyi",
        "как долго что-то длится",
    ),
    "the order in which events happen": (
        "hadisələrin baş verdiyi ardıcıllıq",
        "порядок, в котором происходят события",
    ),
    "things you do regularly in a fixed order": (
        "müəyyən ardıcıllıqla müntəzəm etdiyiniz işlər",
        "регулярные действия в установленном порядке",
    ),
    "a planned meeting at an agreed time": (
        "razılaşdırılmış vaxtda planlaşdırılmış görüş",
        "запланированная встреча в согласованное время",
    ),
    "arriving at the correct time, not late": (
        "gecikmədən düzgün vaxtda çatmaq",
        "приходить вовремя, без опоздания",
    ),
    "a region where the same standard time is used": (
        "eyni standart vaxtın istifadə olunduğu region",
        "регион с одинаковым стандартным временем",
    ),
    "the latest time by which something must be done": (
        "bir şeyin görülməli olduğu son vaxt",
        "крайний срок, к которому что-то должно быть сделано",
    ),
    "relating to the national government, not only one state": (
        "yalnız bir ştat deyil, milli hökumətlə bağlı",
        "относящееся к федеральному правительству, а не только к штату",
    ),
    "one of the major regions with its own local government": (
        "öz yerli hökuməti olan əsas regionlardan biri",
        "крупный регион с собственным местным правительством",
    ),
    "an official count of the population": (
        "əhalinin rəsmi sayımı",
        "официальный перепись населения",
    ),
    "roads, bridges, and systems a country relies on": (
        "ölkənin güvəndiyi yollar, körpülər və sistemlər",
        "дороги, мосты и системы, от которых зависит страна",
    ),
    "a large area with shared geographic or cultural features": (
        "ümumi coğrafi və ya mədəni xüsusiyyətləri olan geniş ərazi",
        "обширная зона с общими географическими или культурными чертами",
    ),
    "typical weather patterns in an area over many years": (
        "bir ərazidə illər boyu tipik hava şəraiti",
        "типичные погодные условия региона за длительный период",
    ),
    "the official line between two countries or states": (
        "iki ölkə və ya ştat arasındakı rəsmi sərhəd xətti",
        "официальная граница между странами или штатами",
    ),
    "a famous place that represents a city or country": (
        "şəhər və ya ölkəni təmsil edən məşhur yer",
        "известное место, символизирующее город или страну",
    ),
}
