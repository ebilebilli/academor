import json

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from portals.middleware import PortalSessionMiddleware
from portals.models import (
    Quiz,
    QuizAssignment,
    QuizCategory,
    StudentCourseSpecialization,
    StudentMockAccess,
    StudentProfile,
    StudyGroup,
    TeacherCourseSpecialization,
    TeacherProfile,
)
from portals.utils.portal_session import PORTAL_COOKIE_NAME, portal_login
from portals.utils.queries import get_student_quizzes_for_category
from portals.utils.quiz_assignments import (
    get_student_mock_access_state,
    get_teacher_student_mock_access_rows,
    get_teacher_student_quiz_access_rows,
    set_student_mock_access,
    set_student_quiz_assignment,
    student_has_active_mock_access,
    student_has_active_mock_access_for_program,
)
from portals.utils.student_courses import quiz_visible_to_student
from portals.tests.test_quiz_visibility import QuizVisibilityTests, _ensure_active_portal_services

User = get_user_model()


def _portal_client_login(client: Client, user) -> None:
    factory = RequestFactory()
    request = factory.get('/portal/')
    request.COOKIES = {}
    portal_login(request, user)
    middleware = PortalSessionMiddleware(lambda r: HttpResponse())
    response = middleware(request)
    client.cookies[PORTAL_COOKIE_NAME] = response.cookies[PORTAL_COOKIE_NAME].value


