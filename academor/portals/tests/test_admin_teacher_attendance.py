from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from portals.models import Attendance, StudentProfile, StudyGroup, TeacherProfile
from portals.utils.admin_teacher_attendance import build_teacher_attendance_overview


class TeacherAttendanceOverviewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.teacher = TeacherProfile.objects.create(user=User.objects.create(username='teacher_one'))
        self.group = StudyGroup.objects.create(
            teacher=self.teacher, name='IELTS 1', start_date=date(2026, 10, 1), is_active=True,
        )
        self.student = StudentProfile.objects.create(user=User.objects.create(username='student_one'))
        self.group.students.add(self.student)
        for day, status in ((5, 'present'), (7, 'late'), (9, 'absent'), (12, 'present')):
            Attendance.objects.create(
                group=self.group, student=self.student, session_date=date(2026, 10, day), status=status,
            )

    def test_overview_counts_and_rate(self):
        data = build_teacher_attendance_overview(teacher_id=self.teacher.pk, year=2026, month=10)
        row = next(t for t in data['teachers'] if t['id'] == self.teacher.pk)
        self.assertEqual((row['present'], row['late'], row['absent']), (2, 1, 1))
        self.assertEqual(row['rate'], 75)  # late counts as attended
        detail = data['detail']
        # totals come from the teacher's general register, which shows the group's marks
        self.assertTrue(detail['main']['is_main_register'])
        self.assertEqual(detail['rate'], 75)
        self.assertEqual(detail['lesson_days'], 4)
        cells = {c['iso']: c['status'] for c in detail['main']['rows'][0]['cells']}
        self.assertEqual(cells['2026-10-09'], 'absent')
        self.assertEqual([g['name'] for g in detail['groups']], ['IELTS 1'])
        self.assertEqual(detail['group_count'], 1)
        self.assertEqual(len(detail['chart']), 31)

    def test_month_without_marks(self):
        data = build_teacher_attendance_overview(teacher_id=self.teacher.pk, year=2026, month=9)
        self.assertIsNone(data['detail']['rate'])
        self.assertEqual(data['prev_month'], '2026-08')
        self.assertEqual(data['next_month'], '2026-10')

    def test_admin_page_renders(self):
        admin = get_user_model().objects.create_superuser('boss', 'boss@example.com', 'pass12345')
        self.client.force_login(admin)
        url = reverse('admin:portals_attendance_teachers')
        response = self.client.get(url, {'teacher': self.teacher.pk, 'month': '2026-10'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'IELTS 1')
        self.assertContains(response, 'Ümumi davamiyyət cədvəli')
        self.assertContains(response, 'ta-cell--absent')
