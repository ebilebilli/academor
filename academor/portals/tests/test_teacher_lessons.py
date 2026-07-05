from datetime import date

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from portals.models import Lesson, LessonAttachment, StudentProfile, StudyGroup, TeacherProfile
from portals.teacher_forms import TeacherLessonForm
from portals.utils.group_services import resolve_group_lesson_service
from portals.utils.lesson_media import build_lesson_edit_materials
from portals.utils.queries import get_student_lessons, get_teacher_lessons
from portals.tests.group_helpers import link_study_group_services
from projects.models.service_models import Service

User = get_user_model()


def _ensure_ielts_service():
    Service.objects.get_or_create(
        slug='ielts',
        defaults={'name_az': 'IELTS', 'name_en': 'IELTS', 'is_active': True},
    )


class TeacherLessonCreateTests(TestCase):
    def setUp(self):
        _ensure_ielts_service()

        self.teacher_user = User.objects.create_user(username='lesson_teacher', password='pass')
        self.other_teacher_user = User.objects.create_user(username='lesson_teacher2', password='pass')
        self.student_user = User.objects.create_user(username='lesson_student', password='pass')

        self.teacher = TeacherProfile.objects.create(user=self.teacher_user)
        self.other_teacher = TeacherProfile.objects.create(user=self.other_teacher_user)
        self.student = StudentProfile.objects.create(user=self.student_user)

        self.group = StudyGroup.objects.create(
            teacher=self.teacher,
            name='IELTS A',
            max_students=10,
        )
        link_study_group_services(self.group, 'ielts')
        self.group.students.add(self.student)

    def test_service_derived_from_group_courses(self):
        self.assertEqual(resolve_group_lesson_service(self.group), 'ielts')

    def test_teacher_without_specializations_can_create_lesson(self):
        form = TeacherLessonForm(
            self.teacher.pk,
            data={
                'name': 'Unit 1',
                'lesson_date': date.today().isoformat(),
                'category_name': 'Grammar',
                'groups': [self.group.pk],
                'description': '',
                'new_video_urls': ['https://www.youtube.com/watch?v=test12345'],
            },
        )
        self.assertTrue(form.is_valid(), form.errors)
        lessons = form.save_for_groups(self.teacher)
        self.assertEqual(len(lessons), 1)
        lesson = lessons[0]
        self.assertEqual(lesson.subject, 'ielts')
        self.assertEqual(lesson.category.name, 'Grammar')
        self.assertEqual(lesson.group_id, self.group.pk)
        self.assertEqual(lesson.teacher_id, self.teacher.pk)

    def test_category_is_optional(self):
        form = TeacherLessonForm(
            self.teacher.pk,
            data={
                'name': 'No category lesson',
                'lesson_date': date.today().isoformat(),
                'category_name': '',
                'groups': [self.group.pk],
                'description': '',
                'new_video_urls': ['https://example.com/video.mp4'],
            },
        )
        self.assertTrue(form.is_valid(), form.errors)
        lessons = form.save_for_groups(self.teacher)
        self.assertIsNone(lessons[0].category_id)

    def test_requires_at_least_one_material(self):
        form = TeacherLessonForm(
            self.teacher.pk,
            data={
                'name': 'Empty lesson',
                'lesson_date': date.today().isoformat(),
                'category_name': '',
                'groups': [self.group.pk],
                'description': '',
                'new_video_urls': [],
            },
        )
        self.assertFalse(form.is_valid())
        self.assertIn('pdf_files', form.errors)

    def test_video_link_only_lesson_is_valid(self):
        form = TeacherLessonForm(
            self.teacher.pk,
            data={
                'name': 'Video lesson',
                'lesson_date': date.today().isoformat(),
                'category_name': '',
                'groups': [self.group.pk],
                'description': '',
                'new_video_urls': ['https://www.youtube.com/watch?v=dQw4w9WgXcQ'],
            },
        )
        self.assertTrue(form.is_valid(), form.errors)
        lessons = form.save_for_groups(self.teacher)
        self.assertEqual(lessons[0].video_url, 'https://www.youtube.com/watch?v=dQw4w9WgXcQ')

    def test_student_sees_only_group_teacher_lessons(self):
        own_lesson = Lesson.objects.create(
            group=self.group,
            teacher=self.teacher,
            subject='ielts',
            name='From own teacher',
            lesson_date=date.today(),
        )
        foreign_lesson = Lesson.objects.create(
            group=self.group,
            teacher=self.other_teacher,
            subject='ielts',
            name='From other teacher',
            lesson_date=date.today(),
        )

        rows = get_student_lessons(self.student.pk)
        ids = {row['id'] for row in rows}
        self.assertIn(own_lesson.pk, ids)
        self.assertNotIn(foreign_lesson.pk, ids)

    def test_teacher_lists_own_group_lessons_without_specializations(self):
        Lesson.objects.create(
            group=self.group,
            teacher=self.teacher,
            subject='ielts',
            name='Listed lesson',
            lesson_date=date.today(),
        )
        rows = get_teacher_lessons(self.teacher.pk)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['name'], 'Listed lesson')


