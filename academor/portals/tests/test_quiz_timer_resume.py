"""A page reload (F5) keeps the quiz clock running instead of starting again at zero."""

from datetime import timedelta
from unittest import mock

from django.urls import reverse
from django.utils import timezone

from portals.tests.test_quiz_reading import QuizReadingTests


class QuizTimerResumeTests(QuizReadingTests):
    def _start(self, client, quiz, at=None):
        url = reverse('portals:student-quiz-start', kwargs={'pk': quiz.pk})
        if at is None:
            return client.post(url, content_type='application/json').json()
        with mock.patch('django.utils.timezone.now', return_value=at):
            return client.post(url, content_type='application/json').json()

    def _client(self):
        from portals.tests.test_quiz_submit import _portal_client_login

        client = self.client_class()
        _portal_client_login(client, self.student_user)
        return client

    def test_reload_continues_the_clock(self):
        quiz = self._create_reading_quiz()
        quiz.is_time_limited = True
        quiz.time_limit_minutes = 60
        quiz.save()
        client = self._client()
        now = timezone.now()

        first = self._start(client, quiz, at=now)
        self.assertTrue(first['success'])
        self.assertEqual(first['elapsed_sec'], 0)
        self.assertTrue(first['attempt_key'])

        again = self._start(client, quiz, at=now + timedelta(seconds=95))
        self.assertEqual(again['elapsed_sec'], 95)
        self.assertEqual(again['attempt_key'], first['attempt_key'])

    def test_a_long_forgotten_attempt_starts_fresh(self):
        quiz = self._create_reading_quiz()
        quiz.is_time_limited = True
        quiz.time_limit_minutes = 60
        quiz.save()
        client = self._client()
        now = timezone.now()
        first = self._start(client, quiz, at=now)

        later = self._start(client, quiz, at=now + timedelta(hours=3))
        self.assertEqual(later['elapsed_sec'], 0)
        self.assertNotEqual(later['attempt_key'], first['attempt_key'])

    def test_take_page_loads_the_draft_script(self):
        quiz = self._create_reading_quiz()
        response = self._client().get(reverse('portals:student-reading-quiz-take', kwargs={'pk': quiz.pk}))
        self.assertContains(response, 'portals/js/quiz-draft.js')
