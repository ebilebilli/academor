"""Public SAT / IELTS level tests that run portal quizzes."""

import json

from django.test import TestCase
from django.urls import reverse

from portals.models import Lead, Quiz, QuizCategory, QuizQuestion
from portals.models.reading_models import ReadingPassage, ReadingQuestion, ReadingQuestionType
from projects.models import Option, Question, Test, UserResult
from projects.utils import level_exam as lx


def _sat_quizzes(category):
    rw = Quiz(category=category, topic='Practice Test 6 — Reading and Writing', is_sat=True, sat_section='reading')
    rw.save()
    for index, correct in enumerate((0, 1, 2), start=1):
        QuizQuestion.objects.create(
            quiz=rw, order=index, question=f'<p>RW question {index}</p>',
            answer_options=['A', 'B', 'C', 'D'], correct_option_index=correct,
        )
    math = Quiz(category=category, topic='Practice Test 6 — Math', is_sat=True, sat_section='algebra')
    math.save()
    QuizQuestion.objects.create(
        quiz=math, order=1, question='<p>3x = 6, x?</p>', answer_options=['1', '2', '3', '4'], correct_option_index=1,
    )
    QuizQuestion.objects.create(
        quiz=math, order=2, question='<p>Slope?</p>', question_type='spr', spr_correct_answers=['2'], correct_answer='2',
    )
    return rw, math


class LevelExamUtilsTests(TestCase):
    def setUp(self):
        self.category = QuizCategory.objects.create(name='Exam sections')

    def test_sat_practice_quizzes_stored_as_plain_mcq_are_sat_sections(self):
        rw, math = _sat_quizzes(self.category)
        self.assertEqual(lx.section_kind(rw), lx.SECTION_SAT_RW)
        self.assertEqual(lx.section_kind(math), lx.SECTION_SAT_MATH)
        self.assertEqual(lx.section_format(math), lx.FORMAT_VARIANT)
        self.assertEqual(lx.section_minutes(rw), 64)
        self.assertEqual(lx.section_minutes(math), 70)

    def test_reading_and_writing_comes_before_math(self):
        rw, math = _sat_quizzes(self.category)
        test = Test.objects.create(title_az='SAT', is_active=True)
        test.portal_quizzes.set([math, rw])
        self.assertEqual([q.pk for q in lx.exam_quizzes(test)], [rw.pk, math.pk])
        self.assertEqual(lx.exam_kind(lx.exam_quizzes(test)), lx.KIND_SAT)

    def test_portal_time_limit_wins_over_the_default(self):
        rw, _ = _sat_quizzes(self.category)
        rw.is_time_limited = True
        rw.time_limit_minutes = 32
        self.assertEqual(lx.section_minutes(rw), 32)

    def test_ielts_bands(self):
        self.assertEqual(lx.ielts_band(lx.KIND_IELTS_LISTENING, 30, 40), 7.0)
        self.assertEqual(lx.ielts_band(lx.KIND_IELTS_READING, 30, 40), 7.0)
        self.assertEqual(lx.ielts_band(lx.KIND_IELTS_READING, 27, 40), 6.5)
        self.assertEqual(lx.ielts_band(lx.KIND_IELTS_LISTENING, 26, 40), 6.5)
        # a 20-question test is scaled to 40
        self.assertEqual(lx.ielts_band(lx.KIND_IELTS_READING, 15, 20), 7.0)
        self.assertIsNone(lx.ielts_band(lx.KIND_SAT, 10, 20))


