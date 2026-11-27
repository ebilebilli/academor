from datetime import date

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from portals.models import StudentProfile, StudyGroup, TeacherProfile
from portals.tests.portal_helpers import ensure_active_portal_services, portal_client_login

User = get_user_model()


class TeacherStudentEditTests(TestCase):
    def setUp(self):
        ensure_active_portal_services('ielts')
        self.teacher_user = User.objects.create_user(username='Teacher One', password='pass')
        self.teacher = TeacherProfile.objects.create(user=self.teacher_user)
        other_user = User.objects.create_user(username='Teacher Two', password='pass')
        self.other_teacher = TeacherProfile.objects.create(user=other_user)

        self.student_user = User.objects.create_user(username='Aysel Namizəd', password='old-pass')
        self.student = StudentProfile.objects.create(user=self.student_user, phone='+994501112233')
        self.morning = StudyGroup.objects.create(teacher=self.teacher, name='IELTS Morning', max_students=10)
        self.evening = StudyGroup.objects.create(teacher=self.teacher, name='IELTS Evening', max_students=10)
        self.foreign = StudyGroup.objects.create(teacher=self.other_teacher, name='Other teacher group', max_students=10)
        self.morning.students.add(self.student)
        self.foreign.students.add(self.student)

        self.stranger = StudentProfile.objects.create(user=User.objects.create_user(username='Test Namizəd', password='x'))
        self.foreign_only = StudyGroup.objects.create(teacher=self.other_teacher, name='Only theirs', max_students=10)
        self.foreign_only.students.add(self.stranger)

        self.client = Client()
        portal_client_login(self.client, self.teacher_user)
        self.url = reverse('portals:teacher-student-edit', kwargs={'student_pk': self.student.pk})

    def _post(self, **overrides):
        data = {
            'full_name': 'Aysel Namizəd',
            'phone': '+994501112233',
            'birth_date': '',
            'enrollment_date': '',
            'lessons_per_month': '',
            'program_month': '',
            'groups': [self.morning.pk],
            'password': '',
        }
        data.update(overrides)
        return self.client.post(self.url, data)

    def test_edit_page_shows_current_details(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertEqual(form.initial['full_name'], 'Aysel Namizəd')
        self.assertEqual(form.initial['groups'], [self.morning.pk])
        # only the teacher's own groups are offered
        self.assertEqual(set(form.fields['groups'].queryset), {self.morning, self.evening})

    def test_teacher_updates_name_phone_dates_and_groups(self):
        response = self._post(
            full_name='Aysel  Namizədova',
            phone='+994507654321',
            birth_date='2008-04-12',
            enrollment_date='2026-09-01',
            lessons_per_month='12',
            program_month='3',
            groups=[self.evening.pk],
        )
        self.assertRedirects(response, reverse('portals:teacher-groups'), fetch_redirect_response=False)
        self.student.refresh_from_db()
        self.student_user.refresh_from_db()
        self.assertEqual(self.student_user.username, 'Aysel Namizədova')
        self.assertEqual(self.student.phone, '+994507654321')
        self.assertEqual(self.student.birth_date, date(2008, 4, 12))
        self.assertEqual(self.student.enrollment_date, date(2026, 9, 1))
        self.assertEqual((self.student.lessons_per_month, self.student.program_month), (12, 3))
        groups = set(self.student.groups.all())
        self.assertEqual(groups, {self.evening, self.foreign})  # the other teacher's group stays
        self.assertTrue(self.student.teachers.filter(pk=self.teacher.pk).exists())

    def test_password_changes_only_when_given(self):
        self._post()
        self.student_user.refresh_from_db()
        self.assertTrue(self.student_user.check_password('old-pass'))
        self._post(password='new-pass-1')
        self.student_user.refresh_from_db()
        self.assertTrue(self.student_user.check_password('new-pass-1'))

    def test_name_taken_by_someone_else_is_refused(self):
        response = self._post(full_name='test namizəd')
        self.assertEqual(response.status_code, 200)
        self.assertIn('full_name', response.context['form'].errors)
        self.student_user.refresh_from_db()
        self.assertEqual(self.student_user.username, 'Aysel Namizəd')

    def test_full_group_is_refused(self):
        self.evening.max_students = 1
        self.evening.save()
        self.evening.students.add(self.stranger)
        response = self._post(groups=[self.morning.pk, self.evening.pk])
        self.assertEqual(response.status_code, 200)
        self.assertIn('groups', response.context['form'].errors)

    def test_other_teachers_student_is_not_found(self):
        url = reverse('portals:teacher-student-edit', kwargs={'student_pk': self.stranger.pk})
        self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(self.client.post(url, {'full_name': 'Hacked'}).status_code, 404)
        self.stranger.user.refresh_from_db()
        self.assertEqual(self.stranger.user.username, 'Test Namizəd')

    def test_next_returns_to_profile_but_never_off_site(self):
        profile = reverse('portals:teacher-student-profile', kwargs={'student_pk': self.student.pk})
        response = self._post(next=profile)
        self.assertRedirects(response, profile, fetch_redirect_response=False)
        response = self._post(next='//evil.example.com/portal/teacher/')
        self.assertRedirects(response, reverse('portals:teacher-groups'), fetch_redirect_response=False)
        response = self._post(next='https://evil.example.com/')
        self.assertRedirects(response, reverse('portals:teacher-groups'), fetch_redirect_response=False)

    def test_students_page_and_profile_link_to_the_edit_form(self):
        page = self.client.get(reverse('portals:teacher-groups'))
        self.assertContains(page, self.url)
        profile = self.client.get(reverse('portals:teacher-student-profile', kwargs={'student_pk': self.student.pk}))
        self.assertContains(profile, self.url)
