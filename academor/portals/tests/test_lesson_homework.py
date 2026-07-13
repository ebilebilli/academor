"""Tests for student lesson homework upload and teacher visibility."""

from datetime import date

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from portals.homework_forms import StudentLessonHomeworkForm
from portals.models import Lesson, LessonHomework, PortalNotification, StudentProfile, StudyGroup, TeacherProfile
from portals.tests.group_helpers import link_study_group_services
from portals.tests.portal_helpers import ensure_active_portal_services, portal_client_login
from portals.utils.notifications import get_notifications, get_unread_notification_count
from portals.utils.queries import get_lesson_homeworks_for_teacher
from projects.models.service_models import Service

User = get_user_model()


@override_settings(
    PORTAL_SESSION_COOKIE_NAME='portal_sessionid',
    PORTAL_SESSION_COOKIE_PATH='/portal/',
)
class LessonHomeworkTests(TestCase):
    def setUp(self):
        ensure_active_portal_services('ielts')
        Service.objects.get_or_create(
            slug='ielts',
            defaults={'name_az': 'IELTS', 'name_en': 'IELTS', 'is_active': True},
        )

        self.teacher_user = User.objects.create_user(username='hw_teacher', password='pass')
        self.other_teacher_user = User.objects.create_user(username='hw_teacher2', password='pass')
        self.student_user = User.objects.create_user(username='hw_student', password='pass')
        self.outsider_user = User.objects.create_user(username='hw_outsider', password='pass')

        self.teacher = TeacherProfile.objects.create(user=self.teacher_user)
        self.other_teacher = TeacherProfile.objects.create(user=self.other_teacher_user)
        self.student = StudentProfile.objects.create(user=self.student_user)
        self.outsider = StudentProfile.objects.create(user=self.outsider_user)

        self.group = StudyGroup.objects.create(
            teacher=self.teacher,
            name='HW Group',
            max_students=10,
        )
        link_study_group_services(self.group, 'ielts')
        self.group.students.add(self.student)

        self.lesson = Lesson.objects.create(
            group=self.group,
            teacher=self.teacher,
            subject='ielts',
            name='Unit 1',
            lesson_date=date.today(),
            description='Practice',
            video_url='https://example.com/video.mp4',
        )

        self.client = Client()
        self.detail_url = reverse('portals:student-lesson-detail', kwargs={'pk': self.lesson.pk})
        self.teacher_url = reverse('portals:teacher-lesson-detail', kwargs={'pk': self.lesson.pk})

    def test_student_can_submit_text_and_file(self):
        portal_client_login(self.client, self.student_user)
        upload = SimpleUploadedFile('notes.txt', b'hello homework', content_type='text/plain')
        response = self.client.post(
            self.detail_url,
            {'text': 'My answers', 'file': upload},
        )
        self.assertEqual(response.status_code, 302)
        hw = LessonHomework.objects.get(lesson=self.lesson, student=self.student)
        self.assertEqual(hw.text, 'My answers')
        self.assertEqual(hw.file_kind, LessonHomework.FileKind.TXT)
        self.assertEqual(hw.original_filename, 'notes.txt')
        self.assertTrue(hw.file.name)

    def test_student_not_in_group_gets_404(self):
        portal_client_login(self.client, self.outsider_user)
        response = self.client.post(self.detail_url, {'text': 'Nope'})
        self.assertEqual(response.status_code, 404)
        self.assertFalse(LessonHomework.objects.exists())

    def test_resubmit_replaces_file(self):
        portal_client_login(self.client, self.student_user)
        first = SimpleUploadedFile('one.txt', b'first', content_type='text/plain')
        self.client.post(self.detail_url, {'text': 'v1', 'file': first})
        hw = LessonHomework.objects.get(lesson=self.lesson, student=self.student)
        old_name = hw.file.name
        old_submitted = hw.submitted_at

        second = SimpleUploadedFile('two.pdf', b'%PDF-1.4 fake', content_type='application/pdf')
        response = self.client.post(self.detail_url, {'text': 'v2', 'file': second})
        self.assertEqual(response.status_code, 302)

        hw.refresh_from_db()
        self.assertEqual(LessonHomework.objects.filter(lesson=self.lesson, student=self.student).count(), 1)
        self.assertEqual(hw.text, 'v2')
        self.assertEqual(hw.file_kind, LessonHomework.FileKind.PDF)
        self.assertEqual(hw.original_filename, 'two.pdf')
        self.assertNotEqual(hw.file.name, old_name)
        self.assertGreaterEqual(hw.submitted_at, old_submitted)

    def test_reject_bad_extension(self):
        form = StudentLessonHomeworkForm(
            data={'text': ''},
            files={
                'file': SimpleUploadedFile('virus.exe', b'MZ', content_type='application/octet-stream'),
            },
        )
        self.assertFalse(form.is_valid())
        self.assertIn('file', form.errors)

    def test_teacher_sees_lesson_homeworks(self):
        LessonHomework.objects.create(
            lesson=self.lesson,
            student=self.student,
            text='Done',
        )
        portal_client_login(self.client, self.teacher_user)
        response = self.client.get(self.teacher_url)
        self.assertEqual(response.status_code, 200)
        homeworks = response.context['lesson_homeworks']
        self.assertEqual(len(homeworks), 1)
        self.assertEqual(homeworks[0]['text'], 'Done')
        self.assertEqual(homeworks[0]['student_name'], self.student.full_name)

        rows = get_lesson_homeworks_for_teacher(self.lesson)
        self.assertEqual(len(rows), 1)

    def test_other_teacher_gets_404(self):
        portal_client_login(self.client, self.other_teacher_user)
        response = self.client.get(self.teacher_url)
        self.assertEqual(response.status_code, 404)

    def test_student_homework_detail_page(self):
        hw = LessonHomework.objects.create(
            lesson=self.lesson,
            student=self.student,
            text='Detail body',
        )
        portal_client_login(self.client, self.student_user)
        url = reverse('portals:student-homework-detail', kwargs={'pk': hw.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Detail body')
        self.assertContains(response, self.lesson.display_name)
        self.assertNotContains(response, 'name="text"')

    def test_outsider_cannot_open_homework_detail(self):
        hw = LessonHomework.objects.create(
            lesson=self.lesson,
            student=self.student,
            text='Secret',
        )
        portal_client_login(self.client, self.outsider_user)
        url = reverse('portals:student-homework-detail', kwargs={'pk': hw.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_lessons_list_shows_homework_summary_not_full_text(self):
        LessonHomework.objects.create(
            lesson=self.lesson,
            student=self.student,
            text='Full homework text should stay on detail page only',
        )
        portal_client_login(self.client, self.student_user)
        response = self.client.get(reverse('portals:student-lessons'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.lesson.display_name)
        self.assertNotContains(response, 'Full homework text should stay on detail page only')

    def test_submit_notifies_teacher(self):
        portal_client_login(self.client, self.student_user)
        response = self.client.post(self.detail_url, {'text': 'Notify teacher please'})
        self.assertEqual(response.status_code, 302)

        hw = LessonHomework.objects.get(lesson=self.lesson, student=self.student)
        notif = PortalNotification.objects.get(
            teacher=self.teacher,
            lesson_homework=hw,
            kind=PortalNotification.Kind.HOMEWORK_SUBMITTED,
        )
        self.assertFalse(notif.is_read)
        self.assertEqual(get_unread_notification_count(teacher_id=self.teacher.pk), 1)

        items = get_notifications(teacher_id=self.teacher.pk, period='all')
        self.assertEqual(len(items), 1)
        self.assertTrue(items[0]['is_homework_submitted'])
        self.assertEqual(items[0]['student_name'], self.student.full_name)
        self.assertIn(
            reverse('portals:teacher-lesson-detail', kwargs={'pk': self.lesson.pk}),
            items[0]['score_detail_url'],
        )

        # Resubmit refreshes unread state on the same notification row.
        notif.is_read = True
        notif.save(update_fields=['is_read'])
        self.client.post(self.detail_url, {'text': 'Updated homework'})
        notif.refresh_from_db()
        self.assertFalse(notif.is_read)
        self.assertEqual(
            PortalNotification.objects.filter(
                teacher=self.teacher,
                lesson_homework=hw,
                kind=PortalNotification.Kind.HOMEWORK_SUBMITTED,
            ).count(),
            1,
        )
