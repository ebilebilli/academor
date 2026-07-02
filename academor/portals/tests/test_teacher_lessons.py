from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase

from portals.models import Lesson, StudentProfile, StudyGroup, TeacherProfile
from portals.teacher_forms import TeacherLessonForm
from portals.utils.group_services import resolve_group_lesson_service
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
                'video_url': '',
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
                'video_url': '',
            },
        )
        self.assertTrue(form.is_valid(), form.errors)
        lessons = form.save_for_groups(self.teacher)
        self.assertIsNone(lessons[0].category_id)

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
