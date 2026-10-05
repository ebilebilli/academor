from datetime import date, time, timedelta
import json

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from django.utils.translation import gettext as _

from portals.middleware import PortalSessionMiddleware
from portals.models import (
    Attendance,
    AttendanceRegisterGuest,
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

    def _register_page(self, **params):
        params.setdefault('tab', 'mark')
        params.setdefault('group', self.group_one.pk)
        query = '&'.join(f'{key}={value}' for key, value in params.items())
        return self.client.get(f"{reverse('portals:teacher-attendance')}?{query}")

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
        self.assertContains(response, 'data-attendance-register')
        self.assertContains(response, 'portal-register-table')
        self.assertNotContains(response, 'attendance-hub-panel')
        self.assertNotContains(response, 'id="attendance-hub-stats"')

    def test_hub_history_tab_shows_students(self):
        response = self.client.get(reverse('portals:teacher-attendance') + '?tab=history')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['hub_tab'], 'history')
        self.assertContains(response, 'attendance-hub-panel')
        self.assertContains(response, 'id="attendance-hub-stats"')
        self.assertNotContains(response, 'data-attendance-register')

    def test_hub_invalid_tab_falls_back_to_mark(self):
        response = self.client.get(reverse('portals:teacher-attendance') + '?tab=unknown')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['hub_tab'], 'mark')
        self.assertContains(response, 'data-attendance-register')

    def test_hub_mark_tab_lists_group_students(self):
        response = self._register_page()
        self.assertEqual(response.status_code, 200)
        register = response.context['register']
        self.assertEqual(register['group']['id'], self.group_one.pk)
        student_ids = {row['id'] for row in register['students']}
        self.assertIn(self.student_a.pk, student_ids)
        self.assertIn(self.student_b.pk, student_ids)
        self.assertNotIn(self.student_c.pk, student_ids)
        self.assertContains(response, self.student_a_user.username)
        self.assertContains(response, 'Excel yüklə')

    def test_hub_mark_tab_month_navigation(self):
        response = self._register_page(month='2026-02')
        register = response.context['register']
        self.assertEqual(register['month_key'], '2026-02')
        self.assertEqual(register['prev_month'], '2026-01')
        self.assertEqual(register['next_month'], '2026-03')
        self.assertEqual(register['days_in_month'], 28)
        disabled_days = [
            day['n'] for day in register['days'] if not day['in_month']
        ]
        self.assertEqual(disabled_days, [29, 30, 31])

    def test_register_hides_students_who_start_after_month(self):
        next_month = date.today().replace(day=1) + timedelta(days=32)
        self.student_b.enrollment_date = next_month.replace(day=1)
        self.student_b.save()
        response = self._register_page()
        student_ids = {row['id'] for row in response.context['register']['students']}
        self.assertIn(self.student_a.pk, student_ids)
        self.assertNotIn(self.student_b.pk, student_ids)

    def test_register_disables_days_before_enrollment(self):
        self.student_a.enrollment_date = date.today().replace(day=15)
        self.student_a.save()
        month = date.today().strftime('%Y-%m')
        response = self._register_page(month=month)
        row = next(
            item
            for item in response.context['register']['students']
            if item['id'] == self.student_a.pk
        )
        self.assertTrue(row['cells'][0]['disabled'])
        self.assertEqual(row['cells'][0]['reason'], 'before_start')
        self.assertFalse(row['cells'][14]['disabled'])

    def test_hub_history_tab_skips_register(self):
        response = self.client.get(reverse('portals:teacher-attendance') + '?tab=history')
        self.assertIsNone(response.context['register'])
        self.assertNotContains(response, 'portal-register-table')

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

    def _register_mark(self, student, session_date, status, group=None):
        return self.client.post(
            reverse('portals:teacher-attendance-register-mark'),
            data=json.dumps({
                'group_id': (group or self.group_one).pk,
                'student_id': student.pk,
                'date': session_date.isoformat(),
                'status': status,
            }),
            content_type='application/json',
        )

    def test_register_mark_autosaves_present(self):
        response = self._register_mark(
            self.student_a,
            self.session_date,
            Attendance.Status.PRESENT,
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload['ok'])
        self.assertEqual(payload['status'], Attendance.Status.PRESENT)
        self.assertEqual(payload['attended'], 1)
        record = Attendance.objects.get()
        self.assertEqual(record.student_id, self.student_a.pk)
        self.assertEqual(record.group_id, self.group_one.pk)
        self.assertIsNone(record.schedule_id)
        self.assertEqual(record.status, Attendance.Status.PRESENT)

    def test_register_mark_updates_existing_session_record(self):
        Attendance.objects.create(
            schedule=self.schedule,
            student=self.student_a,
            session_date=self.session_date,
            status=Attendance.Status.ABSENT,
        )
        response = self._register_mark(
            self.student_a,
            self.session_date,
            Attendance.Status.LATE,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Attendance.objects.count(), 1)
        record = Attendance.objects.get()
        self.assertEqual(record.status, Attendance.Status.LATE)
        self.assertEqual(record.schedule_id, self.schedule.pk)

    def test_register_mark_clear_deletes_record(self):
        Attendance.objects.create(
            schedule=None,
            group=self.group_one,
            student=self.student_a,
            session_date=self.session_date,
            status=Attendance.Status.PRESENT,
        )
        response = self._register_mark(self.student_a, self.session_date, '')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], '')
        self.assertEqual(Attendance.objects.count(), 0)

    def test_register_mark_rejects_student_from_other_group(self):
        response = self._register_mark(
            self.student_c,
            self.session_date,
            Attendance.Status.PRESENT,
            group=self.group_one,
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Attendance.objects.count(), 0)

    def test_register_mark_rejects_day_before_enrollment(self):
        self.student_a.enrollment_date = self.session_date + timedelta(days=3)
        self.student_a.save()
        response = self._register_mark(
            self.student_a,
            self.session_date,
            Attendance.Status.PRESENT,
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Attendance.objects.count(), 0)

    def test_register_add_guest_and_mark(self):
        add_response = self.client.post(
            reverse('portals:teacher-attendance-register-guest'),
            data=json.dumps({
                'group_id': self.group_one.pk,
                'name': '  Qonaq Tələbə  ',
            }),
            content_type='application/json',
        )
        self.assertEqual(add_response.status_code, 200)
        guest_payload = add_response.json()
        self.assertTrue(guest_payload['ok'])
        guest_id = guest_payload['guest']['id']
        self.assertEqual(guest_payload['guest']['name'], 'Qonaq Tələbə')

        page = self._register_page()
        names = [row['name'] for row in page.context['register']['students']]
        self.assertIn('Qonaq Tələbə', names)

        mark_response = self.client.post(
            reverse('portals:teacher-attendance-register-mark'),
            data=json.dumps({
                'group_id': self.group_one.pk,
                'guest_id': guest_id,
                'date': self.session_date.isoformat(),
                'status': Attendance.Status.ABSENT,
            }),
            content_type='application/json',
        )
        self.assertEqual(mark_response.status_code, 200)
        self.assertEqual(mark_response.json()['absent'], 1)
        record = Attendance.objects.get(guest_id=guest_id)
        self.assertIsNone(record.student_id)
        self.assertEqual(record.status, Attendance.Status.ABSENT)

    def test_register_remove_guest_hides_from_grid(self):
        guest = AttendanceRegisterGuest.objects.create(
            group=self.group_one,
            name='Müvəqqəti',
        )
        response = self.client.delete(
            reverse('portals:teacher-attendance-register-guest'),
            data=json.dumps({
                'group_id': self.group_one.pk,
                'guest_id': guest.pk,
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        guest.refresh_from_db()
        self.assertFalse(guest.is_active)
        page = self._register_page()
        guest_ids = [
            row['guest_id']
            for row in page.context['register']['students']
            if row['is_guest']
        ]
        self.assertNotIn(guest.pk, guest_ids)

    def test_register_add_manual_group(self):
        response = self.client.post(
            reverse('portals:teacher-attendance-register-group'),
            data=json.dumps({'name': '  Xüsusi Qrup  '}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload['ok'])
        group_id = payload['group']['id']
        self.assertTrue(payload['group']['is_register_only'])

        page = self._register_page(group=group_id)
        register = page.context['register']
        self.assertEqual(register['group']['id'], group_id)
        self.assertTrue(register['group']['is_register_only'])
        self.assertEqual(register['group']['name'], 'Xüsusi Qrup')
        # Manual group must not pollute normal teacher group lists.
        from portals.utils.teacher_courses import teacher_groups_queryset
        self.assertFalse(
            teacher_groups_queryset(self.teacher.pk).filter(pk=group_id).exists()
        )
        self.assertTrue(
            teacher_groups_queryset(
                self.teacher.pk,
                include_register_only=True,
            ).filter(pk=group_id).exists()
        )

    def test_register_remove_manual_group(self):
        create = self.client.post(
            reverse('portals:teacher-attendance-register-group'),
            data=json.dumps({'name': 'Silinəcək'}),
            content_type='application/json',
        )
        group_id = create.json()['group']['id']
        response = self.client.delete(
            reverse('portals:teacher-attendance-register-group'),
            data=json.dumps({'group_id': group_id}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        page = self._register_page()
        ids = [row['id'] for row in page.context['register']['groups']]
        self.assertNotIn(group_id, ids)

    def test_cannot_remove_portal_group_via_register(self):
        response = self.client.delete(
            reverse('portals:teacher-attendance-register-group'),
            data=json.dumps({'group_id': self.group_one.pk}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.group_one.refresh_from_db()
        self.assertTrue(self.group_one.is_active)
