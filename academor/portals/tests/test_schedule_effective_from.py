from datetime import date, time, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase

from portals.models import Schedule, StudentProfile, StudyGroup, TeacherProfile
from portals.utils.teacher_schedule import build_student_week_calendar, build_teacher_week_calendar
from portals.tests.group_helpers import link_study_group_services

User = get_user_model()


class ScheduleEffectiveFromTests(TestCase):
    def setUp(self):
        self.teacher_user = User.objects.create_user(username='sched_teacher', password='pass')
        self.student_user = User.objects.create_user(username='sched_student', password='pass')
        self.teacher = TeacherProfile.objects.create(user=self.teacher_user)
        self.student = StudentProfile.objects.create(user=self.student_user)

        self.group = StudyGroup.objects.create(
            teacher=self.teacher,
            name='Schedule group',
            max_students=10,
        )
        link_study_group_services(self.group, 'ielts')
        self.group.students.add(self.student)

        self.effective_from = date(2026, 5, 12)
        self.schedule = Schedule.objects.create(
            group=self.group,
            weekday=1,  # Tuesday
            start_time=time(18, 0),
            duration_min=90,
            effective_from=self.effective_from,
        )

    def test_past_week_hidden_for_teacher_calendar(self):
        week_start = date(2026, 5, 4)  # Mon 4 May — Tue session would be 5 May
        calendar = build_teacher_week_calendar(self.teacher.pk, week_start=week_start)
        sessions = [session for day in calendar['days'] for session in day['sessions']]
        self.assertEqual(sessions, [])

    def test_active_week_shown_for_teacher_calendar(self):
        week_start = date(2026, 5, 11)  # Mon 11 May — Tue session is 12 May
        calendar = build_teacher_week_calendar(self.teacher.pk, week_start=week_start)
        sessions = [session for day in calendar['days'] for session in day['sessions']]
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0]['session_date'], date(2026, 5, 12))

    def test_past_week_hidden_for_student_calendar(self):
        week_start = self.effective_from - timedelta(days=self.effective_from.weekday() + 7)
        calendar = build_student_week_calendar(self.student.pk, week_start=week_start)
        sessions = [session for day in calendar['days'] for session in day['sessions']]
        self.assertEqual(sessions, [])

    def test_active_week_shown_for_student_calendar(self):
        week_start = self.effective_from - timedelta(days=self.effective_from.weekday())
        calendar = build_student_week_calendar(self.student.pk, week_start=week_start)
        sessions = [session for day in calendar['days'] for session in day['sessions']]
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0]['session_date'], self.effective_from)

    def test_duplicate_schedule_slots_show_once_in_teacher_calendar(self):
        Schedule.objects.create(
            group=self.group,
            weekday=1,
            start_time=time(18, 0),
            duration_min=90,
            effective_from=date(2026, 4, 1),
        )
        week_start = self.effective_from - timedelta(days=self.effective_from.weekday())
        calendar = build_teacher_week_calendar(self.teacher.pk, week_start=week_start)
        tuesday_sessions = calendar['days'][1]['sessions']
        same_group_time = [
            session for session in tuesday_sessions
            if session['group_id'] == self.group.pk and session['start_time'] == time(18, 0)
        ]
        self.assertEqual(len(same_group_time), 1)
        self.assertEqual(same_group_time[0]['schedule_id'], self.schedule.pk)
