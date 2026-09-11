"""Regression tests for portal security boundaries.

Covers two fixes:
  * OfferNotificationDetailView leaked any offer to any authenticated portal user.
  * Student-supplied quiz answers were rendered through ``quiz_html`` (``mark_safe``),
    giving students stored XSS against the teacher review page.
"""

from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.test import Client, TestCase
from django.urls import reverse

from portals.models import (
    OfferNotification,
    ParentProfile,
    PortalNotification,
    StudentProfile,
    TeacherProfile,
)
from portals.tests.portal_helpers import ensure_active_portal_services, portal_client_login

User = get_user_model()


class OfferNotificationAccessTests(TestCase):
    """Only the user the offer was delivered to may open its detail page."""

    def setUp(self):
        ensure_active_portal_services('ielts')

        self.recipient_user = User.objects.create_user(username='offer_recipient', password='pass')
        self.other_user = User.objects.create_user(username='offer_outsider', password='pass')
        self.parent_user = User.objects.create_user(username='offer_parent', password='pass')
        self.teacher_user = User.objects.create_user(username='offer_teacher', password='pass')

        self.recipient = StudentProfile.objects.create(user=self.recipient_user)
        self.other_student = StudentProfile.objects.create(user=self.other_user)
        self.parent = ParentProfile.objects.create(user=self.parent_user)
        self.teacher = TeacherProfile.objects.create(user=self.teacher_user)

        self.offer = OfferNotification.objects.create(
            name='Summer discount',
            description='20% off the next course.',
        )
        PortalNotification.objects.create(
            student=self.recipient,
            offer_notification=self.offer,
            kind=PortalNotification.Kind.OFFER_NOTIFICATION,
        )

        self.url = reverse('portals:offer-notification-detail', kwargs={'pk': self.offer.pk})

    def _client_for(self, user):
        client = Client()
        portal_client_login(client, user)
        return client

    def test_recipient_can_open_offer(self):
        response = self._client_for(self.recipient_user).get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Summer discount')

    def test_other_student_cannot_open_offer(self):
        response = self._client_for(self.other_user).get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_unrelated_parent_cannot_open_offer(self):
        response = self._client_for(self.parent_user).get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_teacher_cannot_open_offer(self):
        response = self._client_for(self.teacher_user).get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_anonymous_is_redirected_to_login(self):
        response = Client().get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/portal/login/', response['Location'])


class StudentAnswerEscapingTests(TestCase):
    """Student-authored answers must never reach the page as trusted HTML."""

    # Trailing text proves the answer is still shown, not blanked out wholesale.
    payload = '<img src=x onerror=alert(1)>Paris'

    def _assert_neutralised(self, template_name, context):
        html = render_to_string(template_name, context)
        self.assertNotIn('<img', html)
        self.assertNotIn('onerror', html)
        self.assertIn('Paris', html)

    def _question(self, **extra):
        # Every key the templates use as a filter argument must exist, otherwise
        # the template engine raises VariableDoesNotExist while resolving `default:`.
        question = {
            'number': 1,
            'question': 'Gap fill',
            'student_answer': self.payload,
            'student_answer_display': '',
            'correct_answer': 'Paris',
            'correct_answer_display': '',
        }
        question.update(extra)
        return question

    def test_reading_teacher_review_escapes_student_answer(self):
        self._assert_neutralised(
            'portals/includes/quiz_reading_teacher_review_question.html',
            {'q': self._question()},
        )

    def test_reading_choice_review_escapes_student_answer(self):
        self._assert_neutralised(
            'portals/includes/quiz_reading_question_choice.html',
            {'view_only': True, 'q': self._question()},
        )

    def test_listening_variant_review_escapes_student_answer(self):
        self._assert_neutralised(
            'portals/includes/quiz_listening_variant.html',
            {'view_only': True, 'q': self._question()},
        )

    def test_display_value_is_also_neutralised(self):
        # Choice questions render `student_answer_display`; it must be treated
        # with the same suspicion as the raw answer.
        self._assert_neutralised(
            'portals/includes/quiz_reading_teacher_review_question.html',
            {'q': self._question(student_answer_display=self.payload)},
        )
