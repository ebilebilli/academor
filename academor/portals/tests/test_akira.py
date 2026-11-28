"""AKIRA: course registry, analytics, the budget guard and the two result pages."""

import json
from decimal import Decimal
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from portals.akira import analytics, client, prompts, service
from portals.akira.courses import SAT_MATH, SAT_VERBAL, active_course, course_for_quiz, get_course
from portals.akira.skills import question_skill
from portals.models import AkiraMaterial, AkiraReport, AkiraUsage, Quiz, QuizCategory, QuizQuestion, QuizResult, StudentProfile
from portals.tests.portal_helpers import portal_client_login
from projects.models import Test, UserResult

User = get_user_model()


def _completion(text='Xətti tənlikləri yaxşı bilirsən. Bu həftə hər gün 10 sual həll et.'):
    return client.Completion(text=text, model='claude-opus-5-5', input_tokens=1000, output_tokens=200)


def _math_quiz(category, *, source=True):
    quiz = Quiz(category=category, topic='SAT Math drill', is_sat=True, sat_section='algebra')
    quiz.save()
    for index, correct in enumerate((0, 1, 2, 0), start=1):
        QuizQuestion.objects.create(
            quiz=quiz, order=index, question=f'<p>Math {index}</p>',
            answer_options=['A', 'B', 'C', 'D'], correct_option_index=correct,
            source_key=f'academor_sat_math_test_1:q{index}' if source else '',
        )
    return quiz


class CourseRegistryTests(TestCase):
    def test_sat_sections_are_on_and_other_courses_wait_for_their_turn(self):
        self.assertEqual(active_course('sat-math'), SAT_MATH)
        self.assertEqual(active_course('sat_verbal'), SAT_VERBAL)
        for code in ('ielts', 'general_english', 'fmva', 'dipifr'):
            self.assertIsNotNone(get_course(code))
            self.assertIsNone(active_course(code))

    def test_sat_quiz_maps_to_its_section(self):
        category = QuizCategory.objects.create(name='SAT')
        self.assertEqual(course_for_quiz(_math_quiz(category)), SAT_MATH)
        rw = Quiz(category=category, topic='RW', is_sat=True, sat_section='reading')
        rw.save()
        self.assertEqual(course_for_quiz(rw), SAT_VERBAL)

    def test_skills_come_from_the_resource_files(self):
        question = QuizQuestion(source_key='academor_sat_math_test_1:q1')
        domain, skill = question_skill(question)
        self.assertEqual(domain, 'Algebra')
        self.assertTrue(skill)
        self.assertEqual(question_skill(QuizQuestion(source_key='')), ('', ''))


class AnalyticsTests(TestCase):
    def _items(self, statuses, domain='Algebra'):
        return [analytics.build_item(n, s, domain, 'Linear equations') for n, s in enumerate(statuses, start=1)]

    def test_section_facts(self):
        items = self._items(['correct'] * 4, 'Algebra') + [
            analytics.build_item(5, 'wrong', 'Advanced Math', 'Nonlinear functions'),
            analytics.build_item(6, 'blank', 'Advanced Math', 'Nonlinear functions'),
        ]
        facts = analytics.analyse_section(items, SAT_MATH, duration_sec=600, scaled='590–640')
        self.assertEqual((facts['correct'], facts['total'], facts['percent']), (4, 6, 67))
        self.assertEqual(facts['weak_domains'], ['Advanced Math'])
        self.assertEqual(facts['strong_domains'], ['Algebra'])
        self.assertEqual(facts['wrong_numbers'], [5])
        self.assertEqual(facts['blank_numbers'], [6])
        self.assertEqual(facts['sec_per_question'], 100)
        self.assertEqual(facts['target_sec_per_question'], 95)
        self.assertEqual(facts['scale_max'], 800)
        self.assertEqual(facts['weak_skills'][0], {'skill': 'Nonlinear functions', 'missed': 2})

    def test_time_pressure_means_misses_at_the_end(self):
        late = analytics.analyse_section(self._items(['correct'] * 6 + ['wrong', 'blank', 'wrong']), SAT_MATH)
        early = analytics.analyse_section(self._items(['wrong', 'wrong', 'wrong'] + ['correct'] * 6), SAT_MATH)
        self.assertTrue(analytics.time_pressure(late))
        self.assertFalse(analytics.time_pressure(early))