class QuizAssignmentTests(QuizVisibilityTests):
    def test_inactive_assignment_hides_quiz(self):
        QuizAssignment.objects.filter(
            student=self.student,
            quiz=self.ielts_quiz,
        ).update(is_active=False)
        self.assertFalse(quiz_visible_to_student(self.ielts_quiz, self.student.pk))
        quizzes = get_student_quizzes_for_category(self.student.pk, self.ielts_category.pk)
        self.assertEqual(len(quizzes), 1)
        self.assertTrue(quizzes[0]['is_locked'])
        self.assertFalse(quizzes[0]['is_unlocked'])

    def test_teacher_can_activate_quiz_for_student(self):
        QuizAssignment.objects.filter(
            student=self.student,
            quiz=self.ielts_quiz,
        ).delete()
        assignment = set_student_quiz_assignment(
            self.teacher.pk,
            self.student.pk,
            self.ielts_quiz.pk,
            is_active=True,
        )
        self.assertIsNotNone(assignment)
        self.assertTrue(assignment.is_active)
        self.assertTrue(quiz_visible_to_student(self.ielts_quiz, self.student.pk))

    def test_teacher_cannot_assign_quiz_for_non_group_student(self):
        assignment = set_student_quiz_assignment(
            self.teacher.pk,
            self.other_student.pk,
            self.ielts_quiz.pk,
            is_active=True,
        )
        self.assertIsNone(assignment)

    def test_teacher_quiz_access_rows_include_assignment_state(self):
        self.ielts_quiz.is_ielts = True
        self.ielts_quiz.save(update_fields=['is_ielts'])
        rows = get_teacher_student_quiz_access_rows(self.teacher.pk, self.student.pk)
        self.assertEqual(len(rows), 1)
        self.assertIsNone(rows[0]['category_access'])
        self.assertEqual(rows[0]['quizzes'][0]['id'], self.ielts_quiz.pk)
        self.assertTrue(rows[0]['quizzes'][0]['is_active'])

    def test_teacher_quiz_access_general_quizzes_use_category_toggle(self):
        """Non-IELTS/SAT quizzes are controlled by category name, not quiz titles."""
        from portals.tests.group_helpers import create_quiz_category
        from portals.utils.quiz_assignments import (
            quiz_access_control_count,
            set_student_quiz_assignments,
        )

        Service.objects.get_or_create(
            slug='general-english',
            defaults={
                'name_az': 'General English',
                'name_en': 'General English',
                'is_active': True,
            },
        )
        TeacherCourseSpecialization.objects.get_or_create(
            teacher=self.teacher,
            course_type='general_english',
        )
        StudentCourseSpecialization.objects.update_or_create(
            student=self.student,
            course_type='general_english',
            defaults={'is_active': True},
        )
        ge_category = create_quiz_category('A1 Reading Tests', 'general_english')
        q1 = Quiz.objects.create(category=ge_category, topic='My Family', is_ielts=False, is_sat=False)
        q2 = Quiz.objects.create(category=ge_category, topic='My School', is_ielts=False, is_sat=False)
        QuizAssignment.objects.create(
            student=self.student, quiz=q1, is_active=True, assigned_by=self.teacher,
        )
        QuizAssignment.objects.create(
            student=self.student, quiz=q2, is_active=False, assigned_by=self.teacher,
        )

        rows = get_teacher_student_quiz_access_rows(self.teacher.pk, self.student.pk)
        ge_row = next((row for row in rows if row['id'] == ge_category.pk), None)
        self.assertIsNotNone(ge_row)
        self.assertEqual(ge_row['quizzes'], [])
        self.assertIsNotNone(ge_row['category_access'])
        self.assertEqual(ge_row['category_access']['quiz_count'], 2)
        self.assertEqual(ge_row['category_access']['active_count'], 1)
        self.assertTrue(ge_row['category_access']['is_partial'])
        self.assertFalse(ge_row['category_access']['is_active'])

        updated = set_student_quiz_assignments(
            self.teacher.pk,
            self.student.pk,
            is_active=True,
            category_id=ge_category.pk,
            general_only=True,
        )
        self.assertEqual(set(updated), {q1.pk, q2.pk})
        rows = get_teacher_student_quiz_access_rows(self.teacher.pk, self.student.pk)
        ge_row = next(row for row in rows if row['id'] == ge_category.pk)
        self.assertTrue(ge_row['category_access']['is_active'])
        self.assertGreaterEqual(quiz_access_control_count(rows), 1)

    def test_teacher_toggle_endpoint_updates_assignment(self):
        client = Client()
        _portal_client_login(client, self.teacher_user)
        url = reverse(
            'portals:teacher-quiz-assignment-toggle',
            kwargs={'student_pk': self.student.pk, 'quiz_pk': self.ielts_quiz.pk},
        )
        response = client.post(
            url,
            data=json.dumps({'is_active': False}),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload['ok'])
        self.assertFalse(payload['is_active'])
        self.assertFalse(
            QuizAssignment.objects.get(
                student=self.student,
                quiz=self.ielts_quiz,
            ).is_active
        )
        quizzes = get_student_quizzes_for_category(self.student.pk, self.ielts_category.pk)
        self.assertTrue(quizzes[0]['is_locked'])

    def test_teacher_can_toggle_mock_access(self):
        self.assertFalse(student_has_active_mock_access(self.student.pk))
        access = set_student_mock_access(
            self.teacher.pk,
            self.student.pk,
            'ielts',
            is_active=True,
        )
        self.assertIsNotNone(access)
        self.assertTrue(student_has_active_mock_access(self.student.pk))
        state = get_student_mock_access_state(self.student.pk, 'ielts')
        self.assertTrue(state['is_active'])
        self.assertTrue(state['exists'])

        client = Client()
        _portal_client_login(client, self.teacher_user)
        url = reverse(
            'portals:teacher-mock-access-toggle',
            kwargs={'student_pk': self.student.pk, 'program': 'ielts'},
        )
        response = client.post(
            url,
            data=json.dumps({'is_active': False}),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['is_active'])
        self.assertFalse(student_has_active_mock_access(self.student.pk))
        self.assertFalse(
            StudentMockAccess.objects.get(
                student=self.student,
                exam_program='ielts',
            ).is_active
        )


