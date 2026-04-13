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
        if count % 10 == 1 and count % 100 != 11:
            return f"{count} тема"
        elif 2 <= count % 10 <= 4 and not (12 <= count % 100 <= 14):
            return f"{count} темы"
        else:
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
        "Danışıq və ya yazı üçün mövzu seçin. Hər mövzunun səhifəsində sözlərin izahı, tədris üçün qısa "
        "qeydlər, faydalı ifadələr, nümunə cümlələr, müzakirə sualları və qısa yazı tapşırıqları var."
    ),
    "ru": (
        "Выберите тему для устной или письменной практики. На каждой странице темы вы найдёте "
        "словарь с объяснениями, советы по учёбе, полезные фразы, образцы предложений, "
        "вопросы для обсуждения и короткие письменные задания."
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
        "Sözlərin qısa izahı, tədris məsləhətləri və bölmə başlıqları saytın seçdiyiniz dilində göstərilir; "
        "ingilis dilindəki sözlər və dərsdə birbaşa işlənən nümunə cümlələr isə ingilis dilində saxlanılır."
    ),
    "ru": (
        "Пояснения к словам, учебные подсказки и заголовки разделов отображаются на языке сайта; "
        "английские слова и практические фразы для занятий остаются на английском языке."
    ),
}


def theme_keyword_gloss(title: str, lang: str) -> str:
    lang = _lang(lang)
    if lang == "en":
        return f'A key word connected to the theme "{title}".'
    if lang == "az":
        return f"«{title}» mövzusuna uyğun əsas açar söz."
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
        'Bu danışıq mövzusu «{title}» üzrə qurulub. Məqsəd yalnız bir-iki kəlməlik cavablarda qalmamaq, '
        "həmçinin sərbəst danışıq, müsahibə və ya təqdimat üçün yetərincə aydın və geniş cavablar hazırlamaqdır."
    ),
    "ru": (
        'Этот разговорный блок посвящён теме «{title}». Цель — не ограничиваться краткими ответами, '
        "а строить развёрнутые высказывания, которые можно использовать в беседе, на собеседовании или при презентации."
    ),
}

_OVERVIEW_P2 = {
    "en": (
        "Strong answers usually mix description (what happened), explanation (why it matters), "
        "and evaluation (what you think now). Try to use at least three new words from the list below."
    ),
    "az": (
        "Yaxşı cavablar adətən təsviri (nə baş verib), səbəb–nəticə izahını (niyə vacibdir) və şəxsi "
        "qiymətləndirməni (indi necə düşünürsünüz) birlikdə verir. Aşağıdakı siyahıdan ən azı üç yeni söz "
        "işlətməyə çalışın."
    ),
    "ru": (
        "Сильные ответы, как правило, сочетают в себе описание (что произошло), объяснение (почему это важно) "
        "и оценку (ваше нынешнее отношение к этому). Постарайтесь употребить не менее трёх новых слов из списка ниже."
    ),
}

_STUDY_TIP = {
    "en": (
        "In class, aim for clear structure: state one main idea, give one concrete example, "
        "then invite your partner to respond with a question."
    ),
    "az": (
        "Dərsdə aydın quruluş saxlayın: əvvəlcə bir əsas fikir söyləyin, sonra bir konkret nümunə gətirin, "
        "sonda isə həmsöhbətinizi cavab verməsi üçün sualla dəvət edin."
    ),
    "ru": (
        "На занятии придерживайтесь чёткой структуры: выскажите одну главную мысль, "
        "подкрепите её конкретным примером, а затем задайте собеседнику вопрос, чтобы услышать его мнение."
    ),
}

