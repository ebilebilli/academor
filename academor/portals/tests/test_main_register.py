import importlib
from datetime import date

from django.apps import apps
from django.contrib.auth import get_user_model
from django.test import TestCase

from portals.models import Attendance, AttendanceRegisterGuest, StudentProfile, StudyGroup, TeacherProfile
from portals.utils.teacher_attendance_register import (
    MAIN_REGISTER_NAME,
    build_teacher_attendance_register,
    remove_register_group,
    save_register_mark,
    teacher_main_register,
)

create_main_registers = importlib.import_module(
    'portals.migrations.0123_create_main_registers'
).create_main_registers


class MainRegisterTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.teacher = TeacherProfile.objects.create(user=User.objects.create(username='ramil'))
        self.group = StudyGroup.objects.create(
            teacher=self.teacher, name='Foundation IELTS Qrup 2/4/6', start_date=date(2026, 10, 1),
        )
        self.other = StudyGroup.objects.create(teacher=self.teacher, name='IELTS Axşam', start_date=date(2026, 10, 1))
        self.student = StudentProfile.objects.create(user=User.objects.create(username='nihad'))
        self.other.students.add(self.student)

    def _guest_with_marks(self, group, name, days):
        guest = AttendanceRegisterGuest.objects.create(group=group, name=name)
        for day, status in days:
            Attendance.objects.create(group=group, guest=guest, session_date=date(2026, 10, day), status=status)
        return guest

    def test_migration_moves_guests_and_marks_into_the_general_register(self):
        self._guest_with_marks(self.group, 'Ali', [(1, 'present'), (3, 'absent')])
        self._guest_with_marks(self.group, 'Aysel', [(1, 'present')])
        create_main_registers(apps, None)
        main = StudyGroup.objects.get(teacher=self.teacher, is_main_register=True)
        self.assertEqual(main.name, MAIN_REGISTER_NAME)
        self.assertTrue(main.is_register_only)
        self.assertEqual(sorted(main.register_guests.values_list('name', flat=True)), ['Ali', 'Aysel'])
        self.assertEqual(Attendance.objects.filter(group=main).count(), 3)
        self.assertFalse(AttendanceRegisterGuest.objects.filter(group=self.group).exists())
        # the original group keeps its name; running again changes nothing
        self.group.refresh_from_db()
        self.assertEqual(self.group.name, 'Foundation IELTS Qrup 2/4/6')
        create_main_registers(apps, None)
        self.assertEqual(StudyGroup.objects.filter(teacher=self.teacher, is_main_register=True).count(), 1)
        self.assertEqual(Attendance.objects.filter(group=main).count(), 3)

    def test_migration_merges_a_name_already_on_the_general_register(self):
        main = teacher_main_register(self.teacher)
        self._guest_with_marks(main, 'Ali', [(1, 'present')])
        self._guest_with_marks(self.group, 'ali', [(1, 'absent'), (5, 'late')])
        create_main_registers(apps, None)
        self.assertEqual(main.register_guests.count(), 1)
        marks = dict(Attendance.objects.filter(group=main).values_list('session_date', 'status'))
        self.assertEqual(marks[date(2026, 10, 5)], 'late')
        self.assertEqual(len(marks), 2)

    def test_general_register_lists_every_student_and_comes_first(self):
        Attendance.objects.create(group=self.other, student=self.student, session_date=date(2026, 10, 6), status='late')
        register = build_teacher_attendance_register(self.teacher, year=2026, month=10)
        self.assertTrue(register['group']['is_main_register'])
        self.assertTrue(register['groups'][0]['is_main_register'])
        row = next(r for r in register['students'] if r['id'] == self.student.pk)
        self.assertEqual(row['late_count'], 1)

    def test_marking_on_the_general_register_updates_the_existing_day(self):
        Attendance.objects.create(group=self.other, student=self.student, session_date=date(2026, 10, 6), status='late')
        main = teacher_main_register(self.teacher)
        result = save_register_mark(group=main, student=self.student, session_date=date(2026, 10, 6), status='present')
        self.assertTrue(result['ok'])
        self.assertEqual(Attendance.objects.filter(student=self.student, session_date=date(2026, 10, 6)).count(), 1)
        save_register_mark(group=main, student=self.student, session_date=date(2026, 10, 8), status='absent')
        # a new mark is filed under the student's own group, so their portal shows it there
        self.assertEqual(Attendance.objects.get(student=self.student, session_date=date(2026, 10, 8)).group, self.other)
        register = build_teacher_attendance_register(self.teacher, year=2026, month=10, group=main)
        row = next(r for r in register['students'] if r['id'] == self.student.pk)
        self.assertEqual((row['present_count'], row['absent_count']), (1, 1))

    def test_general_register_cannot_be_removed(self):
        main = teacher_main_register(self.teacher)
        self.assertFalse(remove_register_group(teacher=self.teacher, group=main)['ok'])
