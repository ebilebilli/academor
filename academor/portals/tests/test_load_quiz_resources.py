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

    def test_load_dropdown_quiz_marks_questions(self):
        path = RESOURCES_DIR / 'number_6_quiz.json'
        result = load_resource_file(path)

        self.assertEqual(result['total'], 9)
        quiz = Quiz.objects.get(pk=result['quiz_id'])
        questions = list(quiz.questions.order_by('order', 'id'))
        self.assertEqual(len(questions), 9)
        self.assertTrue(all(q.is_dropdown for q in questions))
        self.assertTrue(all(q.question_type == QuizQuestion.QuestionType.MCQ for q in questions))
        self.assertEqual(len(questions[0].answer_options), 12)

    def test_parse_dropdown_quiz_resource(self):
        from portals.utils.quiz_resource_loader import parse_resource_file

        parsed = parse_resource_file(RESOURCES_DIR / 'number_6_quiz.json')
        self.assertEqual(len(parsed['questions']), 9)
        self.assertTrue(all(item['is_dropdown'] for item in parsed['questions']))
        self.assertTrue(all(
            item['question_type'] == QuizQuestion.QuestionType.MCQ
            for item in parsed['questions']
        ))

    def test_dropdown_question_type_normalizes_to_mcq_flag(self):
        from portals.utils.quiz_resource_loader import _normalize_question

        item = _normalize_question(
            {
                'id': 1,
                'question': 'First, she...',
                'question_type': 'dropdown',
                'options': ['went to London.', 'came home.'],
                'answer': 0,
            },
            0,
            'demo',
        )
        self.assertEqual(item['question_type'], QuizQuestion.QuestionType.MCQ)
        self.assertTrue(item['is_dropdown'])
        self.assertEqual(item['correct_option_index'], 0)