class TeacherLessonEditTests(TestCase):
    def setUp(self):
        _ensure_ielts_service()

        self.teacher_user = User.objects.create_user(username='edit_lesson_teacher', password='pass')
        self.teacher = TeacherProfile.objects.create(user=self.teacher_user)
        self.group = StudyGroup.objects.create(
            teacher=self.teacher,
            name='IELTS Edit',
            max_students=10,
        )
        link_study_group_services(self.group, 'ielts')
        self.lesson = Lesson.objects.create(
            group=self.group,
            teacher=self.teacher,
            subject='ielts',
            name='Editable lesson',
            lesson_date=date(2025, 3, 15),
            video_url='https://www.youtube.com/watch?v=test12345',
        )
        self.lesson.pdf_file.save(
            'notes.pdf',
            SimpleUploadedFile('notes.pdf', b'%PDF-1.4', content_type='application/pdf'),
            save=True,
        )
        LessonAttachment.objects.create(
            lesson=self.lesson,
            kind=LessonAttachment.Kind.PDF,
            file=SimpleUploadedFile('extra.pdf', b'%PDF-1.4', content_type='application/pdf'),
        )

    def test_edit_form_keeps_existing_lesson_date(self):
        form = TeacherLessonForm(self.teacher.pk, instance=self.lesson)
        self.assertEqual(form.initial.get('lesson_date'), date(2025, 3, 15))
        self.assertEqual(form['lesson_date'].value(), '2025-03-15')

    def test_edit_form_lists_existing_materials(self):
        form = TeacherLessonForm(self.teacher.pk, instance=self.lesson)
        self.assertEqual(len(form.existing_pdfs), 2)
        material_ids = {row['id'] for row in form.existing_materials}
        self.assertIn('legacy-pdf', material_ids)
        self.assertTrue(any(item.startswith('attachment-') for item in material_ids))
        self.assertEqual(len(build_lesson_edit_materials(self.lesson)), 2)

    def test_edit_can_remove_existing_pdf_and_update_date(self):
        form = TeacherLessonForm(
            self.teacher.pk,
            data={
                'group': self.group.pk,
                'name': 'Editable lesson',
                'lesson_date': '2025-04-01',
                'category_name': '',
                'description': '',
                'new_video_urls': [],
                'remove_attachments': ['legacy-pdf'],
            },
            instance=self.lesson,
        )
        self.assertTrue(form.is_valid(), form.errors)
        lesson = form.save()
        lesson.refresh_from_db()
        self.assertEqual(lesson.lesson_date, date(2025, 4, 1))
        self.assertFalse(lesson.pdf_file)

    def test_create_lesson_with_multiple_video_links(self):
        form = TeacherLessonForm(
            self.teacher.pk,
            data={
                'name': 'Multi video lesson',
                'lesson_date': date.today().isoformat(),
                'category_name': '',
                'groups': [self.group.pk],
                'description': '',
                'new_video_urls': [
                    'https://www.youtube.com/watch?v=videoone12',
                    'https://www.youtube.com/watch?v=videotwo12',
                ],
            },
        )
        self.assertTrue(form.is_valid(), form.errors)
        lessons = form.save_for_groups(self.teacher)
        lesson = lessons[0]
        lesson.refresh_from_db()
        self.assertEqual(lesson.video_url, 'https://www.youtube.com/watch?v=videoone12')
        self.assertEqual(
            lesson.attachments.filter(kind=LessonAttachment.Kind.VIDEO).count(),
            2,
        )

    def test_edit_form_lists_existing_video_links(self):
        form = TeacherLessonForm(self.teacher.pk, instance=self.lesson)
        self.assertEqual(len(form.existing_videos), 1)
        self.assertEqual(form.existing_videos[0]['id'], 'legacy-video')

    def test_edit_can_remove_video_link(self):
        form = TeacherLessonForm(
            self.teacher.pk,
            data={
                'group': self.group.pk,
                'name': 'Editable lesson',
                'lesson_date': '2025-03-15',
                'category_name': '',
                'description': '',
                'new_video_urls': [''],
                'remove_attachments': ['legacy-video'],
            },
            instance=self.lesson,
        )
        self.assertTrue(form.is_valid(), form.errors)
        lesson = form.save()
        lesson.refresh_from_db()
        self.assertEqual(lesson.video_url, '')
        self.assertTrue(lesson.pdf_file)

    def test_edit_form_keeps_existing_videos_separate_from_new_inputs(self):
        form = TeacherLessonForm(self.teacher.pk, instance=self.lesson)
        self.assertEqual(len(form.existing_videos), 1)
        self.assertEqual(form.existing_videos[0]['id'], 'legacy-video')
        self.assertEqual(len(form.new_video_url_rows), 1)
        self.assertEqual(form.new_video_url_rows[0]['url'], '')

    def test_edit_can_add_second_video_link(self):
        form = TeacherLessonForm(
            self.teacher.pk,
            data={
                'group': self.group.pk,
                'name': 'Editable lesson',
                'lesson_date': '2025-03-15',
                'category_name': '',
                'description': '',
                'new_video_urls': [
                    'https://www.youtube.com/watch?v=second1234',
                ],
            },
            instance=self.lesson,
        )
        self.assertTrue(form.is_valid(), form.errors)
        lesson = form.save()
        lesson.refresh_from_db()
        self.assertEqual(lesson.video_url, 'https://www.youtube.com/watch?v=test12345')
        self.assertEqual(
            lesson.attachments.filter(kind=LessonAttachment.Kind.VIDEO).count(),
            2,
        )

    def test_edit_can_remove_attachment_pdf(self):
        attachment = self.lesson.attachments.filter(kind=LessonAttachment.Kind.PDF).first()
        attachment_id = f'attachment-{attachment.pk}'
        form = TeacherLessonForm(
            self.teacher.pk,
            data={
                'group': self.group.pk,
                'name': 'Editable lesson',
                'lesson_date': '2025-03-15',
                'category_name': '',
                'description': '',
                'new_video_urls': ['https://www.youtube.com/watch?v=test12345'],
                'remove_attachments': [attachment_id],
            },
            instance=self.lesson,
        )
        self.assertTrue(form.is_valid(), form.errors)
        lesson = form.save()
        lesson.refresh_from_db()
        self.assertFalse(
            lesson.attachments.filter(kind=LessonAttachment.Kind.PDF).exists(),
        )
        media = build_lesson_edit_materials(lesson)
        pdf_rows = [row for row in media if row['kind'] == LessonAttachment.Kind.PDF]
        self.assertEqual(len(pdf_rows), 1)
        self.assertEqual(pdf_rows[0]['id'], 'legacy-pdf')

    def test_edit_duplicate_pdf_name_is_listed_once(self):
        duplicate = LessonAttachment.objects.create(
            lesson=self.lesson,
            kind=LessonAttachment.Kind.PDF,
            file=SimpleUploadedFile('notes.pdf', b'%PDF-duplicate', content_type='application/pdf'),
        )
        self.assertTrue(duplicate.pk)
        materials = build_lesson_edit_materials(self.lesson)
        pdf_rows = [row for row in materials if row['kind'] == LessonAttachment.Kind.PDF]
        self.assertEqual(len(pdf_rows), 2)
        labels = {row['label'] for row in pdf_rows}
        self.assertEqual(labels, {'notes.pdf', 'extra.pdf'})

    def test_edit_cannot_remove_every_material_without_replacement(self):
        attachment_id = f'attachment-{self.lesson.attachments.first().pk}'
        form = TeacherLessonForm(
            self.teacher.pk,
            data={
                'group': self.group.pk,
                'name': 'Editable lesson',
                'lesson_date': '2025-03-15',
                'category_name': '',
                'description': '',
                'new_video_urls': [],
                'remove_attachments': ['legacy-pdf', attachment_id, 'legacy-video'],
            },
            instance=self.lesson,
        )
        self.assertFalse(form.is_valid())
        self.assertIn('pdf_files', form.errors)