class MockAccessPerProgramTests(TestCase):
    def setUp(self):
        from portals.tests.portal_helpers import ensure_active_portal_services

        ensure_active_portal_services('ielts', 'sat')
        from portals.tests.group_helpers import link_study_group_services

        self.ielts_teacher_user = User.objects.create_user(username='ielts_mock_teacher', password='pass')
        self.sat_teacher_user = User.objects.create_user(username='sat_mock_teacher', password='pass')
        self.student_user = User.objects.create_user(username='dual_mock_student', password='pass')

        self.ielts_teacher = TeacherProfile.objects.create(user=self.ielts_teacher_user)
        self.sat_teacher = TeacherProfile.objects.create(user=self.sat_teacher_user)
        self.student = StudentProfile.objects.create(user=self.student_user)

        TeacherCourseSpecialization.objects.create(teacher=self.ielts_teacher, course_type='ielts')
        TeacherCourseSpecialization.objects.create(teacher=self.sat_teacher, course_type='sat')

        self.ielts_group = StudyGroup.objects.create(
            teacher=self.ielts_teacher,
            name='IELTS mock group',
            max_students=10,
        )
        self.sat_group = StudyGroup.objects.create(
            teacher=self.sat_teacher,
            name='SAT mock group',
            max_students=10,
        )
        link_study_group_services(self.ielts_group, 'ielts')
        link_study_group_services(self.sat_group, 'sat')
        self.ielts_group.students.add(self.student)
        self.sat_group.students.add(self.student)

    def test_sat_teacher_sees_only_sat_mock_toggle(self):
        rows = get_teacher_student_mock_access_rows(self.sat_teacher.pk, self.student.pk)
        self.assertEqual([row['program'] for row in rows], ['sat'])

    def test_ielts_teacher_sees_only_ielts_mock_toggle(self):
        rows = get_teacher_student_mock_access_rows(self.ielts_teacher.pk, self.student.pk)
        self.assertEqual([row['program'] for row in rows], ['ielts'])

    def test_program_access_is_independent(self):
        self.assertTrue(
            set_student_mock_access(
                self.sat_teacher.pk,
                self.student.pk,
                'sat',
                is_active=True,
            )
        )
        self.assertFalse(student_has_active_mock_access_for_program(self.student.pk, 'ielts'))
        self.assertTrue(student_has_active_mock_access_for_program(self.student.pk, 'sat'))
        self.assertTrue(student_has_active_mock_access(self.student.pk))

        denied = set_student_mock_access(
            self.sat_teacher.pk,
            self.student.pk,
            'ielts',
            is_active=True,
        )
        self.assertIsNone(denied)

        self.assertTrue(
            set_student_mock_access(
                self.ielts_teacher.pk,
                self.student.pk,
                'ielts',
                is_active=True,
            )
        )
        self.assertTrue(student_has_active_mock_access_for_program(self.student.pk, 'ielts'))

class QuizAssignmentNewStudentTests(TestCase):
    def setUp(self):
        _ensure_active_portal_services()
        self.teacher_user = User.objects.create_user(username='assign-teacher', password='pass')
        self.student_user = User.objects.create_user(username='assign-student', password='pass')
        self.teacher = TeacherProfile.objects.create(user=self.teacher_user)
        self.student = StudentProfile.objects.create(user=self.student_user)
        TeacherCourseSpecialization.objects.create(teacher=self.teacher, course_type='ielts')
        self.group = StudyGroup.objects.create(teacher=self.teacher, name='IELTS C', max_students=10)
        from portals.tests.group_helpers import create_quiz_category, link_study_group_services

        link_study_group_services(self.group, 'ielts')
        self.group.students.add(self.student)
        category = create_quiz_category('Grammar', 'ielts')
        self.quiz = Quiz.objects.create(category=category, topic='New quiz')

    def test_new_student_does_not_see_quiz_until_teacher_assigns(self):
        self.assertFalse(quiz_visible_to_student(self.quiz, self.student.pk))
        set_student_quiz_assignment(
            self.teacher.pk,
            self.student.pk,
            self.quiz.pk,
            is_active=True,
        )
        self.assertTrue(quiz_visible_to_student(self.quiz, self.student.pk))
