from datetime import date, time

from django.contrib.auth import get_user_model
from django.test import TestCase

from portals.models import Attendance, Schedule, StudentProfile, StudyGroup, TeacherProfile
from portals.utils.qrup_import_helpers import (
    iter_group_sessions,
    parse_lessons_participation,
    sync_student_participation,
)

User = get_user_model()


class QrupParticipationImportTests(TestCase):
    def setUp(self):
        teacher_user = User.objects.create_user(username='part_teacher', password='pass')
        student_user = User.objects.create_user(username='part_student', password='pass')
        self.teacher = TeacherProfile.objects.create(user=teacher_user)
        self.student = StudentProfile.objects.create(user=student_user)
        self.group = StudyGroup.objects.create(
            name='Test Group',
            teacher=self.teacher,
            max_students=12,
        )
        Schedule.objects.create(
            group=self.group,
            weekday=0,
            start_time=time(14, 0),
            duration_min=90,
            effective_from=date(2026, 1, 1),
        )
        Schedule.objects.create(
            group=self.group,
            weekday=2,
            start_time=time(14, 0),
            duration_min=90,
            effective_from=date(2026, 1, 1),
        )

    def test_parse_lessons_participation_scales_by_month(self):
        payload = parse_lessons_participation('8/12', 2)
        self.assertEqual(payload['lessons_attended'], 8)
        self.assertEqual(payload['lessons_per_month'], 12)
        self.assertEqual(payload['month_number'], 2)
        self.assertEqual(payload['total_sessions'], 24)

    def test_sync_student_participation_marks_present_only(self):
        participation = parse_lessons_participation('3/8', 2)
        saved = sync_student_participation(
            self.student,
            self.group,
            participation,
            start_date=date(2026, 6, 2),
        )
        self.assertEqual(saved, 3)
        self.assertEqual(
            Attendance.objects.filter(student=self.student, status='present').count(),
            3,
        )
        self.assertFalse(
            Attendance.objects.filter(student=self.student, status='absent').exists(),
        )

    def test_iter_group_sessions_respects_two_day_schedule(self):
        sessions = iter_group_sessions(
            self.group,
            date(2026, 6, 2),
            max_sessions=16,
        )
        self.assertEqual(len(sessions), 16)
