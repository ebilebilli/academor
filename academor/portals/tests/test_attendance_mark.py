from datetime import date, time, timedelta

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from django.utils.translation import gettext as _

from portals.middleware import PortalSessionMiddleware
from portals.models import (
    Attendance,
    Schedule,
    StudentProfile,
    StudyGroup,
    TeacherCourseSpecialization,
    TeacherProfile,
)
from portals.utils.portal_session import PORTAL_COOKIE_NAME, portal_login
from portals.utils.teacher_attendance import parse_student_ids, save_session_attendance
from portals.utils.teacher_schedule import (
    build_teacher_week_calendar,
    common_group_ids_for_students,
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


class AttendanceMarkTests(TestCase):
    def setUp(self):
        _ensure_active_portal_services()

        self.teacher_user = User.objects.create_user(username='att_teacher', password='pass')
        self.student_a_user = User.objects.create_user(username='att_student_a', password='pass')
        self.student_b_user = User.objects.create_user(username='att_student_b', password='pass')
        self.student_c_user = User.objects.create_user(username='att_student_c', password='pass')

        self.teacher = TeacherProfile.objects.create(user=self.teacher_user)
        self.student_a = StudentProfile.objects.create(user=self.student_a_user)
        self.student_b = StudentProfile.objects.create(user=self.student_b_user)
        self.student_c = StudentProfile.objects.create(user=self.student_c_user)

        TeacherCourseSpecialization.objects.create(teacher=self.teacher, course_type='ielts')

        self.group_one = StudyGroup.objects.create(
            teacher=self.teacher,
            name='IELTS Morning',
            max_students=10,
        )
        link_study_group_services(self.group_one, 'ielts')
        self.group_one.students.add(self.student_a, self.student_b)

        self.group_two = StudyGroup.objects.create(
            teacher=self.teacher,
            name='IELTS Evening',
            max_students=10,
        )
        link_study_group_services(self.group_two, 'ielts')
        self.group_two.students.add(self.student_c)

        self.schedule = Schedule.objects.create(
            group=self.group_one,
            weekday=date.today().weekday(),
            start_time=time(10, 0),
            duration_min=90,
        )
        self.session_date = date.today()

        self.client = Client()
        _portal_client_login(self.client, self.teacher_user)

    def _session_url(self, **params):
        url = reverse('portals:teacher-attendance-session')
        query = '&'.join(f'{key}={value}' for key, value in params.items())
        return f'{url}?{query}' if query else url

    def _post_attendance(self, student_status_map, selected_ids=None):
        selected_ids = selected_ids or list(student_status_map.keys())
        data = {
            'schedule': self.schedule.pk,
            'date': self.session_date.isoformat(),
            'week': self.session_date.isoformat(),
        }
        for student_id in selected_ids:
            data[f'status_{student_id}'] = student_status_map[student_id]
        data['selected_students'] = [str(sid) for sid in selected_ids]
        return self.client.post(self._session_url(), data)

    def test_common_group_ids_for_students_shared_group(self):
        group_ids = common_group_ids_for_students(
            [self.student_a.pk, self.student_b.pk],
            self.teacher.pk,
        )
        self.assertEqual(group_ids, [self.group_one.pk])

    def test_common_group_ids_for_students_no_shared_group(self):
        group_ids = common_group_ids_for_students(
            [self.student_a.pk, self.student_c.pk],
            self.teacher.pk,
        )
        self.assertEqual(group_ids, [])

    def test_calendar_filters_to_common_group_sessions(self):
        week_start = self.session_date - timedelta(days=self.session_date.weekday())
        calendar = build_teacher_week_calendar(
            self.teacher.pk,
            week_start=week_start,
            student_ids=[self.student_a.pk, self.student_b.pk],
        )
        self.assertTrue(calendar['has_sessions'])
        session_groups = {
            session['group_id']
            for day in calendar['days']
            for session in day['sessions']
        }
        self.assertEqual(session_groups, {self.group_one.pk})

    def test_calendar_empty_for_students_in_different_groups(self):
        week_start = self.session_date - timedelta(days=self.session_date.weekday())
        calendar = build_teacher_week_calendar(
            self.teacher.pk,
            week_start=week_start,
            student_ids=[self.student_a.pk, self.student_c.pk],
        )
        self.assertFalse(calendar['has_sessions'])

    def test_hub_defaults_to_mark_tab(self):
        response = self.client.get(reverse('portals:teacher-attendance'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['hub_tab'], 'mark')
        self.assertContains(response, 'portal-attendance-hub-tab is-active')
        self.assertContains(response, 'portal-attendance-hub-action')
        self.assertNotContains(response, 'attendance-hub-panel')
        self.assertNotContains(response, 'id="attendance-hub-stats"')

    def test_hub_history_tab_shows_students(self):
        response = self.client.get(reverse('portals:teacher-attendance') + '?tab=history')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['hub_tab'], 'history')
        self.assertContains(response, 'attendance-hub-panel')
        self.assertContains(response, 'id="attendance-hub-stats"')
        self.assertNotContains(response, 'portal-attendance-hub-action')

    def test_hub_invalid_tab_falls_back_to_mark(self):
        response = self.client.get(reverse('portals:teacher-attendance') + '?tab=unknown')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['hub_tab'], 'mark')
        self.assertContains(response, 'portal-attendance-hub-action')

    def test_hub_mark_tab_lists_todays_sessions(self):
        response = self.client.get(reverse('portals:teacher-attendance'))
        self.assertEqual(response.status_code, 200)
        sessions = response.context['today_sessions']
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0]['group_name'], self.group_one.name)
        self.assertEqual(sessions[0]['marked_count'], 0)
        self.assertFalse(sessions[0]['is_complete'])
        self.assertContains(response, 'portal-attendance-today-card')
        self.assertContains(response, self.group_one.name)

    def test_hub_mark_tab_empty_when_no_class_today(self):
        self.schedule.weekday = (date.today().weekday() + 1) % 7
        self.schedule.save()
        response = self.client.get(reverse('portals:teacher-attendance'))
        self.assertEqual(response.context['today_sessions'], [])
        self.assertContains(response, 'portal-attendance-today-empty')
        self.assertNotContains(response, 'portal-attendance-today-card')

    def test_hub_today_session_shows_marked_progress(self):
        Attendance.objects.create(
            schedule=self.schedule,
            student=self.student_a,
            session_date=self.session_date,
            status=Attendance.Status.PRESENT,
        )
        response = self.client.get(reverse('portals:teacher-attendance'))
        session = response.context['today_sessions'][0]
        self.assertEqual(session['marked_count'], 1)
        self.assertEqual(session['student_count'], 2)
        self.assertTrue(session['is_partial'])
        self.assertFalse(session['is_complete'])
        self.assertContains(response, '1/2')

    def test_hub_history_tab_skips_today_sessions(self):
        response = self.client.get(reverse('portals:teacher-attendance') + '?tab=history')
        self.assertEqual(response.context['today_sessions'], [])
        self.assertNotContains(response, 'portal-attendance-today')

    def test_session_picker_renders_without_schedule(self):
        response = self.client.get(reverse('portals:teacher-attendance-session'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'portal-attendance-picker-calendar')

    def test_student_first_entry_shows_student_picker(self):
        response = self.client.get(reverse('portals:teacher-attendance-create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'portal-attendance-student-pick')

    def test_student_first_filtered_calendar(self):
        url = (
            reverse('portals:teacher-attendance-create')
            + f'?students={self.student_a.pk},{self.student_b.pk}'
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.group_one.name)
        self.assertNotContains(response, self.group_two.name)

    def test_student_first_no_common_group_warning(self):
        url = (
            reverse('portals:teacher-attendance-create')
            + f'?students={self.student_a.pk},{self.student_c.pk}'
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            _(
                'The selected students are not in the same group, or have no '
                'scheduled class this week.',
            ),
        )

    def test_partial_save_only_selected_students(self):
        response = self._post_attendance(
            {
                self.student_a.pk: Attendance.Status.PRESENT,
                self.student_b.pk: Attendance.Status.ABSENT,
            },
            selected_ids=[self.student_a.pk],
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Attendance.objects.count(), 1)
        record = Attendance.objects.get()
        self.assertEqual(record.student_id, self.student_a.pk)
        self.assertEqual(record.status, Attendance.Status.PRESENT)

    def test_save_updates_existing_record(self):
        Attendance.objects.create(
            schedule=self.schedule,
            student=self.student_a,
            session_date=self.session_date,
            status=Attendance.Status.ABSENT,
        )
        response = self._post_attendance(
            {self.student_a.pk: Attendance.Status.LATE},
            selected_ids=[self.student_a.pk],
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Attendance.objects.count(), 1)
        record = Attendance.objects.get()
        self.assertEqual(record.status, Attendance.Status.LATE)

    def test_post_without_selected_students_shows_error(self):
        data = {
            'schedule': self.schedule.pk,
            'date': self.session_date.isoformat(),
            f'status_{self.student_a.pk}': Attendance.Status.PRESENT,
        }
        response = self.client.post(self._session_url(), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Attendance.objects.count(), 0)

    def test_save_session_attendance_helper(self):
        count = save_session_attendance(
            self.schedule,
            self.session_date,
            {
                self.student_a.pk: Attendance.Status.PRESENT,
                self.student_b.pk: Attendance.Status.LATE,
            },
        )
        self.assertEqual(count, 2)
        self.assertEqual(Attendance.objects.count(), 2)

    def test_parse_student_ids_accepts_csv_and_lists(self):
        self.assertEqual(parse_student_ids('1,2,3'), [1, 2, 3])
        self.assertEqual(parse_student_ids(['1', '2']), [1, 2])

    def test_attendance_detail_not_doubled_when_group_has_multiple_courses(self):
        from portals.utils.queries import get_teacher_student_attendance_detail

        Service.objects.get_or_create(
            slug='speaking',
            defaults={'name_az': 'Speaking', 'name_en': 'Speaking', 'is_active': True},
        )
        TeacherCourseSpecialization.objects.get_or_create(
            teacher=self.teacher,
            course_type='speaking',
        )
        link_study_group_services(self.group_one, 'ielts', 'speaking')

        Attendance.objects.create(
            schedule=self.schedule,
            student=self.student_a,
            session_date=self.session_date,
            status=Attendance.Status.PRESENT,
        )

        detail = get_teacher_student_attendance_detail(self.teacher.pk, self.student_a.pk)
        self.assertIsNotNone(detail)
        self.assertEqual(detail['summary']['total'], 1)
        self.assertEqual(detail['summary']['present'], 1)
        self.assertEqual(len(detail['records']), 1)
