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
    Service.objects.get_or_create(
        slug='sat',
        defaults={'name_az': 'SAT', 'name_en': 'SAT', 'is_active': True},
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

        from django.utils import timezone

        self.day = timezone.localdate()
        self.teacher_client = Client()
        _portal_client_login(self.teacher_client, self.teacher_user)
        self.student_client = Client()
        _portal_client_login(self.student_client, self.student_user)

    def _entry(self, score, comment='', *, student=None, group=None):
        return {
            'student_id': (student or self.student).pk,
            'group_id': (group or self.group).pk,
            'score': score,
            'comment': comment,
        }

    def _row_key(self, student=None, group=None):
        student = student or self.student
        group = group or self.group
        return f'{student.pk}_{group.pk}'

    def test_teacher_can_save_weekly_score(self):
        result = save_teacher_weekly_scores(
            teacher_id=self.teacher.pk,
            score_date=self.day,
            entries=[self._entry('8.5', 'Good week')],
        )
        self.assertEqual(result['saved'], 1)
        record = WeeklyStudentScore.objects.get(
            teacher=self.teacher,
            student=self.student,
            study_group=self.group,
            score_date=self.day,
        )
        self.assertEqual(float(record.score), 8.5)
        self.assertEqual(record.comment, 'Good week')

    def test_teacher_cannot_score_foreign_student(self):
        from django.core.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            save_teacher_weekly_scores(
                teacher_id=self.other_teacher.pk,
                score_date=self.day,
                entries=[self._entry('7', '')],
            )

    def test_student_sees_weekly_scores_on_scores_page(self):
        save_teacher_weekly_scores(
            teacher_id=self.teacher.pk,
            score_date=self.day,
            entries=[self._entry('9', '')],
        )
        response = self.student_client.get(reverse('portals:student-scores'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nəticələr və qiymətləndirmələr')
        self.assertContains(response, 'Quiz tarixçəsi')
        self.assertContains(response, 'Günlük qiymətləndirmələr')
        self.assertContains(response, '9')

    def test_weekly_score_notifies_student_and_parent(self):
        save_teacher_weekly_scores(
            teacher_id=self.teacher.pk,
            score_date=self.day,
            entries=[self._entry('7.5', '')],
        )
        record = WeeklyStudentScore.objects.get(
            teacher=self.teacher,
            student=self.student,
            study_group=self.group,
            score_date=self.day,
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
        row_key = self._row_key()
        response = self.teacher_client.post(
            url,
            {
                'day': self.day.isoformat(),
                f'score_{row_key}': '6.5',
                f'comment_{row_key}': 'Steady progress',
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
            score_date=self.day,
            entries=[self._entry('5', 'First save')],
        )
        with self.assertRaises(ValidationError):
            save_teacher_weekly_scores(
                teacher_id=self.teacher.pk,
                score_date=self.day,
                entries=[self._entry('8', 'Changed')],
            )
        record = WeeklyStudentScore.objects.get(
            teacher=self.teacher,
            student=self.student,
            study_group=self.group,
            score_date=self.day,
        )
        self.assertEqual(float(record.score), 5.0)
        self.assertEqual(record.comment, 'First save')

    def test_locked_score_cannot_be_removed(self):
        from django.core.exceptions import ValidationError

        save_teacher_weekly_scores(
            teacher_id=self.teacher.pk,
            score_date=self.day,
            entries=[self._entry('5', '')],
        )
        with self.assertRaises(ValidationError):
            save_teacher_weekly_scores(
                teacher_id=self.teacher.pk,
                score_date=self.day,
                entries=[self._entry('3', '')],
            )
        self.assertTrue(
            WeeklyStudentScore.objects.filter(
                teacher=self.teacher,
                student=self.student,
                study_group=self.group,
                score_date=self.day,
            ).exists()
        )

    def test_empty_score_for_locked_student_is_skipped_in_batch(self):
        save_teacher_weekly_scores(
            teacher_id=self.teacher.pk,
            score_date=self.day,
            entries=[self._entry('5', '')],
        )
        other_user = User.objects.create_user(username='weekly_student_2', password='pass')
        other_student = StudentProfile.objects.create(user=other_user)
        self.group.students.add(other_student)

        result = save_teacher_weekly_scores(
            teacher_id=self.teacher.pk,
            score_date=self.day,
            entries=[
                self._entry('', '', student=self.student),
                self._entry('7', '', student=other_student),
            ],
        )
        self.assertEqual(result['saved'], 1)
        self.assertEqual(
            float(
                WeeklyStudentScore.objects.get(
                    teacher=self.teacher,
                    student=other_student,
                    study_group=self.group,
                    score_date=self.day,
                ).score
            ),
            7.0,
        )

    def test_teacher_cannot_repost_same_score(self):
        save_teacher_weekly_scores(
            teacher_id=self.teacher.pk,
            score_date=self.day,
            entries=[self._entry('7', '')],
        )
        result = save_teacher_weekly_scores(
            teacher_id=self.teacher.pk,
            score_date=self.day,
            entries=[self._entry('7', '')],
        )
        self.assertEqual(result['saved'], 0)
        self.assertEqual(result['skipped'], 1)

    def test_locked_row_shown_on_teacher_page(self):
        save_teacher_weekly_scores(
            teacher_id=self.teacher.pk,
            score_date=self.day,
            entries=[self._entry('8', 'Done')],
        )
        response = self.teacher_client.get(reverse('portals:teacher-weekly-scores'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Kilidlənib')
        self.assertNotContains(response, f'name="score_{self._row_key()}"')

    def test_teacher_can_score_an_earlier_day(self):
        earlier = self.day - timedelta(days=3)
        result = save_teacher_weekly_scores(
            teacher_id=self.teacher.pk,
            score_date=earlier,
            entries=[self._entry('7', '')],
        )
        self.assertEqual(result['saved'], 1)
        self.assertTrue(
            WeeklyStudentScore.objects.filter(student=self.student, score_date=earlier).exists()
        )
        # the same student can still be scored today: one score per day
        save_teacher_weekly_scores(
            teacher_id=self.teacher.pk,
            score_date=self.day,
            entries=[self._entry('9', '')],
        )
        self.assertEqual(WeeklyStudentScore.objects.filter(student=self.student).count(), 2)

    def test_teacher_cannot_score_a_future_day(self):
        from django.core.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            save_teacher_weekly_scores(
                teacher_id=self.teacher.pk,
                score_date=self.day + timedelta(days=1),
                entries=[self._entry('7', '')],
            )

    def test_page_defaults_to_today_and_accepts_a_picked_day(self):
        response = self.teacher_client.get(reverse('portals:teacher-weekly-scores'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'value="{self.day.isoformat()}"')
        self.assertContains(response, f'max="{self.day.isoformat()}"')

        earlier = (self.day - timedelta(days=2)).isoformat()
        response = self.teacher_client.get(reverse('portals:teacher-weekly-scores'), {'day': earlier})
        self.assertContains(response, f'name="day" value="{earlier}"')

        # a future day in the address falls back to today
        future = (self.day + timedelta(days=5)).isoformat()
        response = self.teacher_client.get(reverse('portals:teacher-weekly-scores'), {'day': future})
        self.assertContains(response, f'name="day" value="{self.day.isoformat()}"')

    def test_posting_a_picked_day_saves_it(self):
        earlier = self.day - timedelta(days=1)
        response = self.teacher_client.post(
            reverse('portals:teacher-weekly-scores'),
            {
                'day': earlier.isoformat(),
                f'score_{self._row_key()}': '6.5',
                f'comment_{self._row_key()}': '',
            },
        )
        self.assertEqual(response.status_code, 302)
        record = WeeklyStudentScore.objects.get(student=self.student)
        self.assertEqual(record.score_date, earlier)

    def test_old_address_redirects(self):
        response = self.teacher_client.get('/portal/teacher/weekly-scores/?group=all')
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('portals:teacher-weekly-scores'), response['Location'])

    def test_student_without_group_can_be_scored(self):
        from portals.models import StudentProfile

        lone = StudentProfile.objects.create(
            user=get_user_model().objects.create_user(username='daily_lone', password='pass'),
        )
        lone.teachers.add(self.teacher)
        from portals.utils.cache_utils import invalidate_model_cache

        invalidate_model_cache('StudentProfile')
        board = build_teacher_weekly_score_view(self.teacher.pk, group_id='none')
        rows = [row for row in board['rows'] if row['id'] == lone.pk]
        self.assertEqual(len(rows), 1)
        self.assertIsNone(rows[0]['group_id'])

        save_teacher_weekly_scores(
            teacher_id=self.teacher.pk,
            score_date=self.day,
            entries=[{'student_id': lone.pk, 'group_id': None, 'score': '8', 'comment': ''}],
        )
        record = WeeklyStudentScore.objects.get(student=lone)
        self.assertIsNone(record.study_group_id)
        # one score a day without a group
        from django.core.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            save_teacher_weekly_scores(
                teacher_id=self.teacher.pk,
                score_date=self.day,
                entries=[{'student_id': lone.pk, 'group_id': None, 'score': '5', 'comment': ''}],
            )

    def test_student_with_group_cannot_get_a_groupless_score(self):
        from django.core.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            save_teacher_weekly_scores(
                teacher_id=self.teacher.pk,
                score_date=self.day,
                entries=[{'student_id': self.student.pk, 'group_id': None, 'score': '5', 'comment': ''}],
            )

    def test_student_in_two_teacher_groups_gets_two_weekly_cards(self):
        second_group = StudyGroup.objects.create(
            teacher=self.teacher,
            name='Weekly SAT',
            max_students=10,
        )
        link_study_group_services(second_group, 'sat')
        second_group.students.add(self.student)

        board = build_teacher_weekly_score_view(self.teacher.pk)
        student_rows = [row for row in board['rows'] if row['id'] == self.student.pk]
        self.assertEqual(len(student_rows), 2)
        self.assertEqual(
            {row['group_id'] for row in student_rows},
            {self.group.pk, second_group.pk},
        )

        save_teacher_weekly_scores(
            teacher_id=self.teacher.pk,
            score_date=self.day,
            entries=[
                self._entry('8', group=self.group),
                self._entry('6', group=second_group),
            ],
        )
        self.assertEqual(
            WeeklyStudentScore.objects.filter(
                teacher=self.teacher,
                student=self.student,
                score_date=self.day,
            ).count(),
            2,
        )
