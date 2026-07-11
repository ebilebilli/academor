"""Integration tests for portal quiz take/submit and IELTS/SAT mock flows."""

import json

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from portals.models import (
    IeltsMockTestAttempt,
    Quiz,
    QuizAssignment,
    QuizCategory,
    QuizQuestion,
    QuizResult,
    StudentMockAccess,
    StudentProfile,
    StudyGroup,
    TeacherCourseSpecialization,
    TeacherProfile,
)
from portals.tests.group_helpers import link_study_group_services
from portals.tests.portal_helpers import (
    assign_quiz_to_student,
    ensure_active_portal_services,
    portal_client_login,
)
from portals.tests.test_quiz_visibility import _ensure_active_portal_services as _visibility_services
from portals.utils.ielts_mock_test import (
    SAT_SERVICE,
    get_mock_take_url,
    pick_random_section_quizzes,
    resolve_mock_take_request,
    start_mock_test_attempt,
)
from portals.utils.mock_programs import resolve_take_url_kind
from portals.utils.queries import get_student_quiz_take_data
from portals.utils.student_courses import quiz_visible_to_student

User = get_user_model()


class PortalMockQuizIntegrationTests(TestCase):
    def setUp(self):
        ensure_active_portal_services('ielts', 'sat')
        _visibility_services()

        self.student_user = User.objects.create_user(username='mock_int_student', password='pass')
        self.student = StudentProfile.objects.create(user=self.student_user)
        self.teacher = TeacherProfile.objects.create(
            user=User.objects.create_user(username='mock_int_teacher', password='pass'),
        )
        TeacherCourseSpecialization.objects.create(teacher=self.teacher, course_type='ielts')
        TeacherCourseSpecialization.objects.create(teacher=self.teacher, course_type='sat')

        self.ielts_group = StudyGroup.objects.create(teacher=self.teacher, name='IELTS Int', max_students=10)
        self.sat_group = StudyGroup.objects.create(teacher=self.teacher, name='SAT Int', max_students=10)
        link_study_group_services(self.ielts_group, 'ielts')
        link_study_group_services(self.sat_group, 'sat')
        self.ielts_group.students.add(self.student)
        self.sat_group.students.add(self.student)
        StudentMockAccess.objects.update_or_create(
            student=self.student,
            exam_program='sat',
            defaults={'is_active': True},
        )

        self.rw_category = QuizCategory.objects.create(service='sat', name='SAT Reading and Writing')
        self.math_category = QuizCategory.objects.create(service='sat', name='SAT Math')

        self.sat_reading = self._variant_sat_quiz(self.rw_category, 'SAT Reading pool', 'reading')
        self.sat_writing = self._variant_sat_quiz(self.rw_category, 'SAT Writing pool', 'writing')
        self.sat_algebra = self._variant_sat_quiz(self.math_category, 'SAT Algebra pool', 'algebra')
        self.sat_geometry = self._variant_sat_quiz(self.math_category, 'SAT Geometry pool', 'geometry_data')

        self.client = Client()
        portal_client_login(self.client, self.student_user)

    def _variant_sat_quiz(self, category, topic, sat_section):
        quiz = Quiz.objects.create(
            category=category,
            topic=topic,
            is_sat=True,
            sat_section=sat_section,
        )
        QuizQuestion.objects.create(
            quiz=quiz,
            order=1,
            question=f'<p>{topic}?</p>',
            answer_options=['A', 'B'],
            correct_answer='A',
            correct_option_index=0,
        )
        assign_quiz_to_student(self.student, quiz)
        return quiz

    def test_sat_section_pool_filters_mock_picks(self):
        picked = pick_random_section_quizzes(self.student.pk, SAT_SERVICE)
        self.assertIn(picked['reading_writing'].sat_section, {'reading', 'writing'})
        self.assertIn(picked['math'].sat_section, {'algebra', 'geometry_data'})

    def test_resolve_take_url_kind_variant_for_sat_writing(self):
        kind = resolve_take_url_kind(SAT_SERVICE, 'reading_writing', self.sat_writing)
        self.assertEqual(kind, 'variant')

    def test_resolve_take_url_kind_reading_for_sat_reading_passage_quiz(self):
        reading_quiz = Quiz.objects.create(
            category=self.rw_category,
            topic='SAT passage reading',
            is_sat=True,
            sat_section=Quiz.SatSection.READING,
            is_reading=True,
        )
        kind = resolve_take_url_kind(SAT_SERVICE, 'reading_writing', reading_quiz)
        self.assertEqual(kind, 'reading')

    def test_sat_mock_take_without_assignment_still_loads_when_enrolled(self):
        attempt, error = start_mock_test_attempt(self.student.pk, SAT_SERVICE)
        self.assertIsNone(error)
        quiz_id = attempt.reading_quiz_id
        QuizAssignment.objects.filter(student=self.student, quiz_id=quiz_id).delete()
        self.assertFalse(quiz_visible_to_student(Quiz.objects.get(pk=quiz_id), self.student.pk))

        take_url = get_mock_take_url(attempt, 'reading_writing')
        response = self.client.get(take_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'portals/student/quiz_take.html')

    def test_sat_mock_variant_submit_advances_to_math(self):
        attempt, _ = start_mock_test_attempt(self.student.pk, SAT_SERVICE)
        quiz = Quiz.objects.get(pk=attempt.reading_quiz_id)
        question = quiz.questions.first()

        self.client.get(get_mock_take_url(attempt, 'reading_writing'))
        start_url = reverse('portals:student-quiz-start', kwargs={'pk': quiz.pk})
        self.assertEqual(self.client.post(f'{start_url}?mock={attempt.pk}').status_code, 200)

        submit_url = reverse('portals:student-quiz-submit', kwargs={'pk': quiz.pk})
        response = self.client.post(
            submit_url,
            data=json.dumps({
                'answers': {str(question.pk): question.correct_option_index},
                'duration_sec': 20,
                'mock': attempt.pk,
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()
        self.assertTrue(data['success'], data.get('error'))
        self.assertTrue(data.get('mock_continue'))
        attempt.refresh_from_db()
        self.assertEqual(attempt.current_section, 'math')
        result = QuizResult.objects.filter(
            student=self.student,
            quiz_id=quiz.pk,
            ielts_mock_attempt_id=attempt.pk,
        ).first()
        self.assertIsNotNone(result)

    def test_mock_stale_section_redirects_to_current(self):
        attempt, _ = start_mock_test_attempt(self.student.pk, SAT_SERVICE)
        wrong_quiz_id = attempt.math_quiz_id
        attempt.current_section = 'reading_writing'
        attempt.save(update_fields=['current_section'])

        ctx = resolve_mock_take_request(self.student.pk, attempt.pk, wrong_quiz_id)
        self.assertIn('mock_redirect', ctx)
        self.assertIn(str(attempt.reading_quiz_id), ctx['mock_redirect'])

    def test_locked_quiz_redirects_without_assignment(self):
        category = QuizCategory.objects.create(service='ielts', name='Locked pool')
        quiz = Quiz.objects.create(category=category, topic='Locked quiz')
        QuizQuestion.objects.create(
            quiz=quiz,
            order=1,
            question='Q?',
            answer_options=['A', 'B'],
            correct_answer='A',
            correct_option_index=0,
        )
        url = reverse('portals:student-quiz-take', kwargs={'pk': quiz.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        assign_quiz_to_student(self.student, quiz, is_active=False)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_sat_quiz_requires_single_sat_section(self):
        quiz = Quiz(category=self.rw_category, topic='Bad SAT', is_sat=True, sat_section='')
        with self.assertRaises(ValidationError):
            quiz.full_clean()

    def test_get_student_quiz_take_data_mock_section_flag(self):
        attempt, _ = start_mock_test_attempt(self.student.pk, SAT_SERVICE)
        data = get_student_quiz_take_data(
            self.student.pk,
            attempt.reading_quiz_id,
            mock_attempt_id=attempt.pk,
        )
        self.assertIsNotNone(data)
        self.assertTrue(data.get('is_mock_section'))

    def test_completed_mock_take_redirects(self):
        attempt, _ = start_mock_test_attempt(self.student.pk, SAT_SERVICE)
        attempt.status = IeltsMockTestAttempt.Status.COMPLETED
        attempt.save(update_fields=['status'])
        ctx = resolve_mock_take_request(self.student.pk, attempt.pk, attempt.reading_quiz_id)
        self.assertIn('mock_redirect', ctx)


class PortalQuizVariantSubmitSessionTests(TestCase):
    def setUp(self):
        ensure_active_portal_services('ielts')
        self.student_user = User.objects.create_user(username='variant_session_student', password='pass')
        self.student = StudentProfile.objects.create(user=self.student_user)
        teacher = TeacherProfile.objects.create(
            user=User.objects.create_user(username='variant_session_teacher', password='pass'),
        )
        TeacherCourseSpecialization.objects.create(teacher=teacher, course_type='ielts')
        group = StudyGroup.objects.create(teacher=teacher, name='IELTS Session', max_students=10)
        link_study_group_services(group, 'ielts')
        group.students.add(self.student)

        category = QuizCategory.objects.create(service='ielts', name='Grammar')
        self.quiz = Quiz.objects.create(category=category, topic='Timed variant')
        self.question = QuizQuestion.objects.create(
            quiz=self.quiz,
            order=1,
            question='Pick A',
            answer_options=['A', 'B'],
            correct_answer='A',
            correct_option_index=0,
        )
        assign_quiz_to_student(self.student, self.quiz)
        self.client = Client()
        portal_client_login(self.client, self.student_user)

    def test_variant_submit_without_session_returns_error(self):
        submit_url = reverse('portals:student-quiz-submit', kwargs={'pk': self.quiz.pk})
        response = self.client.post(
            submit_url,
            data=json.dumps({
                'answers': {str(self.question.pk): 0},
                'duration_sec': 10,
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])
