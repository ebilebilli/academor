"""English conversation topics: A–Z index, topic of the day, previous / next."""

import datetime

from django.test import TestCase
from django.urls import reverse

from projects.views.conversation_topics_views import sorted_topics, topic_groups, topic_of_the_day


class ConversationTopicsTests(TestCase):
    def test_index_is_alphabetical_and_the_article_is_ignored(self):
        items = sorted_topics()
        titles = [item['title'] for item in items]
        self.assertEqual(titles.index('The Art of Conversation'), titles.index('Art') + 1)
        letters = [group['letter'] for group in topic_groups(items)]
        self.assertEqual(letters, sorted(letters))
        self.assertEqual(sum(len(g['topics']) for g in topic_groups(items)), len(items))

    def test_topic_of_the_day_is_stable_for_a_day(self):
        items = sorted_topics()
        day = datetime.date(2026, 11, 25)
        first = topic_of_the_day(items, 'en', day)
        self.assertEqual(first, topic_of_the_day(items, 'en', day))
        self.assertEqual(len(first['questions']), 3)

    def test_list_page(self):
        response = self.client.get(reverse('projects:english-conversation-topics'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-topics-search')
        self.assertContains(response, 'id="tpx-A"')
        self.assertContains(response, reverse('projects:tests-page'))

    def test_detail_page_links_previous_and_next(self):
        items = sorted_topics()
        middle = items[1]
        response = self.client.get(reverse('projects:english-conversation-topic-detail', kwargs={'slug': middle['slug']}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['prev_topic']['slug'], items[0]['slug'])
        self.assertEqual(response.context['next_topic']['slug'], items[2]['slug'])
        first = self.client.get(reverse('projects:english-conversation-topic-detail', kwargs={'slug': items[0]['slug']}))
        self.assertIsNone(first.context['prev_topic'])
