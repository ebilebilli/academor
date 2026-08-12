from django.contrib.auth import get_user_model
from django.test import TestCase

from portals.models import (
    CustomerProfile,
    Quiz,
    QuizQuestion,
    QuizResult,
    StudentProfile,
)
from portals.tests.group_helpers import create_quiz_category
from portals.utils.quiz_result_export import (
    build_quiz_result_word_export,
    quiz_result_supports_word_export,
)
from projects.models.service_models import Service

User = get_user_model()


class QuizResultWordExportTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Service.objects.get_or_create(
            slug='ielts',
            defaults={'name_az': 'IELTS', 'name_en': 'IELTS', 'is_active': True},
        )
        cls.category = create_quiz_category('Grammar', 'ielts')
        cls.student = StudentProfile.objects.create(
            user=User.objects.create_user(username='export_student', password='pass'),
        )
        cls.customer = CustomerProfile.objects.create(
            user=User.objects.create_user(username='export_customer', password='pass'),
        )

    def test_variant_export_includes_readable_answers(self):
        quiz = Quiz.objects.create(category=self.category, topic='Variants')
        question = QuizQuestion.objects.create(
            quiz=quiz,
            order=1,
            question='Capital?',
            answer_options=['Paris', 'London'],
            correct_answer='Paris',
        )
        result = QuizResult.objects.create(
            student=self.student,
            quiz=quiz,
            given_answers={str(question.pk): 1},
            total_score=0,
        )
        self.assertTrue(quiz_result_supports_word_export(quiz))
        payload = build_quiz_result_word_export(result)
        self.assertIsNotNone(payload)
        self.assertEqual(payload['student_name'], self.student.full_name)
        self.assertEqual(len(payload['items']), 1)
        self.assertEqual(payload['items'][0]['student_answer']['text'], 'London')
        self.assertEqual(payload['items'][0]['correct_answer']['text'], 'Paris')
        self.assertFalse(payload['items'][0]['is_correct'])

    def test_html_question_and_image_preserved(self):
        quiz = Quiz.objects.create(category=self.category, topic='Math HTML')
        html_q = (
            '<p>If <img alt="x" src="data:image/png;base64,abc" width="8" /> '
            '≠ 0, which must be an integer?</p>'
        )
        option_html = '<img alt="optA" src="data:image/png;base64,def" width="9" />'
        question = QuizQuestion.objects.create(
            quiz=quiz,
            order=1,
            question=html_q,
            answer_options=[option_html, 'B'],
            correct_answer=option_html,
        )
        result = QuizResult.objects.create(
            student=self.student,
            quiz=quiz,
            given_answers={str(question.pk): 0},
            total_score=1,
        )
        payload = build_quiz_result_word_export(result)
        self.assertTrue(payload['items'][0]['question']['is_html'])
        self.assertIn('<img alt="x"', payload['items'][0]['question']['value'])
        self.assertIn('≠', payload['items'][0]['question']['value'])
        self.assertTrue(payload['items'][0]['student_answer']['is_html'])
        self.assertIn('<img alt="optA"', payload['items'][0]['student_answer']['value'])

    def test_customer_owner_name_used(self):
        quiz = Quiz.objects.create(category=self.category, topic='Customer quiz')
        question = QuizQuestion.objects.create(
            quiz=quiz,
            order=1,
            question='Q?',
            answer_options=['A', 'B'],
            correct_answer='A',
        )
        result = QuizResult.objects.create(
            customer=self.customer,
            quiz=quiz,
            given_answers={str(question.pk): 0},
            total_score=1,
        )
        payload = build_quiz_result_word_export(result)
        self.assertEqual(payload['student_name'], self.customer.full_name)

    def test_listening_and_essay_not_supported(self):
        listening = Quiz.objects.create(
            category=self.category,
            topic='Listening',
            is_listening=True,
        )
        essay = Quiz.objects.create(
            category=self.category,
            topic='Writing',
            is_essay=True,
        )
        self.assertFalse(quiz_result_supports_word_export(listening))
        self.assertFalse(quiz_result_supports_word_export(essay))
        listening_result = QuizResult.objects.create(
            student=self.student,
            quiz=listening,
            total_score=5,
        )
        essay_result = QuizResult.objects.create(
            student=self.student,
            quiz=essay,
            student_submission='Hello',
        )
        self.assertIsNone(build_quiz_result_word_export(listening_result))
        self.assertIsNone(build_quiz_result_word_export(essay_result))
