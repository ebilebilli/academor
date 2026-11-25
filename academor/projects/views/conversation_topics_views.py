import datetime

from django.http import Http404, HttpResponsePermanentRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import View

from projects import conversation_topics_locale as ct_loc
from projects.conversation_topics_data import (
    LEGACY_TOPIC_SLUG_REDIRECTS,
    RAW_TOPIC_TITLES,
    TITLE_TO_SLUG,
    build_topic,
    topic_by_slug,
)
from projects.utils.queries import (
    get_background_image,
    get_language_from_request,
    get_project_categories,
    serialize_project_category,
)
from projects.utils.seo_text import topic_overview_preview


def _sort_key(title: str) -> str:
    """"The Art of Conversation" files under A, like in a printed index."""
    key = title.strip()
    if key.lower().startswith("the "):
        key = key[4:]
    return key.lower()


def sorted_topics() -> list[dict]:
    """All topics in A–Z order (the order of the list page and of previous / next)."""
    items = [
        {"title": t, "slug": TITLE_TO_SLUG[t], "letter": (_sort_key(t)[:1] or "#").upper()}
        for t in RAW_TOPIC_TITLES
    ]
    items.sort(key=lambda item: _sort_key(item["title"]))
    for item in items:
        if not item["letter"].isalpha():
            item["letter"] = "#"
    return items


def topic_groups(items: list[dict]) -> list[dict]:
    groups: list[dict] = []
    for item in items:
        if not groups or groups[-1]["letter"] != item["letter"]:
            groups.append({"letter": item["letter"], "topics": []})
        groups[-1]["topics"].append(item)
    return groups


def topic_of_the_day(items: list[dict], lang: str, today: datetime.date | None = None) -> dict | None:
    """One topic per day, the same for everyone, with a few of its discussion questions."""
    if not items:
        return None
    today = today or datetime.date.today()
    item = items[today.toordinal() % len(items)]
    topic = build_topic(item["title"], lang)
    return {
        "title": topic.title,
        "slug": item["slug"],
        "questions": list(topic.discussion_questions[:3]),
    }


class LegacyTopicTwoRedirectView(View):
    """Old slug ``two`` → ``talk-about-two-things`` (title was renamed)."""

    def get(self, request, *args, **kwargs):
        url = reverse(
            "projects:english-conversation-topic-detail",
            kwargs={"slug": "talk-about-two-things"},
        )
        return HttpResponsePermanentRedirect(url)


class LegacyLearnEnglishConversationTopicRedirectView(View):
    """301 from ``/learn/english-conversation-topics/<slug>/`` → ``/topics/<slug>/``."""

    def get(self, request, slug, *args, **kwargs):
        url = reverse(
            "projects:english-conversation-topic-detail",
            kwargs={"slug": slug},
        )
        return HttpResponsePermanentRedirect(url)


class EnglishConversationTopicsListView(View):
    """Speaking topics index: same header image source as level tests (CMS)."""

    template_name = "english-conversation-topics.html"

    def get(self, request):
        lang = get_language_from_request(request)
        topics_meta = sorted_topics()
        groups = topic_groups(topics_meta)
        categories = get_project_categories(lang)
        n = len(topics_meta)
        context = {
            "page_title": ct_loc.list_page_title_site(lang),
            "page_description": ct_loc.list_page_meta_description(lang),
            "page_keywords": _(
                "english conversation, speaking practice, esl topics, vocabulary, academor"
            ),
            "list_h1": ct_loc.list_page_h1(lang),
            "list_lead": ct_loc.list_page_lead(lang),
            "topics": topics_meta,
            "topic_groups": groups,
            "topic_letters": [g["letter"] for g in groups],
            "topic_of_the_day": topic_of_the_day(topics_meta, lang),
            "topic_count": n,
            "topics_count_label": ct_loc.list_topics_count_label(n, lang),
            "background_image": get_background_image("tests"),
            "language": lang,
            "categories": [serialize_project_category(c, lang) for c in categories],
        }
        return render(request, self.template_name, context)


class EnglishConversationTopicDetailView(View):
    template_name = "english-conversation-topic-detail.html"

    def get(self, request, slug):
        new_slug = LEGACY_TOPIC_SLUG_REDIRECTS.get(slug)
        if new_slug:
            return HttpResponsePermanentRedirect(
                reverse(
                    "projects:english-conversation-topic-detail",
                    kwargs={"slug": new_slug},
                )
            )
        lang = get_language_from_request(request)
        topic = topic_by_slug(slug, lang)
        if topic is None:
            raise Http404(_("Topic not found"))
        categories = get_project_categories(lang)
        preview = topic_overview_preview(topic.overview_paragraphs)
        if not preview.strip():
            preview = _(
                "English conversation speaking topic %(topic)s — questions, vocabulary and prompts at Academor, Baku."
            ) % {"topic": topic.title}
        items = sorted_topics()
        index = next((i for i, item in enumerate(items) if item["slug"] == slug), None)
        prev_topic = items[index - 1] if index else None
        next_topic = items[index + 1] if index is not None and index + 1 < len(items) else None
        context = {
            "prev_topic": prev_topic,
            "next_topic": next_topic,
            "topic_position": (index + 1) if index is not None else None,
            "topic_count": len(items),
            "page_title": _("%(topic)s | English conversation | Academor") % {"topic": topic.title},
            "page_description": preview[:320],
            "page_keywords": _("english conversation, speaking practice, esl, %(topic)s")
            % {"topic": topic.title},
            "topic": topic,
            "background_image": get_background_image("tests"),
            "language": lang,
            "categories": [serialize_project_category(c, lang) for c in categories],
        }
        return render(request, self.template_name, context)