_CLUSTER_NOTES: dict[str, dict[str, str]] = {
    "grammar_time": {
        "en": "Pay special attention to time expressions and how they change verb forms.",
        "az": "Zamanı bildirən ifadələrə və onların felin zamanına təsir etməsinə xüsusi diqqət yetirin.",
        "ru": "Уделите особое внимание временны́м выражениям и тому, как они влияют на форму глагола.",
    },
    "hypothetical_drill": {
        "en": "Practice both quick reactions and slower, reasoned answers; examiners reward both.",
        "az": "Həm ani, qısa cavabları, həm də yavaş, düşünülmüş və əsaslandırılmış cavabları məşq edin; "
        "hər iki üslub da yüksək qiymətləndirilə bilər.",
        "ru": "Тренируйте как быстрые, спонтанные реакции, так и обдуманные, аргументированные ответы — экзаменаторы ценят оба стиля.",
    },
    "usa_geo": {
        "en": "Balance facts you have learned with careful language—hedge when you are not sure.",
        "az": "Öyrəndiyiniz faktları ehtiyatlı ifadələrlə çatdırın; əmin olmadığınız yerdə “bəlkə”, “güman ki” kimi "
        "yumşaldıcı sözlərdən istifadə edin.",
        "ru": "Подкрепляйте изученные факты осторожными формулировками — используйте смягчающие обороты там, где не уверены.",
    },
    "safety_disaster": {
        "en": "Use calm, precise vocabulary; avoid exaggeration unless you are telling a story.",
        "az": "Sakit, aydın sözlər seçin; hekayə danışmırsınızsa, hadisələri şişirtməyin.",
        "ru": "Используйте спокойную, точную лексику; избегайте преувеличений, если только не рассказываете историю.",
    },
    "media_tech": {
        "en": "Be ready to compare benefits and risks without relying only on slogans.",
        "az": "Faydaları və riskləri yalnız şüarlara söykənmədən, arqumentlərlə müqayisə edə bilməyə hazır olun.",
        "ru": "Будьте готовы взвешенно сравнивать плюсы и минусы, не ограничиваясь расхожими лозунгами.",
    },
    "money_consumer": {
        "en": "Numbers and examples make abstract money topics easier to follow.",
        "az": "Rəqəm və konkret nümunələr pul, xərcləmə kimi mövzuları daha aydın və başa düşülən edir.",
        "ru": "Конкретные цифры и примеры делают абстрактные денежные темы понятнее и убедительнее.",
    },
    "leisure_travel": {
        "en": "Sensory details (sights, sounds, routines) make travel stories memorable.",
        "az": "Gördükləriniz, eşitdikləriniz və gündəlik təfərrüat kimi hisslərə aid detallar səyahət hekayəsini "
        "yaddaqalan edir.",
        "ru": "Сенсорные детали — виды, звуки, привычный распорядок — делают рассказы о поездках живыми и запоминающимися.",
    },
    "family_social": {
        "en": "Respect privacy: share what you are comfortable discussing and invite others to do the same.",
        "az": "Şəxsi həyata hörmət edin: yalnız danışmağa hazır olduğunuz şeyləri paylaşın və qarşı tərəfə də eyni "
        "həssaslığı göstərməyə dəvət edin.",
        "ru": "Уважайте личные границы: говорите лишь о том, о чём готовы рассказывать, и предложите то же самое собеседнику.",
    },
    "work_study": {
        "en": "Link habits (revision, feedback) to outcomes (grades, confidence, career).",
        "az": "Təkrar, müəllim rəyi kimi vərdişləri qiymət, özgüvən və gələcək peşə ilə birbaşa əlaqələndirin.",
        "ru": "Связывайте учебные привычки (повторение, обратная связь) с конкретными результатами: оценками, уверенностью в себе, карьерными перспективами.",
    },
    "health": {
        "en": "Stay factual and kind; health topics can be sensitive for classmates.",
        "az": "Faktlara söykənin və nəzakətli olun; sağlamlıq mövzuları sinif yoldaşlarınız üçün həssas ola bilər.",
        "ru": "Опирайтесь на факты и будьте тактичны — темы здоровья могут оказаться болезненными для некоторых одноклассников.",
    },
    "society": {
        "en": "Acknowledge different viewpoints before you argue against them.",
        "az": "Etiraz etməzdən əvvəl digər baxış bucaqlarını qəbul etdiyinizi və başa düşdüyünüzü göstərin.",
        "ru": "Сначала покажите, что вы понимаете и признаёте другие точки зрения, и только потом приводите свои контраргументы.",
    },
    "environment_science": {
        "en": "Separate what is widely accepted from what is still debated.",
        "az": "Elm dünyasında artıq geniş qəbul edilən fikirləri hələ mübahisə mövzusu olanlardan ayırd edin.",
        "ru": "Чётко разграничивайте то, что признано наукой, и то, что по-прежнему остаётся предметом дискуссий.",
    },
    "arts_culture": {
        "en": 'Describe what you notice before you judge whether something is "good."',
        "az": "Əvvəlcə əsərdə və ya hadisədə nə gördüyünüzü təsvir edin, sonra onun “yaxşı” və ya “pis” "
        "olması haqqında qərar verin.",
        "ru": "Сначала опишите, что вы замечаете в произведении, и лишь затем выносите суждение о том, «хорошо» это или нет.",
    },
    "emotion_behavior": {
        "en": "Name emotions precisely; it helps listeners understand you.",
        "az": "Hisslərinizi dəqiq adlarla ifadə edin; bu, sizi dinləyənlərin sizi daha yaxşı anlamasına kömək edir.",
        "ru": "Называйте эмоции точно и конкретно — так слушателям гораздо легче вас понять.",
    },
    "general": {
        "en": "Almost any topic can connect to values, habits, and future plans—use those bridges.",
        "az": "Demək olar ki, hər mövzunu dəyərləriniz, gündəlik vərdişləriniz və gələcək planlarınızla əlaqələndirmək "
        "olar; bu əlaqələrdən istifadə edin.",
        "ru": "Почти любую тему можно связать с личными ценностями, повседневными привычками и планами на будущее — используйте эти мостики в разговоре.",
    },
}


