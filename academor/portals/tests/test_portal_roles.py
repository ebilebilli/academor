"""Portal access, role isolation, and multi-group UI for each portal role."""

from datetime import date
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from portals.models import (
    CustomerProfile,
    ParentProfile,
    Quiz,
    QuizCategory,
    QuizQuestion,
    QuizResult,
    StudentCourseSpecialization,
    StudentProfile,
    StudyGroup,
    TeacherProfile,
    WeeklyStudentScore,
)
from portals.tests.group_helpers import link_study_group_services
from portals.tests.portal_helpers import ensure_active_portal_services, portal_client_login
from portals.utils.queries import get_portal_role
from portals.views.views_v1 import _student_scores_context

User = get_user_model()

STUDENT_PAGES = (
    'portals:student-dashboard',
    'portals:student-lessons',
    'portals:student-schedule',
    'portals:student-attendance',
    'portals:student-scores',
)

TEACHER_PAGES = (
    'portals:teacher-dashboard',
    'portals:teacher-lessons',
    'portals:teacher-schedule',
    'portals:teacher-attendance',
    'portals:teacher-scores',
)

PARENT_PAGES = (
    'portals:parent-dashboard',
    'portals:parent-lessons',
    'portals:parent-schedule',
    'portals:parent-scores',
    'portals:parent-attendance',
)

CUSTOMER_PAGES = (
    'portals:customer-dashboard',
    'portals:customer-notifications',
    'portals:customer-mock-packages',
)


class PortalRoleFixtureMixin:
    def setUp_portal_roles(self):
        ensure_active_portal_services('ielts', 'sat')

        self.teacher_a = TeacherProfile.objects.create(
            user=User.objects.create_user(username='role_teacher_a', password='pass'),
        )
        self.teacher_b = TeacherProfile.objects.create(
            user=User.objects.create_user(username='role_teacher_b', password='pass'),
        )

        self.student_user = User.objects.create_user(username='role_student', password='pass')
        self.student = StudentProfile.objects.create(user=self.student_user)

        self.parent_user = User.objects.create_user(username='role_parent', password='pass')
        self.parent = ParentProfile.objects.create(user=self.parent_user)
        self.parent.students.add(self.student)

        self.customer_user = User.objects.create_user(username='role_customer', password='pass')
        self.customer = CustomerProfile.objects.create(
            user=self.customer_user,
            phone='+994501110011',
            teacher=self.teacher_a,
        )

        self.group_a = StudyGroup.objects.create(
            teacher=self.teacher_a,
            name='IELTS group A',
            max_students=10,
        )
        self.group_b = StudyGroup.objects.create(
            teacher=self.teacher_b,
            name='SAT group B',
            max_students=10,
        )
        link_study_group_services(self.group_a, 'ielts')
        link_study_group_services(self.group_b, 'sat')
        self.group_a.students.add(self.student)
        self.group_b.students.add(self.student)

        StudentCourseSpecialization.objects.get_or_create(
            student=self.student,
            course_type='ielts',
            defaults={'is_active': True},
        )
        StudentCourseSpecialization.objects.get_or_create(
            student=self.student,
            course_type='sat',
            defaults={'is_active': True},
        )


