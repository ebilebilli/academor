from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from portals.admin.admin_v1 import QuizQuestionInline
from portals.models import Quiz, QuizCategory
from portals.tests.portal_helpers import ensure_active_portal_services

User = get_user_model()


class QuizQuestionInlineAdminTests(TestCase):
    def setUp(self):
        ensure_active_portal_services('ielts')
        self.factory = RequestFactory()
        self.inline = QuizQuestionInline(Quiz, admin_site=None)
        self.category = QuizCategory.objects.create(name='Grammar')
        self.quiz = Quiz.objects.create(category=self.category, topic='Variant quiz')

    def test_inline_always_includes_spr_answer_fields(self):
        request = self.factory.get('/')
        fields = self.inline.get_fields(request, obj=self.quiz)

        self.assertIn('question_type', fields)
        self.assertIn('spr_correct_answers', fields)
        self.assertIn('spr_max_length', fields)
