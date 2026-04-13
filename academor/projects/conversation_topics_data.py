"""Static English conversation-practice content for speaking-class themes.

English terms and practice lines stay in English; glosses and study notes are
localized via ``conversation_topics_locale`` (Azerbaijani / Russian).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from django.utils.text import slugify
from unidecode import unidecode

from projects import conversation_topics_locale as _ct_loc


@dataclass(frozen=True)
class TopicVocab:
    term: str
    gloss: str


@dataclass(frozen=True)
class ConversationTopic:
    title: str
    slug: str
    overview_paragraphs: tuple[str, ...]
    vocabulary: tuple[TopicVocab, ...]
    useful_phrases: tuple[str, ...]
    example_sentences: tuple[str, ...]
    discussion_questions: tuple[str, ...]
    writing_prompts: tuple[str, ...]


# --- Topic titles from curriculum list (deduplicated; section labels omitted) ---

RAW_TOPIC_TITLES: tuple[str, ...] = (
    "Accidents at Home",
    "Adoption",
    "Advertising",
    "Advice",
    "Age: Youth & Old Age",
    "Airplanes",
    "Amusement Parks",
    "Anger",
    "Animals & Pets",
    "Annoying Things",
    "Arguing",
    "Art",
    "The Art of Conversation",
    "Bags and Purses",
    "Baseball",
    "Basketball",
    "Beach",
    "Beauty & Physical Attractiveness",
    "Behavior",
    "Birthdays",
    "Body Language",
    "Books & Reading",
    "Bullfighting",
    "Business",
    "Cars & Driving",
    "Celebrities",
    "Change",
    "Charity",
    "Cheating",
    "Childbirth",
    "Childhood",
    "Children",
    "Chores",
    "Cities",
    "Classrooms",
    "Cloning",
    "Clothes & Fashion",
    "College",
    "Colors / Colours",
    "Comics",
    "Community",
    "Commuting",
    "Complaining",
    "Computers",
    "Conflict",
    "Corruption",
    "Countries",
    "Creativity",
    "Crime",
    "Culture",
    "Cultural Shock & Adapting to Canada",
    "Dangers",
    "Dating",
    "Death & Dying",
    "Diets",
    "Disabilities & Handicaps",
    "Disaster",
    "Disaster Preparation",
    "Discrimination",
    "Dogs & Cats",
    "Do You Wish...?",
    "Dreams",
    "Drugs",
    "Earthquakes",
    "Easter",
    "Education",
    "Encouragement",
    "English Literature & Books",
    "English study",
    "Entertainment",
    "Environment & Pollution",
    "Everyday Questions",
    "Eye Contact",
    "Facebook",
    "Fads & Trends",
    "Faith & Faithlessness",
    "Family",
    "Family & Alternative Lifestyles",
    "Famous People",
    "Fashion",
    "Favorites",
    "Fears",
    "Feelings",
    "Films in Your own Language",
    "Fire Safety",
    "First Dates",
    "Food & Eating",
    "Free Time & Hobbies",
    "Friends",
    "Fruits & Vegetables",
    "Future",
    "Gambling",
    "Garage sale",
    "Gardening",
    "Gay Community",
    "Gender Roles",
    "Generation Gap",
    "Gestures",
    "Getting to Know Each Other",
    "Gifts",
    "Goals",
    "Going to a Party",
    "Gossip & Rumors",
    "Habits",
    "Happiness",
    "Have You Ever ...",
    "Health",
    "Healthy Lifestyle",
    "Hobbies",
    "Holidays",
    "April Fool's Day",
    "Christmas",
    "Halloween",
    "Saint Patrick's Day",
    "Thanksgiving",
    "After a Vacation",
    "Valentine's Day",
    "Home",
    "Homeless",
    "Hometowns",
    "Homework",
    "Honesty & Truthfulness",
    "How Long...?",
    "How often do you...?",
    "Humor",
    "If You Were...?",
    "Immigration",
    "Internet",
    "Inventions",
    "Job Interview",
    "Jobs & Occupations",
    "Jokes",
    "Languages",
    "Leaders & Leadership",
    "Learning a Foreign Language",
    "My Life so Far",
    "Likes & Dislikes",
    "Living Arrangements & Dream House",
    "Love, Dating & Marriage",
    "Machines",
    "Makeup, Lotions & Skin Care",
    "Manners",
    "Marriage",
    "Martial Arts",
    "Meaning of Life & Reasons for Living",
    "Meeting People",
    "Memory",
    "Midlife Crisis",
    "Mind, Body & Health",
    "Money & Shopping",
    "Motivation",
    "Movie Industry",
    "Movies",
    "Moving to Another Country",
    "Music",
    "Names",
    "Neighbor Complaints",
    "Neighborhood",
    "News",
    "New Media",
    "New Year's Day",
    "New Year's Resolutions",
    "Dreams, Daydreams & Nightmares",
    "Olympics",
    "Body",
    "Painting",
    "Parenting",
    "Planning a Party",
    "Personality",
    "Photography",
    "Plagiarism",
    "Plans",
    "Police",
    "Politics",
    "Pope John II",
    "Possessions",
    "Poverty",
    "Prejudices",
    "Privacy",
    "Procrastination",
    "Race",
    "Religion",
    "House Renovation",
    "Restaurants & Eating Out",
    "Nursing Homes & Retirement Communities",
    "Retirement",
    "Russia & the World",
    "Safety Inside & Outside of Home",
    "School",
    "Science & Technology",
    "Secrets",
    "Self-employment",
    "Service Industry",
    "Silly Questions",
    "Single Life",
    "Sleep",
    "Smoking",
    "Social Problems",
    "Social Networking",
    "Sports",
    "Standardized Exams",
    "Stereotypes",
    "Stress",
    "Super Heroes in Comics",
    "Supernatural, Ghosts & Superstitions",
    "Talk About Four Things",
    "Talk About Three Things",
    "Teachers",
    "Teenagers",
    "Telepathy",
    "Telephones",
    "Television",
    "Tell me about...?",
    "Terror",
    "Texting",
    "Time",
    "Tipping",
    "Trade Fairs, County Fairs & Industrial Exhibitions",
    "Traffic Accidents",
    "Transportation",
    "Trauma",
    "Travel",
    "Tsunami",
    "Talk About Two Things",
    "Unemployment",
    "The Unexplained",
    "United States",
    "University",
    "Moving to the United States",
    "About the United States",
    "United States Geography",
    "United States Leadership",
    "Vegetarian",
    "Volunteer Work",
    "War",
    "Weather",
    "Weddings",
    "Weekends",
    "What if...?",
    "What would you...?",
    "When did you first...?",
    "When was the last...?",
    "White Lies",
    "Who is the greatest...?",
    "Wishes",
    "World Peace",
    "Would you ever...?",
    "Would you rather...?",
    "Drills",
    "Are You Good At ...?",
    "Days of the Week",
    "How do you...?",
    "Months of the Year",
)


def _slug_base(title: str) -> str:
    cleaned = re.sub(r"[/]", " ", title)
    return slugify(unidecode(cleaned)) or "topic"


def _unique_slugs(titles: Iterable[str]) -> dict[str, str]:
    bases = [_slug_base(t) for t in titles]
    per_base: dict[str, int] = {}
    out: dict[str, str] = {}
    for title, base in zip(titles, bases):
        n = per_base.get(base, 0)
        if n == 0:
            out[title] = base
        else:
            out[title] = f"{base}-{n + 1}"
        per_base[base] = n + 1
    return out


TITLE_TO_SLUG: dict[str, str] = _unique_slugs(RAW_TOPIC_TITLES)


# --- Shared vocabulary banks (term, gloss) ---

_ACADEMIC_SPEAKING: tuple[tuple[str, str], ...] = (
    ("clarify", "make something easier to understand by explaining it"),
    ("elaborate", "add more detail to what you are saying"),
    ("point of view", "a personal opinion or way of seeing a topic"),
    ("assumption", "something you accept as true without proof"),
    ("nuance", "a small, subtle difference in meaning or feeling"),
    ("hedging", "using careful language so you do not sound too absolute"),
    ("counterargument", "a reason against an idea you have mentioned"),
    ("anecdote", "a short personal story used to illustrate a point"),
)


_THEME_GLOSS_MARKER = "__THEME_KEYWORD__"

# (English term, English gloss) — gloss translated at build time via _ct_loc.gloss
CLUSTER_VOCAB: dict[str, tuple[tuple[str, str], ...]] = {
    "general": (
        ("relevant", "closely connected to the subject you are discussing"),
        ("experience", "something that you have lived through"),
        ("opinion", "what you think about a topic, not necessarily a fact"),
        ("background", "earlier events or context that help explain a situation"),
        ("compare", "look at two things to see how they are similar or different"),
        ("contrast", "focus on differences between two things"),
        ("summarize", "give the main ideas in a short form"),
        ("bias", "a tendency to prefer one side or view unfairly"),
    ),
    "family_social": (
        ("support", "help or encouragement you give to someone"),
        ("boundaries", "limits about what behavior you accept from others"),
        ("expectations", "beliefs about what should happen or how people should act"),
        ("compromise", "an agreement where each side gives up something"),
        ("trust", "belief that someone is honest and reliable"),
        ("conflict", "serious disagreement or argument"),
        ("household", "all the people living together in one home"),
        ("upbringing", "the way you were cared for and taught as a child"),
    ),
    "work_study": (
        ("qualification", "a certificate, degree, or skill that proves ability"),
        ("deadline", "the latest time something must be finished"),
        ("feedback", "comments about how well you did and how to improve"),
        ("curriculum", "the full set of subjects or topics in a course"),
        ("peer", "a person of the same age or level as you in school or work"),
        ("plagiarism", "using someone else's work as if it were your own"),
        ("revision", "studying material again before a test"),
        ("internship", "a short period of training work, often for students"),
    ),
    "health": (
        ("symptom", "a sign that you might be ill or stressed"),
        ("prevention", "actions that stop a problem before it starts"),
        ("well-being", "your general state of health and happiness"),
        ("chronic", "continuing for a long time, not just once"),
        ("recovery", "the process of getting better after illness or injury"),
        ("nutrition", "the food you eat and how it affects your body"),
        ("sedentary", "involving a lot of sitting and little physical activity"),
        ("resilience", "ability to recover from difficulties"),
    ),
    "safety_disaster": (
        ("hazard", "something that can cause harm or danger"),
        ("evacuation", "organized movement of people away from danger"),
        ("first aid", "simple medical care given immediately after an injury"),
        ("insurance", "an agreement that pays money if you have a loss"),
        ("emergency kit", "basic supplies kept ready for a crisis"),
        ("aftershock", "a smaller earthquake following a larger one"),
        ("shelter", "a safe place that protects you from weather or danger"),
        ("mitigation", "steps that reduce the seriousness of a future risk"),
    ),
    "media_tech": (
        ("algorithm", "a set of rules a computer uses to sort or show content"),
        ("privacy", "control over who sees your personal information"),
        ("misinformation", "false information spread without intending to lie"),
        ("disinformation", "false information spread on purpose to mislead"),
        ("notification", "an alert on your phone or computer"),
        ("screen time", "hours spent using phones, TVs, or computers"),
        ("digital footprint", "the record of your activity left online"),
        ("cyberbullying", "using digital tools to harass or threaten someone"),
    ),
    "society": (
        ("inequality", "an unfair difference between groups"),
        ("stereotype", "a fixed, oversimplified idea about a group of people"),
        ("prejudice", "unfair negative attitudes not based on real evidence"),
        ("legislation", "laws made by a government"),
        ("activism", "organized efforts to bring social or political change"),
        ("integration", "the process of becoming part of a larger community"),
        ("marginalized", "treated as unimportant and pushed to the edge of society"),
        ("accountability", "being responsible for your actions and their results"),
    ),
    "leisure_travel": (
        ("itinerary", "a planned route or list of places and times for a trip"),
        ("souvenir", "an object you buy to remember a place you visited"),
        ("jet lag", "tiredness after flying across many time zones"),
        ("customs", "the place where your bags are checked when you enter a country"),
        ("hostel", "inexpensive lodging, often with shared rooms"),
        ("landmark", "a famous building or natural feature that helps you navigate"),
        ("excursion", "a short trip for pleasure, often as part of a holiday"),
        ("overtourism", "too many visitors causing harm to a place"),
    ),
    "money_consumer": (
        ("budget", "a plan for how you will spend or save money"),
        ("expense", "money you have to pay for something"),
        ("bargain", "something bought for less than the usual price"),
        ("refund", "money given back when you return a product"),
        ("subscription", "regular payment for a continuing service"),
        ("impulse buying", "buying suddenly without careful thought"),
        ("brand loyalty", "always choosing products from the same company"),
        ("consumer rights", "legal protections for people who buy goods or services"),
    ),
    "emotion_behavior": (
        ("trigger", "something that causes a strong emotional reaction"),
        ("coping strategy", "a healthy way you deal with stress or pain"),
        ("empathy", "understanding and sharing another person's feelings"),
        ("etiquette", "accepted rules for polite behavior in a society"),
        ("tone of voice", "the way your voice sounds, showing attitude or emotion"),
        ("body language", "messages sent by posture, gestures, and facial expressions"),
        ("resentment", "long-lasting angry feelings after unfair treatment"),
        ("self-awareness", "understanding your own emotions and habits"),
    ),
    "environment_science": (
        ("pollution", "harmful substances added to air, water, or soil"),
        ("renewable energy", "energy from sources that are naturally replaced"),
        ("carbon footprint", "total greenhouse gases caused by a person or activity"),
        ("biodiversity", "the variety of living species in an area"),
        ("sustainability", "using resources in a way that protects the future"),
        ("innovation", "a new idea, device, or method that improves something"),
        ("ethics", "ideas about what is morally right or wrong in research"),
        ("hypothesis", "a testable prediction in a scientific investigation"),
    ),
    "arts_culture": (
        ("composition", "the way parts are arranged in a picture, song, or text"),
        ("interpretation", "your personal explanation of the meaning of art"),
        ("genre", "a category such as comedy, thriller, or portrait"),
        ("exhibition", "a public show of paintings, photos, or objects"),
        ("censorship", "official control over what art or media may appear"),
        ("heritage", "traditions and objects passed down from past generations"),
        ("aesthetic", "related to beauty or taste in art and design"),
        ("inspiration", "something that gives you new creative ideas"),
    ),
    "hypothetical_drill": (
        ("imagine", "form a picture or idea in your mind"),
        ("hypothetical", "a situation imagined to explore possibilities, not real"),
        ("prioritize", "decide which things are most important first"),
        ("trade-off", "accepting a disadvantage to gain an advantage"),
        ("consequence", "a result that follows from an action or choice"),
        ("preference", "something you like more than other options"),
        ("probability", "how likely something is to happen"),
        ("justification", "reasons you give to support a decision"),
    ),
    "grammar_time": (
        ("frequency", "how often something happens"),
        ("duration", "how long something continues"),
        ("sequence", "the order in which events happen"),
        ("routine", "things you do regularly in a fixed order"),
        ("appointment", "a planned meeting at an agreed time"),
        ("punctual", "arriving at the correct time, not late"),
        ("time zone", "a region where the same standard time is used"),
        ("deadline", "the latest time by which something must be done"),
    ),
    "usa_geo": (
        ("federal", "relating to the national government, not only one state"),
        ("state", "one of the major regions with its own local government"),
        ("census", "an official count of the population"),
        ("infrastructure", "roads, bridges, and systems a country relies on"),
        ("region", "a large area with shared geographic or cultural features"),
        ("climate", "typical weather patterns in an area over many years"),
        ("border", "the official line between two countries or states"),
        ("landmark", "a famous place that represents a city or country"),
    ),
}


CLUSTER_RULES: tuple[tuple[tuple[str, ...], str], ...] = (
    (("how long", "how often", "when did you first", "when was the last"), "grammar_time"),
    (("days of the week", "months of the year", "how do you"), "grammar_time"),
    (("would you rather", "would you ever", "what if", "what would you", "if you were"), "hypothetical_drill"),
    (("do you wish", "who is the greatest", "tell me about", "have you ever", "silly questions"), "hypothetical_drill"),
    (("talk about three", "talk about four", "talk about two", "drills", "are you good at"), "hypothetical_drill"),
    (("united states", "about the united states", "moving to the united states"), "usa_geo"),
    (("u.s.", "american leadership", "states geography"), "usa_geo"),
    (("canada", "cultural shock"), "society"),
    (("earthquake", "tsunami", "disaster", "fire safety", "accidents at home", "safety inside"), "safety_disaster"),
    (("traffic accident", "danger", "trauma"), "safety_disaster"),
    (("facebook", "internet", "social networking", "new media", "texting", "telephones", "television", "computers"), "media_tech"),
    (("environment", "pollution", "science & technology", "cloning", "inventions"), "environment_science"),
    (("job interview", "jobs & occupations", "self-employment", "service industry", "business", "unemployment"), "money_consumer"),
    (("money & shopping", "gambling", "tipping", "garage sale", "poverty", "charity", "volunteer"), "money_consumer"),
    (("travel", "airplanes", "transportation", "commuting", "beach", "vacation", "cities", "hometowns", "countries"), "leisure_travel"),
    (("hotel", "neighborhood", "home", "house renovation", "chores", "garage sale"), "family_social"),
    (("family", "marriage", "children", "parenting", "dating", "weddings", "single life", "adoption"), "family_social"),
    (("school", "classrooms", "teachers", "homework", "university", "college", "standardized exams", "education", "english study"), "work_study"),
    (
        (
            "health",
            "diet",
            "sleep",
            "smoking",
            "mind, body",
            "disabilities",
            "childbirth",
            "body language",
            "body",
        ),
        "health",
    ),
    (("sport", "baseball", "basketball", "olympics", "martial arts", "bullfighting"), "leisure_travel"),
    (("movies", "music", "entertainment", "comics", "super heroes", "celebrities", "movie industry"), "arts_culture"),
    (("art", "painting", "photography", "fashion", "beauty", "makeup", "clothes"), "arts_culture"),
    (("crime", "police", "corruption", "terror", "war"), "society"),
    (("discrimination", "race", "prejudice", "stereotypes", "gender roles", "gay community", "religion", "faith"), "society"),
    (("politics", "news", "immigration", "russia & the world", "world peace"), "society"),
    (("emotion", "anger", "fear", "stress", "happiness", "feelings", "humor", "manners", "behavior"), "emotion_behavior"),
)


def _cluster_for_title(title: str) -> str:
    """Map title → vocabulary cluster without naive substring bugs (e.g. 'art' in 'party')."""
    t_norm = " ".join(re.findall(r"[a-z0-9]+", title.lower()))
    if not t_norm:
        return "general"
    word_set = set(t_norm.split())
    for keywords, cluster in CLUSTER_RULES:
        for k in keywords:
            k_clean = k.lower().strip()
            if not k_clean:
                continue
            parts = re.findall(r"[a-z0-9]+", k_clean)
            if len(parts) >= 2:
                if " ".join(parts) in t_norm:
                    return cluster
            elif len(parts) == 1 and parts[0] in word_set:
                return cluster
    return "general"


def _talk_about_things_count(title: str) -> int | None:
    return {
        "Talk About Two Things": 2,
        "Talk About Three Things": 3,
        "Talk About Four Things": 4,
    }.get(title)


def _phrases_talk_about(n: int) -> tuple[str, ...]:
    if n == 2:
        return (
            "There are two things I want to mention: first … and second …",
            "On one hand …; on the other hand …",
            "If I compare these two points, the main difference is …",
            "The first thing is … The second thing is …",
            "Between option A and option B, I would choose … because …",
            "What links these two ideas together is …",
            "Could you give two clear examples from your own life?",
            "Two reasons I feel this way are … and …",
            "I would put it in this order: first …, then …",
        )
    if n == 3:
        return (
            "I will talk about three things: first …, second …, and third …",
            "The three main points I want to make are …",
            "In order of importance, I would say …, then …, and finally …",
            "One similarity among all three is …",
            "The weakest of the three, in my view, is … because …",
            "If I had to remove one of the three, I would drop …",
            "Three examples that support my opinion are …",
            "Let me summarize the three ideas in one sentence: …",
            "Which of the three matters most to you personally?",
        )
    if n == 4:
        return (
            "I will cover four areas: first …, second …, third …, and fourth …",
            "The four corners of this topic are …",
            "Out of these four, the one I use most often is …",
            "Two of these four go together well; the other two are more separate because …",
            "If we only had time for two of the four, I would pick … and …",
            "The fourth point is easy to forget, but it matters because …",
            "Let me rank these four from most to least important: …",
            "Four short examples from everyday life are …",
            "Which of the four would you change first if you could?",
        )
    return ()


def _sentences_talk_about(n: int) -> tuple[str, ...]:
    if n == 2:
        return (
            "Our teacher asked us to compare two ideas, so I prepared two short examples.",
            "I find it easier to speak when I limit myself to two clear reasons.",
            "In pairs, we listed two advantages and two disadvantages before we decided.",
            "Two things I noticed in the news this week both relate to education.",
            "When I practice, I say the first point slowly, then I add the second point.",
            "Two memories from childhood still shape how I think about this topic.",
            "If I only had thirty seconds, I would name two facts and stop.",
            "My partner and I disagreed on two small details, but we agreed on the big picture.",
            "Two questions I still have are whether … and whether …",
            "I used two linking words, “first” and “second,” to keep my answer organized.",
            "Between two cultures, the routine that surprised me most was …",
            "Two people I interviewed gave opposite advice, which made the discussion interesting.",
            "I wrote two short paragraphs so each idea had enough space.",
            "Two common mistakes learners make here are rushing and repeating the same idea twice.",
        )
    if n == 3:
        return (
            "Listing three reasons helped me sound more confident in the speaking exam.",
            "I grouped my answer into three short parts so the listener could follow easily.",
            "Three friends gave three different opinions, and I tried to respect all of them.",
            "In my notebook I keep three vocabulary columns: noun, verb, and adjective.",
            "Three everyday situations where this skill matters are school, work, and travel.",
            "The third point was the hardest to explain, so I used a simple example.",
            "We took turns: each student added one new fact until we had three.",
            "Three months ago I would have answered differently; my view has shifted.",
            "I practiced three times before class and timed myself each time.",
            "Three questions the examiner asked all connected to the same main theme.",
            "On the board we wrote three headings and filled them in as a team.",
            "Three small changes in my routine already improved my focus.",
            "I can describe the process in three steps without looking at my notes.",
            "Three sources I read agreed on the facts but disagreed on the solution.",
        )
    if n == 4:
        return (
            "Talking about four items is challenging, so I use a simple memory pattern.",
            "We divided the whiteboard into four boxes and put one idea in each box.",
            "Four classmates shared four stories, and we looked for common themes.",
            "I try to spend equal time on each of the four so one part does not dominate.",
            "Four factors influenced my decision: cost, time, quality, and location.",
            "In the exam I named four examples, but I kept each one very short.",
            "Four questions from the audience pushed me to clarify my main claim.",
            "I listed four pros and then four cons before I formed an opinion.",
            "Four photos on the slide reminded me what to say next.",
            "My study group meets four times a month to practice this drill.",
            "Four short sentences are better than one long confusing paragraph.",
            "I ranked four options and explained why the bottom one failed.",
            "Four cultural habits surprised me when I moved to a new city.",
            "We rotated roles four times so everyone practiced every part.",
        )
    return ()


def _questions_talk_about(n: int) -> tuple[str, ...]:
    word = {2: "two", 3: "three", 4: "four"}[n]
    return (
        f"What {word} things will you choose if you have no time to prepare?",
        f"Which {word} items on your list are the easiest to explain in English?",
        f"How do you decide the order when you present {word} points?",
        f"Can {word} small examples be stronger than one long story? Why?",
        f"What {word} questions would you ask a partner who disagrees with you?",
        f"Which of your {word} points is most personal, and which is most factual?",
        "How would you shorten your answer if you could keep only half of your main points?",
        f"What {word} topics would you avoid in a formal interview, and why?",
        f"If you could add a fifth idea, how would it connect to the {word} you already have?",
        f"What {word} skills from this drill help you in real conversations?",
        f"How do you check that your listener understood all {word} parts?",
        f"What {word} words or phrases help you signal structure while you speak?",
        f"Describe {word} times when this structure helped you in school or work.",
        f"In your culture, is it common to organize answers in {word} clear parts?",
    )


def _writing_talk_about(n: int) -> tuple[str, ...]:
    spell = {2: "two", 3: "three", 4: "four"}[n]
    return (
        f"Write exactly {n} short paragraphs ({spell} separate ideas), each with a clear topic sentence.",
        f"Write a dialogue where each speaker must give exactly {n} reasons for their opinion.",
        f"Write a self-check list of {n} items you will review before your next speaking practice.",
    )


def _title_tokens(title: str) -> list[str]:
    words = re.findall(r"[A-Za-z]+", title)
    skip = {"and", "or", "the", "of", "in", "to", "for", "your", "you", "a", "an", "at", "on", "with", "from"}
    return [w for w in words if len(w) > 2 and w.lower() not in skip]


def _merge_vocab(title: str, cluster: str, lang: str) -> tuple[TopicVocab, ...]:
    pool: list[tuple[str, str]] = []
    seen: set[str] = set()

    def add(items: Iterable[tuple[str, str]]) -> None:
        for term, gloss_en in items:
            key = term.lower()
            if key not in seen:
                seen.add(key)
                pool.append((term, gloss_en))

    add(CLUSTER_VOCAB.get(cluster, CLUSTER_VOCAB["general"]))
    add(CLUSTER_VOCAB["general"])
    add(_ACADEMIC_SPEAKING)

    for tok in _title_tokens(title)[:6]:
        if tok.lower() not in seen:
            seen.add(tok.lower())
            pool.append(
                (tok.capitalize() if tok.islower() else tok, _THEME_GLOSS_MARKER)
            )

    out: list[TopicVocab] = []
    for term, gloss_src in pool[:22]:
        if gloss_src == _THEME_GLOSS_MARKER:
            out.append(TopicVocab(term, _ct_loc.theme_keyword_gloss(title, lang)))
        else:
            out.append(TopicVocab(term, _ct_loc.gloss(gloss_src, lang)))
    return tuple(out)


def _phrases(title: str) -> tuple[str, ...]:
    return (
        f"If I had to introduce “{title}” in one sentence, I would say…",
        f"The aspect of {title} that affects me most directly is…",
        f"Compared with five years ago, {title} seems to have become…",
        f"I would explain {title} to a younger learner by saying…",
        f"A common misconception about {title} is…",
        f"What I still want to learn about {title} is…",
        "Could you elaborate on what you mean by that?",
        "I see your point; however, I would add that…",
        "I am not entirely sure, but my impression is that…",
    )


def _sentences(title: str, cluster: str) -> tuple[str, ...]:
    t = title
    core = [
        f"When our teacher announced the topic “{t},” I immediately thought of a story from my own life.",
        f"I would define “{t}” in everyday language as something people notice, talk about, and sometimes disagree on.",
        f"In my community, {t} comes up in conversations more often than strangers might expect.",
        f"If someone asked me for advice about {t}, I would first ask what situation they are facing.",
        f"One article I read connected {t} to wider social changes, not only personal choices.",
        f"I try to listen carefully when classmates discuss {t} because opinions vary a lot.",
        f"My family and I do not always share the same view on {t}, but we usually stay respectful.",
        f"On social media, {t} is often simplified, so I prefer longer discussions in class.",
        f"I would summarize my stance on {t} as cautious optimism, though details matter.",
        f"Studying {t} in English helps me express ideas I already have in my first language.",
    ]
    extra = {
        "grammar_time": [
            f"When we practice “{t},” I pay attention to auxiliary verbs and word order.",
            f"I sometimes confuse similar time expressions while answering questions about {t}.",
        ],
        "hypothetical_drill": [
            f"Questions about “{t}” force me to choose between values, not only facts.",
            f"I like {t} drills because there is no single correct emotional answer.",
        ],
        "safety_disaster": [
            f"Talking about {t} reminds me that preparation is more useful than panic.",
            f"I would rather know basic safety steps than ignore risks related to {t}.",
        ],
        "media_tech": [
            f"The topic {t} makes me reconsider how much attention I give to screens.",
            f"I try to verify claims I see online before I discuss {t} with friends.",
        ],
    }.get(cluster, [
        f"I can connect {t} to both local examples and something I have read internationally.",
        f"Before I argue about {t}, I like to check whether we mean the same terms.",
    ])
    return tuple(core + extra)[:14]


def _questions(title: str) -> tuple[str, ...]:
    t = title
    return (
        f"What is the first example you think of when you hear “{t}”?",
        f"How is {t} viewed differently by different generations in your country?",
        f"Has your personal attitude toward {t} changed over time? Why?",
        f"What habits or policies could improve outcomes related to {t}?",
        f"Who is most affected by {t}, and in what concrete ways?",
        f"What is a respectful way to disagree with someone about {t}?",
        f"Which news source or book has shaped your ideas about {t}?",
        f"What is one myth or stereotype people should stop repeating about {t}?",
        f"If you could interview an expert on {t}, what three questions would you ask?",
        f"How does {t} appear in films, songs, or advertisements you know?",
        f"What role should schools play in teaching students about {t}?",
        f"Describe a time when {t} created a dilemma for you or someone you know.",
        f"What would you like foreigners to understand about {t} in your culture?",
        f"Looking ahead ten years, how might {t} evolve, in your opinion?",
    )


def _writing_prompts(title: str) -> tuple[str, ...]:
    t = title
    return (
        f"Write a 150-word paragraph explaining why “{t}” matters to you personally.",
        f"Write a dialogue between two friends who disagree politely about {t}.",
        f"Write a short reflective journal entry: “What I learned after discussing {t} in class.”",
    )


def build_topic(title: str, lang: str = "en") -> ConversationTopic:
    cluster = _cluster_for_title(title)
    slug = TITLE_TO_SLUG[title]
    n_things = _talk_about_things_count(title)
    if n_things is not None:
        useful_phrases = _phrases_talk_about(n_things)
        example_sentences = _sentences_talk_about(n_things)
        discussion_questions = _questions_talk_about(n_things)
        writing_prompts = _writing_talk_about(n_things)
    else:
        useful_phrases = _phrases(title)
        example_sentences = _sentences(title, cluster)
        discussion_questions = _questions(title)
        writing_prompts = _writing_prompts(title)
    return ConversationTopic(
        title=title,
        slug=slug,
        overview_paragraphs=_ct_loc.overview_paragraphs(title, cluster, lang),
        vocabulary=_merge_vocab(title, cluster, lang),
        useful_phrases=useful_phrases,
        example_sentences=example_sentences,
        discussion_questions=discussion_questions,
        writing_prompts=writing_prompts,
    )


def topic_by_slug(slug: str, lang: str = "en") -> ConversationTopic | None:
    for t in RAW_TOPIC_TITLES:
        if TITLE_TO_SLUG[t] == slug:
            return build_topic(t, lang)
    return None
