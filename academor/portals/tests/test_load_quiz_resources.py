from django.contrib.auth import get_user_model

from django.test import TestCase

from portals.models import Quiz, QuizQuestion
from portals.utils.quiz_resource_loader import RESOURCES_DIR, load_resource_file
from projects.models.service_models import Service

User = get_user_model()


class LoadQuizResourcesTests(TestCase):
    def setUp(self):
        Service.objects.get_or_create(
            slug='general-english',
            defaults={'name_az': 'General English', 'name_en': 'General English', 'is_active': True},
        )

    def test_load_resource_creates_quiz_with_inline_questions(self):
        path = RESOURCES_DIR / 'a1_quiz_1.json'
        result = load_resource_file(path)

        self.assertEqual(result['total'], 30)
        quiz = Quiz.objects.get(pk=result['quiz_id'])
        self.assertEqual(quiz.questions.count(), 30)
        self.assertEqual(
            QuizQuestion.objects.filter(quiz=quiz, source_key__startswith='a1_quiz_1:').count(),
            30,
        )
