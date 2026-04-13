from django.http import Http404, HttpResponsePermanentRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import View

from projects import conversation_topics_locale as ct_loc
from projects.conversation_topics_data import RAW_TOPIC_TITLES, TITLE_TO_SLUG, topic_by_slug
from projects.utils.queries import (
    get_background_image,
    get_language_from_request,
    get_project_categories,
    serialize_project_category,
)


class LegacyTopicTwoRedirectView(View):
    """Old slug ``two`` → ``talk-about-two-things`` (title was renamed)."""

    def get(self, request, *args, **kwargs):
        url = reverse(
            "projects:english-conversation-topic-detail",
            kwargs={"slug": "talk-about-two-things"},
        )
        return HttpResponsePermanentRedirect(url)


class EnglishConversationTopicsListView(View):
    """Speaking topics index: same header image source as level tests (CMS)."""

    template_name = "english-conversation-topics.html"

    def get(self, request):
        lang = get_language_from_request(request)
        topics_meta = [{"title": t, "slug": TITLE_TO_SLUG[t]} for t in RAW_TOPIC_TITLES]
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
        lang = get_language_from_request(request)
        topic = topic_by_slug(slug, lang)
        if topic is None:
            raise Http404(_("Topic not found"))
        categories = get_project_categories(lang)
        context = {
            "page_title": _("%(topic)s | English conversation | Academor")
            % {"topic": topic.title},
            "page_description": _(
                "Model sentences and questions in English; localized tips and vocabulary glosses."
            ),
            "page_keywords": _("english conversation, speaking practice, esl, %(topic)s")
            % {"topic": topic.title},
            "topic": topic,
            "background_image": get_background_image("tests"),
            "language": lang,
            "categories": [serialize_project_category(c, lang) for c in categories],
        }
        return render(request, self.template_name, context)
