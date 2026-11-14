"""Data migration 0128: group services -> student services, defaults, register names -> students.

Runs the real migration on a database rolled back to 0127. Fictional names only.
"""

from datetime import date

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase

BEFORE = [('portals', '0127_student_active_teachers_lesson_targets')]
AFTER = [('portals', '0128_student_services_from_groups_and_register_students')]


class StudentServicesMigrationTests(TransactionTestCase):
    def setUp(self):
        executor = MigrationExecutor(connection)
        executor.migrate(BEFORE)
        self.old_apps = executor.loader.project_state(BEFORE).apps

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(executor.loader.graph.leaf_nodes())

    def _migrate(self):
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(AFTER)
        return executor.loader.project_state(AFTER).apps

    def test_carries_data_over(self):
        apps = self.old_apps
        User = apps.get_model('auth', 'User')
        Service = apps.get_model('projects', 'Service')
        Teacher = apps.get_model('portals', 'TeacherProfile')
        Student = apps.get_model('portals', 'StudentProfile')
        Spec = apps.get_model('portals', 'StudentCourseSpecialization')
        Group = apps.get_model('portals', 'StudyGroup')
        Guest = apps.get_model('portals', 'AttendanceRegisterGuest')
        Attendance = apps.get_model('portals', 'Attendance')

        for slug, name in (('ielts', 'IELTS'), ('general-english', 'General English'), ('sat', 'SAT')):
            Service.objects.create(slug=slug, name_az=name, name_en=name, is_active=True)
        sat = Service.objects.get(slug='sat')

        teacher = Teacher.objects.create(user=User.objects.create(username='Mig Teacher'))
        sat_group = Group.objects.create(teacher=teacher, name='SAT A', max_students=10)
        sat_group.courses.add(sat)
        register_group = Group.objects.create(
            teacher=teacher, name='Hand list', max_students=10, is_register_only=True,
        )

        in_sat_group = Student.objects.create(user=User.objects.create(username='Mig Sat'))
        sat_group.students.add(in_sat_group)
        no_service = Student.objects.create(user=User.objects.create(username='Mig Empty'))
        ielts_only = Student.objects.create(user=User.objects.create(username='Mig Ielts'))
        Spec.objects.create(student=ielts_only, course_type='ielts', is_active=True)

        guest = Guest.objects.create(group=register_group, name='Mig Guest')
        Attendance.objects.create(
            group=register_group, guest=guest, session_date=date(2026, 11, 2), status='present',
        )

        apps = self._migrate()
        Student = apps.get_model('portals', 'StudentProfile')
        Spec = apps.get_model('portals', 'StudentCourseSpecialization')
        Group = apps.get_model('portals', 'StudyGroup')
        Guest = apps.get_model('portals', 'AttendanceRegisterGuest')
        Attendance = apps.get_model('portals', 'Attendance')

        def codes(username):
            return set(
                Spec.objects.filter(student__user__username=username, is_active=True)
                .values_list('course_type', flat=True)
            )

        # 1. the group's service became the student's own
        self.assertIn('sat', codes('Mig Sat'))
        # 2. nothing at all -> IELTS + General English
        self.assertEqual(codes('Mig Empty'), {'ielts', 'general_english'})
        # 3. IELTS students get General English on
        self.assertEqual(codes('Mig Ielts'), {'ielts', 'general_english'})
        # 4. the register name is a real student of the teacher, marks moved with it
        new_student = Student.objects.get(user__username='Mig Guest')
        self.assertTrue(new_student.teachers.filter(pk=teacher.pk).exists())
        self.assertTrue(new_student.groups.filter(pk=register_group.pk).exists())
        self.assertTrue(new_student.user.password.startswith('!'))  # unusable: no password yet
        self.assertEqual(codes('Mig Guest'), {'ielts', 'general_english'})
        mark = Attendance.objects.get(session_date=date(2026, 11, 2))
        self.assertEqual(mark.student_id, new_student.pk)
        self.assertIsNone(mark.guest_id)
        self.assertFalse(Guest.objects.get(pk=guest.pk).is_active)
        # 5. register-only groups are ordinary groups now
        self.assertFalse(Group.objects.get(pk=register_group.pk).is_register_only)
        del no_service