class PortalRoleAccessTests(PortalRoleFixtureMixin, TestCase):
    def setUp(self):
        self.setUp_portal_roles()

    def _assert_redirects_to_dashboard(self, client, url_name, **kwargs):
        response = client.get(reverse(url_name, kwargs=kwargs))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('portals:dashboard'))

    def test_unauthenticated_user_redirected_to_login(self):
        client = Client()
        response = client.get(reverse('portals:student-dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('portals:login'), response.url)

    def test_student_can_access_student_pages(self):
        client = Client()
        portal_client_login(client, self.student_user)
        for url_name in STUDENT_PAGES:
            with self.subTest(url=url_name):
                response = client.get(reverse(url_name))
                self.assertEqual(response.status_code, 200)

    def test_teacher_can_access_teacher_pages(self):
        client = Client()
        portal_client_login(client, self.teacher_a.user)
        for url_name in TEACHER_PAGES:
            with self.subTest(url=url_name):
                response = client.get(reverse(url_name))
                self.assertEqual(response.status_code, 200)

    def test_parent_can_access_parent_pages(self):
        client = Client()
        portal_client_login(client, self.parent_user)
        for url_name in PARENT_PAGES:
            with self.subTest(url=url_name):
                response = client.get(reverse(url_name))
                self.assertEqual(response.status_code, 200)

    def test_customer_can_access_customer_pages(self):
        client = Client()
        portal_client_login(client, self.customer_user)
        for url_name in CUSTOMER_PAGES:
            with self.subTest(url=url_name):
                response = client.get(reverse(url_name))
                self.assertEqual(response.status_code, 200)

    def test_student_blocked_from_other_role_pages(self):
        client = Client()
        portal_client_login(client, self.student_user)
        for url_name in TEACHER_PAGES + PARENT_PAGES + CUSTOMER_PAGES:
            with self.subTest(url=url_name):
                self._assert_redirects_to_dashboard(client, url_name)

    def test_teacher_blocked_from_other_role_pages(self):
        client = Client()
        portal_client_login(client, self.teacher_a.user)
        for url_name in STUDENT_PAGES + PARENT_PAGES + CUSTOMER_PAGES:
            with self.subTest(url=url_name):
                self._assert_redirects_to_dashboard(client, url_name)

    def test_parent_blocked_from_other_role_pages(self):
        client = Client()
        portal_client_login(client, self.parent_user)
        for url_name in STUDENT_PAGES + TEACHER_PAGES + CUSTOMER_PAGES:
            with self.subTest(url=url_name):
                self._assert_redirects_to_dashboard(client, url_name)

    def test_customer_blocked_from_other_role_pages(self):
        client = Client()
        portal_client_login(client, self.customer_user)
        for url_name in STUDENT_PAGES + TEACHER_PAGES + PARENT_PAGES:
            with self.subTest(url=url_name):
                self._assert_redirects_to_dashboard(client, url_name)

    def test_get_portal_role_priority_teacher_over_student(self):
        user = User.objects.create_user(username='dual_role', password='pass')
        TeacherProfile.objects.create(user=user)
        StudentProfile.objects.create(user=user)
        self.assertEqual(get_portal_role(user), 'teacher')


class PortalRoleMultiGroupTests(PortalRoleFixtureMixin, TestCase):
    def setUp(self):
        self.setUp_portal_roles()

    def test_student_schedule_shows_group_filter_tabs(self):
        client = Client()
        portal_client_login(client, self.student_user)
        response = client.get(reverse('portals:student-schedule'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'IELTS group A')
        self.assertContains(response, 'SAT group B')
        self.assertContains(response, 'data-score-group')

    def test_parent_schedule_shows_group_filter_tabs(self):
        client = Client()
        portal_client_login(client, self.parent_user)
        response = client.get(
            reverse('portals:parent-schedule'),
            {'student': self.student.pk},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'IELTS group A')
        self.assertContains(response, 'SAT group B')
        self.assertContains(response, 'data-score-group')

    def test_teacher_student_profile_shows_only_own_group_card(self):
        client = Client()
        portal_client_login(client, self.teacher_a.user)
        response = client.get(
            reverse('portals:teacher-student-profile', kwargs={'student_pk': self.student.pk}),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'IELTS group A')
        self.assertNotContains(response, 'SAT group B')

    def test_teacher_b_student_profile_shows_only_sat_group_card(self):
        client = Client()
        portal_client_login(client, self.teacher_b.user)
        response = client.get(
            reverse('portals:teacher-student-profile', kwargs={'student_pk': self.student.pk}),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SAT group B')
        self.assertNotContains(response, 'IELTS group A')

    def test_teacher_student_profile_tab_panel_request_skips_full_page_metrics(self):
        client = Client()
        portal_client_login(client, self.teacher_a.user)

        with patch('portals.views.views_v1.build_student_performance_by_groups', side_effect=AssertionError('full page metrics should not run')):
            response = client.get(
                reverse('portals:teacher-student-profile', kwargs={'student_pk': self.student.pk}),
                {'tab': 'quiz-results'},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'portal-student-empty')

    def test_student_scores_average_respects_active_group(self):
        from portals.tests.group_helpers import create_quiz_category

        ielts_category = create_quiz_category('IELTS', 'ielts')
        sat_category = create_quiz_category('SAT', 'sat')
        ielts_quiz = Quiz.objects.create(topic='IELTS quiz', category=ielts_category)
        sat_quiz = Quiz.objects.create(topic='SAT quiz', category=sat_category)
        QuizQuestion.objects.create(
            quiz=ielts_quiz,
            order=1,
            question='<p>IELTS?</p>',
            answer_options=['A', 'B'],
            correct_answer='A',
            correct_option_index=0,
        )
        QuizQuestion.objects.create(
            quiz=sat_quiz,
            order=1,
            question='<p>SAT?</p>',
            answer_options=['A', 'B'],
            correct_answer='A',
            correct_option_index=0,
        )
        QuizResult.objects.create(
            student=self.student,
            quiz=ielts_quiz,
            total_score=10,
            duration_sec=60,
            completed_at=timezone.now(),
        )
        QuizResult.objects.create(
            student=self.student,
            quiz=sat_quiz,
            total_score=5,
            duration_sec=60,
            completed_at=timezone.now(),
        )
        WeeklyStudentScore.objects.create(
            student=self.student,
            teacher=self.teacher_a,
            study_group=self.group_a,
            week_start=date(2026, 7, 6),
            score=8,
        )
        WeeklyStudentScore.objects.create(
            student=self.student,
            teacher=self.teacher_b,
            study_group=self.group_b,
            week_start=date(2026, 7, 6),
            score=4,
        )

        request = RequestFactory().get(
            f'/portal/student/scores/?group={self.group_a.pk}'
        )
        ctx = _student_scores_context(self.student.pk, request=request)
        self.assertEqual(ctx['quiz_average']['graded_count'], 1)
        self.assertEqual(ctx['weekly_average']['graded_count'], 1)
        self.assertEqual(len(ctx['weekly_scores']), 1)
        self.assertEqual(ctx['weekly_scores'][0]['score'], 8)

        request_b = RequestFactory().get(
            f'/portal/student/scores/?group={self.group_b.pk}'
        )
        ctx_b = _student_scores_context(self.student.pk, request=request_b)
        self.assertEqual(ctx_b['quiz_average']['graded_count'], 1)
        self.assertEqual(ctx_b['weekly_average']['graded_count'], 1)
        self.assertEqual(ctx_b['weekly_scores'][0]['score'], 4)
