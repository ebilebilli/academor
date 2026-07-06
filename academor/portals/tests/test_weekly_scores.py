from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from portals.middleware import PortalSessionMiddleware
from portals.models import (
    ParentProfile,
    PortalNotification,
    StudentProfile,
    StudyGroup,
    TeacherCourseSpecialization,
    TeacherProfile,
    WeeklyStudentScore,
)
from portals.utils.portal_session import PORTAL_COOKIE_NAME, portal_login
from portals.utils.weekly_scores import (
    build_teacher_weekly_score_view,
    get_student_weekly_scores,
    save_teacher_weekly_scores,
)
from portals.tests.group_helpers import link_study_group_services
from projects.models.service_models import Service

User = get_user_model()


def _portal_client_login(client: Client, user) -> None:
    factory = RequestFactory()
    request = factory.get('/portal/')
    request.COOKIES = {}
    portal_login(request, user)
    middleware = PortalSessionMiddleware(lambda r: HttpResponse())
    response = middleware(request)
    client.cookies[PORTAL_COOKIE_NAME] = response.cookies[PORTAL_COOKIE_NAME].value


def _ensure_active_portal_services():
    Service.objects.get_or_create(
        slug='ielts',
        defaults={'name_az': 'IELTS', 'name_en': 'IELTS', 'is_active': True},
    )