# English gloss (msgid) -> (Azerbaijani, Russian)
_GLOSSES: dict[str, tuple[str, str]] = {
    "make something easier to understand by explaining it": (
        "bir şeyi izah etməklə daha aydın və başa düşülən etmək",
        "сделать что-то понятнее, объяснив подробнее",
    ),
    "add more detail to what you are saying": (
        "söylədiklərinizə əlavə təfərrüat və ya izah vermək",
        "добавить подробности к тому, что вы говорите",
    ),
    "a personal opinion or way of seeing a topic": (
        "mövzuya şəxsi münasibət və ya baxış bucağı",
        "личная точка зрения или способ смотреть на тему",
    ),
    "something you accept as true without proof": (
        "sübutu olmadan doğru hesab etdiyiniz qəbul",
        "то, что вы принимаете за истину без доказательств",
    ),
    "a small, subtle difference in meaning or feeling": (
        "mənada və ya duyğuda nazik, kiçik fərq",
        "тонкое смысловое или эмоциональное различие",
    ),
    "using careful language so you do not sound too absolute": (
        "çox birmənalı və kategorik səslənməmək üçün ehtiyatlı ifadələr seçmək",
        "выбор осторожных формулировок, чтобы не звучать категорично",
    ),
    "a reason against an idea you have mentioned": (
        "demək istədiyiniz fikrə qarşı çıxan arqument",
        "контраргумент против упомянутой вами идеи",
    ),
    "a short personal story used to illustrate a point": (
        "fikrinizi nümayiş etdirmək üçün danışdığınız qısa şəxsi hadisə",
        "короткий личный рассказ, иллюстрирующий мысль",
    ),
    "closely connected to the subject you are discussing": (
        "müzakirə etdiyiniz mövzuya birbaşa bağlı olan",
        "непосредственно связанное с обсуждаемой темой",
    ),
    "something that you have lived through": (
        "özünüzün şəxsən yaşadığı təcrübə",
        "то, через что вы сами прошли",
    ),
    "what you think about a topic, not necessarily a fact": (
        "mövzu barədə şəxsi fikriniz; həmişə obyektiv fakt olmaya bilər",
        "ваше мнение по теме — не обязательно объективный факт",
    ),
    "earlier events or context that help explain a situation": (
        "cari vəziyyəti başa düşdürmək üçün əvvəlki hadisələr və ümumi məzmun (kontekst)",
        "предшествующие события или контекст, помогающие объяснить ситуацию",
    ),
    "look at two things to see how they are similar or different": (
        "iki şeyi yan-yana qoyub oxşar və fərqli cəhətlərini müqayisə etmək",
        "сопоставить два предмета, чтобы найти сходства и различия",
    ),
    "focus on differences between two things": (
        "iki şey arasındakı fərqləri əsas məqsəd kimi göstərmək",
        "сосредоточиться на различиях между двумя вещами",
    ),
    "give the main ideas in a short form": (
        "əsas fikirləri qısa və ümumiləşdirilmiş şəkildə çatdırmaq",
        "кратко изложить главные идеи",
    ),
    "a tendency to prefer one side or view unfairly": (
        "bir tərəfə və ya fikrə haqsız şəkildə üstünlük vermə meyli",
        "предвзятая склонность к одной стороне или точке зрения",
    ),
    "help or encouragement you give to someone": (
        "kiməsə göstərdiyiniz mənəvi və ya praktik dəstək",
        "помощь или поддержка, которую вы оказываете кому-то",
    ),
    "limits about what behavior you accept from others": (
        "başqalarının sizə qarşı hansı davranışını qəbul etdiyinizi göstərən sərhəd",
        "границы допустимого поведения других людей по отношению к вам",
    ),
    "beliefs about what should happen or how people should act": (
        "nələrin baş verməli və ya insanların necə davranmalı olduğuna dair gözlənti",
        "представления о том, что должно происходить и как следует себя вести",
    ),
    "an agreement where each side gives up something": (
        "hər tərəfin müəyyən güzəştə getdiyi razılaşma",
        "соглашение, в котором каждая сторона на что-то идёт ради другой",
    ),
    "belief that someone is honest and reliable": (
        "birinin dürüst və sözünün üstündə duran adam olduğuna olan inam",
        "уверенность в том, что человек честен и надёжен",
    ),
    "serious disagreement or argument": (
        "dərin fikir ayrılığı və ya kəskin mübahisə",
        "серьёзное разногласие или острый спор",
    ),
    "all the people living together in one home": (
        "eyni evdə birlikdə yaşayan ailə üzvləri və ya ev təsərrüfatı",
        "все люди, живущие вместе в одном доме",
    ),
    "the way you were cared for and taught as a child": (
        "uşaq yaşlarında sizə necə qayğı göstərildiyi və nə öyrədildiyi",
        "то, как вас воспитывали и чему учили в детстве",
    ),
    "a certificate, degree, or skill that proves ability": (
        "bacarığınızı təsdiqləyən sənəd, dərəcə və ya praktiki vəsait",
        "диплом, сертификат или навык, подтверждающие вашу компетентность",
    ),
    "the latest time something must be finished": (
        "işin və ya tapşırığın son icra müddəti",
        "крайний срок, к которому что-то должно быть завершено",
    ),
    "comments about how well you did and how to improve": (
        "gördüyünüz iş haqqında rəy və təkmilləşmə üçün məsləhət",
        "отзыв о том, как вы справились, и советы по улучшению",
    ),
    "the full set of subjects or topics in a course": (
        "kursda keçilən bütün fənlər və ya dərs mövzuları",
        "полный перечень предметов или тем учебного курса",
    ),
    "a person of the same age or level as you in school or work": (
        "məktəbdə və ya işdə sizinlə eyni yaşda və ya oxşar səviyyədə olan həmkar",
        "человек того же возраста или уровня в учёбе или работе",
    ),
    "using someone else's work as if it were your own": (
        "başqasının əməyini özünüzmüş kimi təqdim etmək",
        "выдавать чужую работу за свою собственную",
    ),
    "studying material again before a test": (
        "imtahan və ya yoxlama öncəsi materialı təkrarlamaq",
        "повторение пройденного материала перед экзаменом",
    ),
    "a short period of training work, often for students": (
        "adətən tələbələr üçün təyin olunan qısa müddətli təcrübə (staj)",
        "короткий период практики или стажировки, как правило для студентов",
    ),
    "a sign that you might be ill or stressed": (
        "xəstəlik və ya gərginlik ola biləcəyinizi düşündürən əlamət",
        "признак возможной болезни или стресса",
    ),
    "actions that stop a problem before it starts": (
        "problem yaranmazdan əvvəl onun qarşısını alan tədbirlər",
        "меры, предотвращающие проблему до её возникновения",
    ),
    "your general state of health and happiness": (
        "fiziki sağlamlıq və ümumi əhval-ruhiyyənizin vəziyyəti",
        "общее состояние здоровья и самочувствия",
    ),
    "continuing for a long time, not just once": (
        "təkcə bir dəfəlik deyil, uzun müddət davam edən",
        "продолжающееся долгое время, а не разовое",
    ),
    "the process of getting better after illness or injury": (
        "xəstəlik və ya bədən xəsarətindən sonra sağalma və bərpa mərhələsi",
        "процесс восстановления после болезни или травмы",
    ),
    "the food you eat and how it affects your body": (
        "qəbul etdiyiniz qida və onun orqanizmə təsiri",
        "питание и его влияние на ваш организм",
    ),
    "involving a lot of sitting and little physical activity": (
        "çox oturmaq, az hərəkət və fiziki fəaliyyət deməkdir",
        "предполагающий много сидения и мало физической активности",
    ),
    "ability to recover from difficulties": (
        "çətinliklərdən sonra yenidən ayağa qalma və uyğunlaşma bacarığı",
        "способность восстанавливаться после трудностей и невзгод",
    ),
    "something that can cause harm or danger": (
        "zərər və ya təhlükə törədə bilən amil",
        "то, что способно причинить вред или создать опасность",
    ),
    "organized movement of people away from danger": (
        "təhlükəli zonadan insanların təşkilatlı şəkildə təxliyyəsi",
        "организованное перемещение людей прочь от опасности",
    ),
    "simple medical care given immediately after an injury": (
        "xəsarətdən dərhal sonra göstərilən ilkin və sadə tibbi yardım",
        "первая медицинская помощь, оказываемая сразу после травмы",
    ),
    "an agreement that pays money if you have a loss": (
        "zərər baş verdikdə ödəniş vəd edən sığorta müqaviləsi",
        "договор, по которому выплачивается возмещение при наступлении ущерба",
    ),
    "basic supplies kept ready for a crisis": (
        "fövqəladə hallar üçün əvvəlcədən saxlanılan əsas ləvazimatlar",
        "базовый набор предметов первой необходимости на случай кризиса",
    ),
    "a smaller earthquake following a larger one": (
        "güclü zəlzələdən sonra qeydə alınan daha zəif təkanlar",
        "более слабое землетрясение после сильного",
    ),
    "a safe place that protects you from weather or danger": (
        "hava şəraitindən və ya təhlükədən mühafizə verən təhlükəsiz sığınacaq",
        "безопасное место, защищающее от погоды или опасности",
    ),
    "steps that reduce the seriousness of a future risk": (
        "gələcəkdə ehtimal olunan riskin təsirini azaldan addımlar",
        "меры, снижающие тяжесть будущего риска",
    ),
    "a set of rules a computer uses to sort or show content": (
        "kompüterin məzmunu necə sıralayacağını və ya göstərəcəyini müəyyən edən qaydalar dəsti",
        "набор правил, по которым компьютер сортирует или отображает контент",
    ),
    "control over who sees your personal information": (
        "şəxsi məlumatlarınızı kimin görə biləcəyinə nəzarət",
        "контроль над тем, кто имеет доступ к вашим личным данным",
    ),
    "false information spread without intending to lie": (
        "yalan danışmaq niyyəti olmadan yayılan səhv məlumat",
        "недостоверная информация, распространяемая без умысла обмануть",
    ),
    "false information spread on purpose to mislead": (
        "insanları qəsdən yanlış istiqamətə yönəltmək üçün yayılan yalan məlumat",
        "заведомо ложная информация, намеренно распространяемая с целью ввести в заблуждение",
    ),
    "an alert on your phone or computer": (
        "telefon və ya kompüterdə gələn xəbərdarlıq bildirişi",
        "оповещение на телефоне или компьютере",
    ),
    "hours spent using phones, TVs, or computers": (
        "telefon, televizor və ya kompüterlə keçirilən vaxt",
        "время, проведённое за телефоном, телевизором или компьютером",
    ),
    "the record of your activity left online": (
        "internetdə sizin fəaliyyətiniz barədə qalan iz və ya tarixçə",
        "след вашей активности, оставленный в интернете",
    ),
    "using digital tools to harass or threaten someone": (
        "rəqəmsal vasitələrlə kimisə təqib etmək və ya hədələmək",
        "использование цифровых средств для преследования или запугивания кого-либо",
    ),
    "an unfair difference between groups": (
        "qruplar arasında ədalətsiz ayrı-seçkilik və ya bərabərsizlik",
        "несправедливое неравенство между группами людей",
    ),
    "a fixed, oversimplified idea about a group of people": (
        "insan qrupu haqqında həqiqəti əks etdirməyən sadələşdirilmiş stereotip",
        "устойчивое упрощённое представление о группе людей",
    ),
    "unfair negative attitudes not based on real evidence": (
        "real faktlara söykənməyən, ədalətsiz mənfi münasibət",
        "предвзятое негативное отношение, не основанное на реальных фактах",
    ),
    "laws made by a government": (
        "dövlət orqanları tərəfindən qəbul edilmiş normativ aktlar",
        "законы, принятые государственными органами",
    ),
    "organized efforts to bring social or political change": (
        "ictimai və ya siyasi dəyişiklik üçün planlı və təşkil olunmuş fəaliyyət",
        "организованные действия ради социальных или политических преобразований",
    ),
    "the process of becoming part of a larger community": (
        "daha geniş cəmiyyətin tamhüquqlu üzvünə çevrilmə prosesi",
        "процесс вхождения в более широкое сообщество",
    ),
    "treated as unimportant and pushed to the edge of society": (
        "cəmiyyətin mərkəzindən kənara itələnmiş və əhəmiyyətsiz sayılmış kimi hiss etdirilən",
        "оттеснённые на обочину общества и лишённые голоса",
    ),
    "being responsible for your actions and their results": (
        "öz hərəkətlərinizin və onların nəticəsinin məsuliyyətini üzərinizə götürmək",
        "готовность нести ответственность за свои поступки и их последствия",
    ),
    "a planned route or list of places and times for a trip": (
        "səfərin marşrutu və gediləcək yerlərin vaxt cədvəli",
        "заранее составленный маршрут и расписание поездки",
    ),
    "an object you buy to remember a place you visited": (
        "ziyarət etdiyiniz yeri xatırlatmaq üçün aldığınız xatirə əşyası",
        "сувенир, купленный на память о посещённом месте",
    ),
    "tiredness after flying across many time zones": (
        "bir neçə saat qurşağını dəyişən uçuşdan sonra yaranan yorğunluq",
        "усталость от перелёта через несколько часовых поясов",
    ),
    "the place where your bags are checked when you enter a country": (
        "ölkəyə girişdə baqajınızın gömrük yoxlamasından keçdiyi məntəqə",
        "пункт таможенного досмотра багажа при въезде в страну",
    ),
    "inexpensive lodging, often with shared rooms": (
        "adətən otağı başqaları ilə paylaşdığınız münasib qiymətli yaşayış yeri",
        "недорогое жильё, нередко с общими комнатами",
    ),
    "a famous building or natural feature that helps you navigate": (
        "orientasiya üçün istifadə etdiyiniz məşhur bina və ya təbiət nişanı",
        "известное здание или природный объект, служащий ориентиром",
    ),
    "a short trip for pleasure, often as part of a holiday": (
        "adətən tətil planının içində olan qısa məsafəli ekskursiya",
        "небольшая поездка для удовольствия, часто в рамках отпуска",
    ),
    "too many visitors causing harm to a place": (
        "həddindən artıq turist axını nəticəsində yerə və mühitə zərər",
        "избыточный поток туристов, наносящий ущерб месту",
    ),
    "a plan for how you will spend or save money": (
        "gəlirinizi necə xərcləyəcəyiniz və ya qənaət edəcəyinizə dair plan",
        "план распределения доходов: на что тратить и что откладывать",
    ),
    "money you have to pay for something": (
        "bir xidmət və ya məhsul üçün ödəməli olduğunuz məbləğ",
        "сумма, которую необходимо заплатить за что-либо",
    ),
    "something bought for less than the usual price": (
        "adətən satılan qiymətdən ucuz başa gələn alış",
        "покупка по цене ниже обычной",
    ),
    "money given back when you return a product": (
        "məhsulu qaytardığınız halda geri ödənilən məbləğ",
        "возврат денег при возврате товара",
    ),
    "regular payment for a continuing service": (
        "davamlı göstərilən xidmətə görə aylıq və ya dövri ödəniş",
        "регулярная плата за пользование продолжающейся услугой",
    ),
    "buying suddenly without careful thought": (
        "əvvəlcədən düşünmədən qəfil edilən alış-veriş",
        "импульсивная покупка без предварительного обдумывания",
    ),
    "always choosing products from the same company": (
        "həmişə eyni brend və ya şirkətin məhsullarını üstün tutmaq",
        "постоянное предпочтение продуктов одной и той же компании",
    ),
    "legal protections for people who buy goods or services": (
        "alıcıların hüquqlarını qoruyan qanuni təminat",
        "правовая защита покупателей товаров и услуг",
    ),
    "something that causes a strong emotional reaction": (
        "güclü emosiya və ya reaksiya doğuran təkanverici amil",
        "то, что вызывает сильный эмоциональный отклик",
    ),
    "a healthy way you deal with stress or pain": (
        "stress və ya ağrı ilə sağlam və təhlükəsiz üsulla başa çıxmaq",
        "здоровый способ справляться со стрессом или душевной болью",
    ),
    "understanding and sharing another person's feelings": (
        "başqasının hisslərini dərk etmək və özünüzü onun yerinə qoymaq",
        "способность понимать и разделять чувства другого человека",
    ),
    "accepted rules for polite behavior in a society": (
        "ictimai mühitdə qəbul olunmuş nəzakət və davranış normaları",
        "общепринятые нормы вежливого поведения в обществе",
    ),
    "the way your voice sounds, showing attitude or emotion": (
        "səsinizin tonu və intoniyası ilə ifadə etdiyiniz münasibət və ya hiss",
        "звучание вашего голоса, выражающее отношение или эмоцию",
    ),
    "messages sent by posture, gestures, and facial expressions": (
        "durğu, əl hərəkətləri və mimika ilə ötürülən qarşılıqlı siqnallar",
        "сигналы, передаваемые позой, жестами и мимикой",
    ),
    "long-lasting angry feelings after unfair treatment": (
        "ədalətsiz rəftardan sonra uzun müddət çəkən inciklik və ya qəzəb",
        "длительная обида или гнев, вызванные несправедливым обращением",
    ),
    "understanding your own emotions and habits": (
        "öz daxili dünyanızı, emosiyalarınızı və davranış vərdişlərinizi tanımaq",
        "осознание собственных эмоций и поведенческих привычек",
    ),
    "harmful substances added to air, water, or soil": (
        "hava, su və ya torpağa düşən zərərli maddələr",
        "вредные вещества, попадающие в воздух, воду или почву",
    ),
    "energy from sources that are naturally replaced": (
        "təbii yolla yenilənən mənbələrdən əldə olunan enerji",
        "энергия, получаемая из природно восполняемых источников",
    ),
    "total greenhouse gases caused by a person or activity": (
        "fərdi və ya fəaliyyət nəticəsində atmosferə buraxılan istixana qazlarının ümumi həcmi",
        "суммарный выброс парниковых газов от человека или деятельности",
    ),
    "the variety of living species in an area": (
        "müəyyən ərazidə yaşayan canlı növlərinin müxtəlifliyi",
        "разнообразие живых видов на определённой территории",
    ),
    "using resources in a way that protects the future": (
        "təbii ehtiyatlardan gələcək nəsillər üçün zərər vermədən istifadə",
        "использование ресурсов так, чтобы не навредить будущим поколениям",
    ),
    "a new idea, device, or method that improves something": (
        "mövcud vəziyyəti yaxşılaşdıran yeni texniki həll və ya üsul",
        "новая идея, устройство или метод, улучшающие что-либо",
    ),
    "ideas about what is morally right or wrong in research": (
        "elmi tədqiqatda nəyin əxlaqi cəhətdən qəbul edilə bilən olduğu barədə baxış",
        "представления о том, что допустимо и недопустимо в научных исследованиях",
    ),
    "a testable prediction in a scientific investigation": (
        "təcrübə və ya müşahidə ilə yoxlana bilən elmi fərziyyə",
        "проверяемое предположение в рамках научного исследования",
    ),
    "the way parts are arranged in a picture, song, or text": (
        "əsərdə, mahnıda və ya mətnində hissələrin kompozisiya üzrə düzülüşü",
        "композиционное расположение частей в картине, музыке или тексте",
    ),
    "your personal explanation of the meaning of art": (
        "yaradıcılıq nümunəsinin sizin üçün daşıdığı mənanı şərh etmək",
        "ваше собственное толкование смысла художественного произведения",
    ),
    "a category such as comedy, thriller, or portrait": (
        "komediya, triller, portret kimi janr və ya alt janr",
        "жанровая категория: например, комедия, триллер или портрет",
    ),
    "a public show of paintings, photos, or objects": (
        "rəsm əsərlərinin, foto və ya eksponatların ictimai nümayişi",
        "публичная выставка картин, фотографий или предметов",
    ),
    "official control over what art or media may appear": (
        "hansı bədii və ya media məzmununun ictimaiyyətə açıq ola biləcəyinə dövlət nəzarəti",
        "государственный контроль над тем, какое искусство или медиаконтент допускается к показу",
    ),
    "traditions and objects passed down from past generations": (
        "nəsillərdən-nəsillərə ötürülən mədəni irs və maddi nişanələr",
        "традиции и предметы, переходящие от поколения к поколению",
    ),
    "related to beauty or taste in art and design": (
        "incəsənət və dizaynda estetik zövq və gözəllik anlayışı ilə bağlı",
        "связанное с красотой и художественным вкусом в искусстве и дизайне",
    ),
    "something that gives you new creative ideas": (
        "yaradıcı düşüncənizi stimullaşdıran ilham mənbəyi",
        "то, что даёт толчок новым творческим идеям",
    ),
    "form a picture or idea in your mind": (
        "zəhninizdə canlı təsəvvür və ya mental obraz yaratmaq",
        "мысленно представить образ или идею",
    ),
    "a situation imagined to explore possibilities, not real": (
        "real həyatda olmayan, yalnız mümkün ssenariləri müzakirə üçün qurulan vəziyyət",
        "воображаемая ситуация для исследования возможностей, не реальность",
    ),
    "decide which things are most important first": (
        "vaciblik dərəcəsinə görə prioritetləri müəyyənləşdirmək",
        "определить, что важнее всего, и заняться этим в первую очередь",
    ),
    "accepting a disadvantage to gain an advantage": (
        "daha böyük fayda əldə etmək üçün müəyyən güzəştə getmək",
        "согласиться на издержки ради получения выгоды",
    ),
    "a result that follows from an action or choice": (
        "hərəkət və ya seçimin birbaşa nəticəsi və ya təsiri",
        "следствие, вытекающее из действия или решения",
    ),
    "something you like more than other options": (
        "digər alternativlərə nisbətən üstün tutduğunuz seçim",
        "то, что вы предпочитаете другим вариантам",
    ),
    "how likely something is to happen": (
        "hadisənin baş vermə ehtimalının yüksək və ya aşağı olması",
        "степень вероятности того, что что-то произойдёт",
    ),
    "reasons you give to support a decision": (
        "verdiyiniz qərarı əsaslandıran arqumentlər və sübutlar",
        "доводы, которые вы приводите в поддержку своего решения",
    ),
    "how often something happens": (
        "hadisənin müəyyən zaman kəsiyində nə tez-tez təkrarlandığı",
        "то, как часто что-то происходит",
    ),
    "how long something continues": (
        "prosesin və ya vəziyyətin nə qədər müddət davam etdiyi",
        "то, как долго что-то продолжается",
    ),
    "the order in which events happen": (
        "hadisələrin bir-birini əvəz etmə ardıcıllığı",
        "последовательность, в которой происходят события",
    ),
    "things you do regularly in a fixed order": (
        "hər gün və ya həftə eyni ardıcıllıqla təkrarlanan gündəlik işlər",
        "действия, выполняемые регулярно в одном и том же порядке",
    ),
    "a planned meeting at an agreed time": (
        "əvvəlcədən razılaşdırılmış vaxtda görüşmək",
        "заранее намеченная встреча в согласованное время",
    ),
    "arriving at the correct time, not late": (
        "müəyyən edilmiş vaxtda, gecikmədən yetişmək",
        "приходить вовремя, не опаздывая",
    ),
    "a region where the same standard time is used": (
        "eyni rəsmi yerli vaxtın tətbiq olunduğu coğrafi zona",
        "территория, на которой действует единое поясное время",
    ),
    "the latest time by which something must be done": (
        "tapşırığın və ya işin son icra tarixi",
        "крайний срок, к которому что-то должно быть сделано",
    ),
    "relating to the national government, not only one state": (
        "tək ştat yox, bütövlükdə ölkənin mərkəzi idarəetmə orqanlarına aid olan",
        "относящееся к федеральному правительству страны, а не к отдельному штату",
    ),
    "one of the major regions with its own local government": (
        "öz yerli özünüidarə orqanları olan iri inzibati ərazi vahidi",
        "крупный регион со своими органами местного самоуправления",
    ),
    "an official count of the population": (
        "əhalinin dövlət tərəfindən aparılan rəsmi siyahıyaalınması",
        "официальная перепись населения",
    ),
    "roads, bridges, and systems a country relies on": (
        "ölkənin dayanıqlı inkişafı üçün zəruri olan yol, nəqliyyat və kommunikasiya infrastrukturu",
        "дороги, мосты и системы жизнеобеспечения, от которых зависит страна",
    ),
    "a large area with shared geographic or cultural features": (
        "ümumi təbii və ya mədəni xüsusiyyətləri bölüşən geniş coğrafi region",
        "обширная территория с общими географическими или культурными чертами",
    ),
    "typical weather patterns in an area over many years": (
        "müəyyən ərazidə uzun illər ərzində müşahidə olunan iqlim tipi və hava rejimi",
        "характерные погодные условия для данного региона, сложившиеся за многие годы",
    ),
    "the official line between two countries or states": (
        "iki dövlət və ya inzibati vahid arasındakı beynəlxalq və ya daxili sərhəd xətti",
        "официальная граница между двумя странами или штатами",
    ),
    "a famous place that represents a city or country": (
        "şəhər və ya ölkənin simvoluna çevrilmiş məşhur məkan",
        "известное место, ставшее символом города или страны",
    ),
}