class NumberGuardTests(TestCase):
    def test_only_numbers_from_the_facts_pass(self):
        facts = {'correct': 31, 'total': 44, 'scaled': '590–640'}
        self.assertEqual(prompts.unknown_numbers('31 sual düzgündür, bal 590–640, 3 gün məşq et.', facts), set())
        self.assertEqual(prompts.unknown_numbers('Balın 700 olacaq.', facts), {700})
        self.assertEqual(prompts.unknown_numbers('Hər gün 10 sual həll et, 85% düzgün olsun.', facts), {85})


@override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}})
class PortalReportTests(TestCase):
    def setUp(self):
        self.category = QuizCategory.objects.create(name='SAT Math')
        self.quiz = _math_quiz(self.category)
        self.user = User.objects.create_user(username='Aysel Namizəd', password='x')
        self.student = StudentProfile.objects.create(user=self.user)
        q1, q2, q3, q4 = self.quiz.questions.order_by('order')
        self.result = QuizResult.objects.create(
            student=self.student, quiz=self.quiz, total_score=2, duration_sec=400,
            given_answers={str(q1.pk): 0, str(q2.pk): 1, str(q3.pk): 0},
        )
        self.url = reverse('portals:akira-quiz-result', kwargs={'result_pk': self.result.pk})

    def test_report_facts_use_the_breakdown(self):
        report = service.report_for_quiz_result(self.result)
        self.assertEqual(report.course_code, 'sat-math')
        facts = report.facts
        self.assertEqual((facts['correct'], facts['wrong'], facts['blank'], facts['total']), (2, 1, 1, 4))
        self.assertEqual(facts['wrong_numbers'], [3])
        self.assertEqual(facts['blank_numbers'], [4])
        self.assertTrue(facts['domains'])

    @mock.patch.object(client, 'is_configured', return_value=True)
    @mock.patch.object(client, 'complete')
    def test_comment_is_written_once_and_logged(self, complete, _configured):
        complete.return_value = _completion()
        report = service.report_for_quiz_result(self.result)
        first = service.write_comment(report.pk)
        second = service.write_comment(report.pk)
        self.assertEqual(first.status, AkiraReport.Status.READY)
        self.assertEqual(second.comment, first.comment)
        self.assertEqual(complete.call_count, 1)
        usage = AkiraUsage.objects.get()
        self.assertTrue(usage.ok)
        self.assertEqual(usage.cost_usd, Decimal('0.00800'))  # 1000 in * $4 + 200 out * $20 per million

    @mock.patch.object(client, 'is_configured', return_value=True)
    @mock.patch.object(client, 'complete')
    def test_invented_numbers_are_not_shown(self, complete, _configured):
        complete.return_value = _completion('Növbəti dəfə balın 750 olacaq.')
        report = service.write_comment(service.report_for_quiz_result(self.result).pk)
        self.assertEqual(report.status, AkiraReport.Status.FAILED)
        self.assertEqual(report.comment, '')
        self.assertEqual(service.report_payload(report)['status'], 'pending')  # one more try is allowed
        service.write_comment(report.pk)
        report.refresh_from_db()
        self.assertEqual(service.report_payload(report)['status'], 'failed')
        self.assertEqual(complete.call_count, 2)

    @mock.patch.object(client, 'complete')
    def test_without_a_key_akira_stays_silent(self, complete):
        with mock.patch.dict('os.environ', {'ANTHROPIC_API_KEY': ''}):
            report = service.write_comment(service.report_for_quiz_result(self.result).pk)
        self.assertEqual(report.status, AkiraReport.Status.SKIPPED)
        complete.assert_not_called()

    @mock.patch.object(client, 'is_configured', return_value=True)
    @mock.patch.object(client, 'complete')
    def test_monthly_budget_stops_new_comments(self, complete, _configured):
        AkiraUsage.objects.create(purpose='x', model_name='claude-opus-5-5', cost_usd=Decimal('80'))
        report = service.write_comment(service.report_for_quiz_result(self.result).pk)
        self.assertEqual((report.status, report.error), (AkiraReport.Status.SKIPPED, 'monthly budget reached'))
        complete.assert_not_called()

    @mock.patch.object(client, 'is_configured', return_value=True)
    @mock.patch.object(client, 'complete')
    def test_materials_for_weak_areas_go_into_the_prompt(self, complete, _configured):
        complete.return_value = _completion()
        AkiraMaterial.objects.create(course_code='sat-math', title='Academor: tənliklər', content='Əvvəl tərəfləri sadələşdir.')
        AkiraMaterial.objects.create(course_code='ielts', title='IELTS note', content='Not for SAT.')
        service.write_comment(service.report_for_quiz_result(self.result).pk)
        message = complete.call_args[0][1]
        self.assertIn('Academor: tənliklər', message)
        self.assertNotIn('IELTS note', message)

    @mock.patch.object(client, 'is_configured', return_value=True)
    @mock.patch.object(client, 'complete')
    def test_endpoint_and_score_page(self, complete, _configured):
        complete.return_value = _completion()
        browser = Client()
        portal_client_login(browser, self.user)
        page = browser.get(reverse('portals:student-score-detail', kwargs={'result_pk': self.result.pk}))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, 'data-akira-card')
        self.assertContains(page, 'akira.js')
        data = browser.post(self.url, data='{}', content_type='application/json').json()
        self.assertEqual(data['status'], 'ready')
        self.assertIn('Xətti tənlikləri', data['comment'])
        vote = browser.post(self.url, data=json.dumps({'helpful': True}), content_type='application/json').json()
        self.assertTrue(vote['helpful'])

    def test_other_students_cannot_read_the_report(self):
        other = User.objects.create_user(username='Murad Əliyev', password='x')
        StudentProfile.objects.create(user=other)
        browser = Client()
        portal_client_login(browser, other)
        self.assertEqual(browser.post(self.url, data='{}', content_type='application/json').status_code, 404)

    def test_quizzes_outside_akira_have_no_card(self):
        general = Quiz(category=self.category, topic='Grammar')
        general.save()
        QuizQuestion.objects.create(quiz=general, order=1, question='<p>Q</p>', answer_options=['a', 'b'], correct_option_index=0)
        result = QuizResult.objects.create(student=self.student, quiz=general, total_score=1, given_answers={})
        self.assertIsNone(service.report_for_quiz_result(result))