class SatLevelExamFlowTests(TestCase):
    def setUp(self):
        category = QuizCategory.objects.create(name='Exam sections')
        self.rw, self.math = _sat_quizzes(category)
        self.test = Test.objects.create(title_az='SAT sınaq testi', title_en='SAT practice test', is_active=True)
        self.test.portal_quizzes.set([self.rw, self.math])
        self.intro_url = reverse('projects:test-take', kwargs={'test_id': self.test.pk})

    def _section(self, n, action=''):
        name = {'': 'level-exam-section', 'start': 'level-exam-start', 'submit': 'level-exam-submit'}[action]
        return reverse(f'projects:{name}', kwargs={'test_id': self.test.pk, 'section': n})

    def _submit(self, n, answers, trigger='manual'):
        return self.client.post(
            self._section(n, 'submit'),
            data=json.dumps({'answers': answers, 'completion_trigger': trigger}),
            content_type='application/json',
        )

    def _start(self):
        with self.captureOnCommitCallbacks(execute=True):
            return self.client.post(self.intro_url, {'first_name': 'Aysel Namizəd', 'number': '+994 50 111 22 33'})

    def test_intro_shows_sections_offer_and_form(self):
        response = self.client.get(self.intro_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'level-exam-intro.html')
        content = response.content.decode()
        self.assertIn('name="number"', content)
        self.assertIn('WhatsApp', content)
        self.assertIn('50%', content)

    def test_name_and_phone_are_required_before_the_test(self):
        response = self.client.post(self.intro_url, {'first_name': '', 'number': '1'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(UserResult.objects.count(), 0)
        self.assertEqual(self.client.get(self._section(1)).status_code, 302)

    def test_full_attempt(self):
        response = self._start()
        self.assertRedirects(response, self._section(1), fetch_redirect_response=False)
        result = UserResult.objects.get()
        self.assertEqual(result.details['kind'], 'sat')
        self.assertEqual(result.details['status'], 'started')
        self.assertTrue(Lead.objects.filter(level_test_result=result).exists())

        page = self.client.get(self._section(1))
        self.assertEqual(page.status_code, 200)
        self.assertTemplateUsed(page, 'portals/student/quiz_take.html')
        self.assertTemplateUsed(page, 'level-exam-base.html')
        self.assertContains(page, 'data-time-limit-sec="3840"')

        # cannot jump ahead
        self.assertRedirects(self.client.get(self._section(2)), self._section(1), fetch_redirect_response=False)

        self.assertEqual(self.client.post(self._section(1, 'start')).json(), {'success': True})
        q1, q2, q3 = self.rw.questions.order_by('order')
        data = self._submit(1, {str(q1.pk): 0, str(q2.pk): 3}).json()
        self.assertTrue(data['success'])
        self.assertEqual(data['next_url'], self._section(2))
        self.assertNotIn('questions', data)  # no answer key goes back to the browser

        m1, m2 = self.math.questions.order_by('order')
        self.client.post(self._section(2, 'start'))
        with self.captureOnCommitCallbacks(execute=True):
            data = self._submit(2, {str(m1.pk): 1, str(m2.pk): '2'}, trigger='time_limit').json()
        self.assertEqual(data['next_url'], reverse('projects:level-exam-result', kwargs={'test_id': self.test.pk}))

        result.refresh_from_db()
        self.assertEqual(result.details['status'], 'finished')
        rw_row, math_row = result.details['sections']
        self.assertEqual((rw_row['correct'], rw_row['total'], rw_row['wrong'], rw_row['unanswered']), (1, 3, [2], [3]))
        self.assertEqual((math_row['correct'], math_row['total'], math_row['trigger']), (2, 2, 'time_limit'))
        self.assertEqual(result.level, 'R&W 1/3 · Math 2/2')
        self.assertEqual(result.score, 3)

        lead = Lead.objects.get(level_test_result=result)
        self.assertEqual(lead.level, 'SAT 1/3+2/2')
        self.assertTrue(lead.activities.filter(text__contains='səhv: 2').exists())

        page = self.client.get(data['next_url'])
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, 'data-lx-count="1">1</span><small>/3</small>', html=False)
        self.assertContains(page, 'data-lx-count="2">2</span><small>/2</small>', html=False)
        self.assertContains(page, '--pct: 33%')

    def test_double_submit_does_not_overwrite(self):
        self._start()
        self.client.post(self._section(1, 'start'))
        q1 = self.rw.questions.order_by('order').first()
        self._submit(1, {str(q1.pk): 0})
        again = self._submit(1, {}).json()
        self.assertEqual(again['next_url'], self._section(2))
        result = UserResult.objects.get()
        self.assertEqual(result.details['sections'][0]['correct'], 1)

    def test_result_waits_for_the_last_section(self):
        self._start()
        result_url = reverse('projects:level-exam-result', kwargs={'test_id': self.test.pk})
        self.assertRedirects(self.client.get(result_url), self._section(1), fetch_redirect_response=False)


class IeltsReadingLevelExamTests(TestCase):
    def setUp(self):
        category = QuizCategory.objects.create(name='IELTS sections')
        self.quiz = Quiz.objects.create(category=category, topic='IELTS Reading level test', is_reading=True, is_ielts=True)
        passage = ReadingPassage.objects.create(quiz=self.quiz, order=1, title='Passage 1', body='<p>Text.</p>')
        self.questions = [
            ReadingQuestion.objects.create(
                passage=passage, order=i, question_type=ReadingQuestionType.TFNG,
                question=f'<p>Statement {i}</p>', correct_answer='True',
            )
            for i in range(1, 5)
        ]
        self.test = Test.objects.create(title_az='IELTS Reading', is_active=True)
        self.test.portal_quizzes.set([self.quiz])

    def test_intro_shows_the_ielts_discount(self):
        url = reverse('projects:test-take', kwargs={'test_id': self.test.pk})
        response = self.client.get(url)
        self.assertEqual(response.context['ielts_discount_percent'], 25)
        self.assertContains(response, '−25%')

    def test_band_on_result(self):
        url = reverse('projects:test-take', kwargs={'test_id': self.test.pk})
        self.client.post(url, {'first_name': 'Murad Namizəd', 'number': '+994 55 222 33 44'})
        section = reverse('projects:level-exam-section', kwargs={'test_id': self.test.pk, 'section': 1})
        page = self.client.get(section)
        self.assertTemplateUsed(page, 'portals/student/quiz_take_reading.html')
        self.client.post(reverse('projects:level-exam-start', kwargs={'test_id': self.test.pk, 'section': 1}))
        answers = {str(q.pk): 'True' for q in self.questions[:3]}
        self.client.post(
            reverse('projects:level-exam-submit', kwargs={'test_id': self.test.pk, 'section': 1}),
            data=json.dumps({'answers': answers}), content_type='application/json',
        )
        result = UserResult.objects.get()
        row = result.details['sections'][0]
        self.assertEqual((row['correct'], row['total']), (3, 4))
        self.assertEqual(row['band_label'], '7.0')  # 3/4 -> 30/40
        self.assertEqual(result.level, 'Band 7.0 (3/4)')
        page = self.client.get(reverse('projects:level-exam-result', kwargs={'test_id': self.test.pk}))
        self.assertContains(page, '7.0')
        self.assertContains(page, '--pct: 77.8%')  # band 7.0 on the 0-9 scale, dot decimal in any language


class TestsPageTests(TestCase):
    def setUp(self):
        from django.core.cache import cache

        cache.clear()  # get_tests is cached across requests

    def test_exam_and_level_tests_are_listed_separately(self):
        category = QuizCategory.objects.create(name='Exam sections')
        rw, math = _sat_quizzes(category)
        sat = Test.objects.create(title_az='SAT sınaq testi', is_active=True)
        sat.portal_quizzes.set([rw, math])
        level = Test.objects.create(title_az='Səviyyə testi', is_active=True)
        question = Question.objects.create(test=level, text='Q', order=1)
        Option.objects.create(question=question, text='a', is_correct=True)

        response = self.client.get(reverse('projects:tests-page'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual([card['id'] for card in response.context['exam_tests']], [sat.pk])
        self.assertEqual(response.context['exam_tests'][0]['question_count'], 5)
        self.assertEqual([t['id'] for t in response.context['tests']], [level.pk])

    def test_classic_level_test_still_uses_its_own_page_with_the_cefr_scale(self):
        level = Test.objects.create(title_az='Səviyyə testi', is_active=True)
        response = self.client.get(reverse('projects:test-take', kwargs={'test_id': level.pk}))
        self.assertTemplateUsed(response, 'test-take.html')
        self.assertContains(response, 'lt-cefr-heading')

    def test_admin_order_decides_the_list_and_cefr_left_the_tests_page(self):
        category = QuizCategory.objects.create(name='Exam sections')
        rw, math = _sat_quizzes(category)
        sat = Test.objects.create(title_az='SAT sınaq testi', is_active=True, order=2)
        sat.portal_quizzes.set([rw, math])
        level = Test.objects.create(title_az='Səviyyə testi', is_active=True, order=1)
        response = self.client.get(reverse('projects:tests-page'))
        self.assertEqual([card['id'] for card in response.context['test_cards']], [level.pk, sat.pk])
        self.assertEqual([card['kind'] for card in response.context['test_cards']], ['level', 'sat'])
        self.assertNotContains(response, 'lt-cefr-heading')


class LevelExamAdminTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model

        self.admin = get_user_model().objects.create_superuser('exam-admin', 'exam-admin@example.com', 'pass12345')
        self.client.force_login(self.admin)
        category = QuizCategory.objects.create(name='Exam sections')
        self.rw, self.math = _sat_quizzes(category)
        self.test = Test.objects.create(title_az='SAT sınaq testi', is_active=True)
        self.test.portal_quizzes.set([self.rw, self.math])

    def test_test_admin_shows_portal_quizzes_and_format(self):
        changelist = self.client.get(reverse('admin:projects_test_changelist'))
        self.assertContains(changelist, 'Portal exam: Reading and Writing + Math')
        change = self.client.get(reverse('admin:projects_test_change', args=[self.test.pk]))
        self.assertContains(change, 'portal_quizzes')

    def test_result_admin_shows_the_exam_report(self):
        result = UserResult.objects.create(
            first_name='Aysel', number='+994501112233', test=self.test, score=3, level='R&W 1/3 · Math 2/2',
            details={'kind': 'sat', 'status': 'finished', 'sections': [
                {'label': 'Reading and Writing', 'correct': 1, 'total': 3, 'wrong': [2], 'unanswered': [3],
                 'duration_sec': 600, 'trigger': 'manual'},
            ]},
        )
        response = self.client.get(reverse('admin:projects_userresult_change', args=[result.pk]))
        self.assertContains(response, 'Wrong (question no.)')
        self.assertContains(response, '<td>2</td>', html=False)
        self.assertContains(self.client.get(reverse('admin:projects_userresult_changelist')), 'Finished')


class SatScoreTableTests(TestCase):
    def test_parse_rows_ranges_and_blanks(self):
        table = lx.parse_sat_score_table('Raw  RW  Math\n0 200 200\n40 600-640 620–660\n58 - 750\nnot a row\n41 900 300')
        self.assertEqual(table['rw'], {0: (200, 200), 40: (600, 640)})
        self.assertEqual(table['math'], {0: (200, 200), 40: (620, 660), 58: (750, 750), 41: (300, 300)})

    def test_result_shows_estimated_sat_score_print_and_story(self):
        category = QuizCategory.objects.create(name='Exam sections')
        rw, math = _sat_quizzes(category)
        test = Test.objects.create(title_az='SAT', is_active=True, sat_score_table='0 200 200\n1 300 400\n2 400 500\n3 500 600')
        test.portal_quizzes.set([rw, math])
        self.client.post(reverse('projects:test-take', kwargs={'test_id': test.pk}), {'first_name': 'Aysel Namizəd', 'number': '+994 50 111 22 33'})
        for section, quiz, answers in ((1, rw, {str(rw.questions.order_by('order')[0].pk): 0}), (2, math, {})):
            self.client.post(reverse('projects:level-exam-start', kwargs={'test_id': test.pk, 'section': section}))
            self.client.post(
                reverse('projects:level-exam-submit', kwargs={'test_id': test.pk, 'section': section}),
                data=json.dumps({'answers': answers}), content_type='application/json',
            )
        page = self.client.get(reverse('projects:level-exam-result', kwargs={'test_id': test.pk}))
        self.assertEqual(page.context['sat_total'], '500')  # R&W 1 -> 300, Math 0 -> 200
        self.assertContains(page, 'data-lx-print')
        self.assertContains(page, 'id="lx-story-data"')
        self.assertEqual(page.context['story']['total'], '500 / 1600')


class LevelExamAdminPrintTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model

        self.client.force_login(get_user_model().objects.create_superuser('exam-admin2', 'a2@example.com', 'pass12345'))
        test = Test.objects.create(title_az='IELTS Reading', is_active=True)
        self.result = UserResult.objects.create(
            first_name='Murad', number='+994551112233', test=test, score=30, level='Band 7.0 (30/40)',
            details={'kind': 'ielts_reading', 'status': 'finished', 'sections': [
                {'label': 'Reading', 'correct': 30, 'total': 40, 'band_label': '7.0', 'wrong': [4, 9],
                 'unanswered': [], 'duration_sec': 3300, 'trigger': 'manual'},
            ]},
        )

    def test_print_page_and_bulk_action(self):
        url = reverse('admin:projects_userresult_print')
        page = self.client.get(f'{url}?ids={self.result.pk}')
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, 'Band 7.0 (30/40)')
        self.assertContains(page, '4, 9')
        response = self.client.post(reverse('admin:projects_userresult_changelist'), {
            'action': 'print_selected', '_selected_action': [self.result.pk],
        })
        self.assertRedirects(response, f'{url}?ids={self.result.pk}', fetch_redirect_response=False)
        self.assertContains(self.client.get(reverse('admin:projects_userresult_changelist')), 'Print / PDF')