class WeeklyStudentScoreTests(TestCase):
    def setUp(self):
        _ensure_active_portal_services()

        self.teacher_user = User.objects.create_user(username='weekly_teacher', password='pass')
        self.student_user = User.objects.create_user(username='weekly_student', password='pass')
        self.parent_user = User.objects.create_user(username='weekly_parent', password='pass')
        self.other_teacher_user = User.objects.create_user(username='weekly_other_teacher', password='pass')

        self.teacher = TeacherProfile.objects.create(user=self.teacher_user)
        self.other_teacher = TeacherProfile.objects.create(user=self.other_teacher_user)
        self.student = StudentProfile.objects.create(user=self.student_user)
        self.parent = ParentProfile.objects.create(user=self.parent_user)
        self.parent.students.add(self.student)

        TeacherCourseSpecialization.objects.create(teacher=self.teacher, course_type='ielts')
        TeacherCourseSpecialization.objects.create(teacher=self.other_teacher, course_type='ielts')

        self.group = StudyGroup.objects.create(
            teacher=self.teacher,
            name='Weekly IELTS',
            max_students=10,
        )
        link_study_group_services(self.group, 'ielts')
        self.group.students.add(self.student)

        self.week_start = date.today() - timedelta(days=date.today().weekday())
        self.teacher_client = Client()
        _portal_client_login(self.teacher_client, self.teacher_user)
        self.student_client = Client()
        _portal_client_login(self.student_client, self.student_user)

    def test_teacher_can_save_weekly_score(self):
        result = save_teacher_weekly_scores(
            teacher_id=self.teacher.pk,
            week_start=self.week_start,
            entries=[{'student_id': self.student.pk, 'score': '8.5', 'comment': 'Good week'}],
        )
        self.assertEqual(result['saved'], 1)
        record = WeeklyStudentScore.objects.get(
            teacher=self.teacher,
            student=self.student,
            week_start=self.week_start,
        )
        self.assertEqual(float(record.score), 8.5)
        self.assertEqual(record.comment, 'Good week')

    def test_teacher_cannot_score_foreign_student(self):
        from django.core.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            save_teacher_weekly_scores(
                teacher_id=self.other_teacher.pk,
                week_start=self.week_start,
                entries=[{'student_id': self.student.pk, 'score': '7', 'comment': ''}],
            )

    def test_student_sees_weekly_scores_on_scores_page(self):
        save_teacher_weekly_scores(
            teacher_id=self.teacher.pk,
            week_start=self.week_start,
            entries=[{'student_id': self.student.pk, 'score': '9', 'comment': ''}],
        )
        response = self.student_client.get(reverse('portals:student-scores'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nəticələr və qiymətləndirmələr')
        self.assertContains(response, 'Quiz tarixçəsi')
        self.assertContains(response, 'Həftəlik qiymətləndirmələr')
        self.assertContains(response, '9')

    def test_weekly_score_notifies_student_and_parent(self):
        save_teacher_weekly_scores(
            teacher_id=self.teacher.pk,
            week_start=self.week_start,
            entries=[{'student_id': self.student.pk, 'score': '7.5', 'comment': ''}],
        )
        record = WeeklyStudentScore.objects.get(
            teacher=self.teacher,
            student=self.student,
            week_start=self.week_start,
        )
        self.assertTrue(
            PortalNotification.objects.filter(
                student=self.student,
                weekly_student_score=record,
                kind=PortalNotification.Kind.WEEKLY_SCORE_PUBLISHED,
            ).exists()
        )
        self.assertTrue(
            PortalNotification.objects.filter(
                parent=self.parent,
                weekly_student_score=record,
                kind=PortalNotification.Kind.WEEKLY_SCORE_PUBLISHED,
            ).exists()
        )

    def test_teacher_weekly_scores_page_lists_students(self):
        response = self.teacher_client.get(reverse('portals:teacher-weekly-scores'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.student.full_name)

    def test_teacher_can_post_weekly_scores(self):
        url = reverse('portals:teacher-weekly-scores')
        response = self.teacher_client.post(
            url,
            {
                'week': self.week_start.isoformat(),
                f'score_{self.student.pk}': '6.5',
                f'comment_{self.student.pk}': 'Steady progress',
            },
        )
        self.assertEqual(response.status_code, 302)
        board = build_teacher_weekly_score_view(self.teacher.pk)
        self.assertEqual(board['scored_count'], 1)
        scores = get_student_weekly_scores(self.student.pk)
        self.assertEqual(len(scores), 1)
        self.assertEqual(scores[0]['score'], 6.5)

    def test_locked_score_cannot_be_changed(self):
        from django.core.exceptions import ValidationError

        save_teacher_weekly_scores(
            teacher_id=self.teacher.pk,
            week_start=self.week_start,
            entries=[{'student_id': self.student.pk, 'score': '5', 'comment': 'First save'}],
        )
        with self.assertRaises(ValidationError):
            save_teacher_weekly_scores(
                teacher_id=self.teacher.pk,
                week_start=self.week_start,
                entries=[{'student_id': self.student.pk, 'score': '8', 'comment': 'Changed'}],
            )
        record = WeeklyStudentScore.objects.get(
            teacher=self.teacher,
            student=self.student,
            week_start=self.week_start,
        )
        self.assertEqual(float(record.score), 5.0)
        self.assertEqual(record.comment, 'First save')

    def test_locked_score_cannot_be_removed(self):
        from django.core.exceptions import ValidationError

        save_teacher_weekly_scores(
            teacher_id=self.teacher.pk,
            week_start=self.week_start,
            entries=[{'student_id': self.student.pk, 'score': '5', 'comment': ''}],
        )
        with self.assertRaises(ValidationError):
            save_teacher_weekly_scores(
                teacher_id=self.teacher.pk,
                week_start=self.week_start,
                entries=[{'student_id': self.student.pk, 'score': '3', 'comment': ''}],
            )
        self.assertTrue(
            WeeklyStudentScore.objects.filter(
                teacher=self.teacher,
                student=self.student,
                week_start=self.week_start,
            ).exists()
        )

    def test_empty_score_for_locked_student_is_skipped_in_batch(self):
        save_teacher_weekly_scores(
            teacher_id=self.teacher.pk,
            week_start=self.week_start,
            entries=[{'student_id': self.student.pk, 'score': '5', 'comment': ''}],
        )
        other_user = User.objects.create_user(username='weekly_student_2', password='pass')
        other_student = StudentProfile.objects.create(user=other_user)
        self.group.students.add(other_student)

        result = save_teacher_weekly_scores(
            teacher_id=self.teacher.pk,
            week_start=self.week_start,
            entries=[
                {'student_id': self.student.pk, 'score': '', 'comment': ''},
                {'student_id': other_student.pk, 'score': '7', 'comment': ''},
            ],
        )
        self.assertEqual(result['saved'], 1)
        self.assertEqual(
            float(
                WeeklyStudentScore.objects.get(
                    teacher=self.teacher,
                    student=other_student,
                    week_start=self.week_start,
                ).score
            ),
            7.0,
        )

    def test_teacher_cannot_repost_same_score(self):
        save_teacher_weekly_scores(
            teacher_id=self.teacher.pk,
            week_start=self.week_start,
            entries=[{'student_id': self.student.pk, 'score': '7', 'comment': ''}],
        )
        result = save_teacher_weekly_scores(
            teacher_id=self.teacher.pk,
            week_start=self.week_start,
            entries=[{'student_id': self.student.pk, 'score': '7', 'comment': ''}],
        )
        self.assertEqual(result['saved'], 0)
        self.assertEqual(result['skipped'], 1)

    def test_locked_row_shown_on_teacher_page(self):
        save_teacher_weekly_scores(
            teacher_id=self.teacher.pk,
            week_start=self.week_start,
            entries=[{'student_id': self.student.pk, 'score': '8', 'comment': 'Done'}],
        )
        response = self.teacher_client.get(reverse('portals:teacher-weekly-scores'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Kilidlənib')
        self.assertNotContains(response, 'name="score_' + str(self.student.pk) + '"')

    def test_teacher_cannot_score_past_week(self):
        from django.core.exceptions import ValidationError

        past_week = self.week_start - timedelta(days=7)
        with self.assertRaises(ValidationError):
            save_teacher_weekly_scores(
                teacher_id=self.teacher.pk,
                week_start=past_week,
                entries=[{'student_id': self.student.pk, 'score': '7', 'comment': ''}],
            )

    def test_weekly_scores_page_ignores_week_query_param(self):
        past_week = (self.week_start - timedelta(days=7)).isoformat()
        response = self.teacher_client.get(
            reverse('portals:teacher-weekly-scores'),
            {'week': past_week},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cari həftə')
        self.assertNotContains(response, 'data-weekly-week-nav')