class PublicTestReportTests(TestCase):
    def setUp(self):
        category = QuizCategory.objects.create(name='Exam sections')
        rw = Quiz(category=category, topic='Practice — Reading and Writing', is_sat=True, sat_section='reading')
        rw.save()
        for index in range(1, 4):
            QuizQuestion.objects.create(quiz=rw, order=index, question=f'<p>RW {index}</p>', answer_options=['A', 'B'], correct_option_index=0)
        self.math = _math_quiz(category)
        self.rw = rw
        self.test = Test.objects.create(title_az='SAT sınaq testi', is_active=True)
        self.test.portal_quizzes.set([rw, self.math])

    def _finish(self):
        self.client.post(reverse('projects:test-take', kwargs={'test_id': self.test.pk}), {'first_name': 'Aysel Namizəd', 'number': '+994 50 111 22 33'})
        sections = ((1, self.rw, {str(self.rw.questions.order_by('order')[0].pk): 0}), (2, self.math, {}))
        for section, quiz, answers in sections:
            self.client.post(reverse('projects:level-exam-start', kwargs={'test_id': self.test.pk, 'section': section}))
            self.client.post(
                reverse('projects:level-exam-submit', kwargs={'test_id': self.test.pk, 'section': section}),
                data=json.dumps({'answers': answers}), content_type='application/json',
            )

    @mock.patch.object(client, 'is_configured', return_value=True)
    @mock.patch.object(client, 'complete')
    def test_result_page_shows_akira_and_the_comment_endpoint_works(self, complete, _configured):
        complete.return_value = _completion('Mətn suallarında başlanğıc yaxşıdır. Math-da hər gün 10 sual həll et.')
        self._finish()
        page = self.client.get(reverse('projects:level-exam-result', kwargs={'test_id': self.test.pk}))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, 'data-akira-card')
        report = AkiraReport.objects.get(user_result=UserResult.objects.get())
        self.assertEqual(report.kind, AkiraReport.Kind.PUBLIC_TEST)
        self.assertEqual(len(report.facts['sections']), 2)
        self.assertEqual(report.facts['summary']['total'], 7)
        url = reverse('projects:level-exam-akira', kwargs={'test_id': self.test.pk})
        data = self.client.post(url, data='{}', content_type='application/json').json()
        self.assertEqual(data['status'], 'ready')
        self.assertEqual(complete.call_args[0][1].count('FACTS'), 1)
        self.assertIn('visitor', complete.call_args[0][1])

    def test_another_browser_cannot_ask_for_the_comment(self):
        self._finish()
        self.client.get(reverse('projects:level-exam-result', kwargs={'test_id': self.test.pk}))
        stranger = Client()
        url = reverse('projects:level-exam-akira', kwargs={'test_id': self.test.pk})
        self.assertEqual(stranger.post(url, data='{}', content_type='application/json').status_code, 404)
