"""Academor SAT practice tests 2–10 (Math and Reading and Writing) load into the portal correctly."""

import json

from django.test import TestCase

from portals.models import Quiz
from portals.utils.quiz_resource_loader import SAT_RESOURCES_DIR, load_resource_file
from portals.utils.sat_spr_validation import validate_spr_answer
from projects.models.service_models import Service

TESTS = range(2, 11)


class SatPracticeTestFilesTests(TestCase):
    def setUp(self):
        for slug, name in (('sat-math', 'SAT Math'), ('sat-verbal', 'SAT Verbal')):
            Service.objects.get_or_create(slug=slug, defaults={'name_az': name, 'name_en': name, 'is_active': True})

    def _data(self, kind, number):
        return json.loads((SAT_RESOURCES_DIR / f'academor_sat_{kind}_test_{number}.json').read_text(encoding='utf-8'))

    def test_math_files_follow_the_blueprint(self):
        for number in TESTS:
            data = self._data('math', number)
            questions = data['questions']
            self.assertEqual(len(questions), 44, number)
            for module in (1, 2):
                rows = [q for q in questions if q['module'] == module]
                self.assertEqual(len(rows), 22, (number, module))
                spr = [i + 1 for i, q in enumerate(rows) if q.get('question_type') == 'spr']
                self.assertEqual(spr, [6, 7, 13, 14, 20, 21], (number, module))
            for q in questions:
                if q.get('question_type') == 'spr':
                    for answer in q['spr_correct_answers']:
                        self.assertTrue(
                            validate_spr_answer(answer, q['spr_correct_answers']).get('is_correct'),
                            (number, q['id'], answer),
                        )
                else:
                    self.assertEqual(len(set(q['options'])), 4, (number, q['id']))
                    self.assertIn(q['correct'], q['options'], (number, q['id']))

    def test_reading_and_writing_files_follow_the_blueprint(self):
        for number in TESTS:
            data = self._data('verbal', number)
            questions = data['questions']
            self.assertEqual(len(questions), 54, number)
            for module in (1, 2):
                rows = [q for q in questions if q['module'] == module]
                self.assertEqual(len(rows), 27, (number, module))
                graphics = [q for q in rows if q['skill'] == 'Command of Evidence: Quantitative']
                self.assertEqual(len(graphics), 3, (number, module))
                self.assertTrue(all('<img' in q['question'] for q in graphics), (number, module))
            for q in questions:
                self.assertEqual(len(set(q['options'])), 4, (number, q['id']))
                self.assertIn(q['correct'], q['options'], (number, q['id']))
                self.assertNotIn('___<', q['question'].replace('<strong>______</strong>', ''), (number, q['id']))

    def test_every_file_loads_into_the_portal(self):
        for number in TESTS:
            for kind, total in (('math', 44), ('verbal', 54)):
                result = load_resource_file(SAT_RESOURCES_DIR / f'academor_sat_{kind}_test_{number}.json')
                quiz = Quiz.objects.get(pk=result['quiz_id'])
                self.assertEqual(quiz.questions.count(), total, (kind, number))
                self.assertTrue(quiz.is_sat, (kind, number))
        self.assertEqual(Quiz.objects.filter(topic__startswith='Academor SAT Practice Test').count(), 18)
