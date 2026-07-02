from django.contrib.auth import get_user_model
from django.test import TestCase

from portals.models import Classroom, StudentCourseSpecialization, StudentProfile, StudyGroup, TeacherCourseSpecialization, TeacherProfile
from portals.utils.queries import get_classroom_detail, get_student_classrooms, get_teacher_classrooms
from portals.utils.student_courses import classroom_visible_to_student, classroom_visible_to_teacher
from projects.models.service_models import Service

User = get_user_model()


def _ensure_services():
    Service.objects.get_or_create(
        slug='ielts',
        defaults={'name_az': 'IELTS', 'name_en': 'IELTS', 'is_active': True},
    )
    Service.objects.get_or_create(
        slug='only-speaking',
        defaults={'name_az': 'Speaking', 'name_en': 'Speaking', 'is_active': True},
    )


class ClassroomVisibilityTests(TestCase):
    def setUp(self):
        _ensure_services()
        self.ielts_service = Service.objects.get(slug='ielts')
        self.speaking_service = Service.objects.get(slug='only-speaking')

        self.teacher_user = User.objects.create_user(username='t_class', password='pass')
        self.student_user = User.objects.create_user(username='s_class', password='pass')
        self.other_teacher_user = User.objects.create_user(username='t2_class', password='pass')

        self.teacher = TeacherProfile.objects.create(user=self.teacher_user)
        self.other_teacher = TeacherProfile.objects.create(user=self.other_teacher_user)
        self.student = StudentProfile.objects.create(user=self.student_user)

        TeacherCourseSpecialization.objects.create(teacher=self.teacher, course_type='ielts')
        TeacherCourseSpecialization.objects.create(teacher=self.other_teacher, course_type='speaking')

        self.group = StudyGroup.objects.create(
            teacher=self.teacher,
            name='IELTS group',
            max_students=10,
        )
        from portals.tests.group_helpers import link_study_group_services

        link_study_group_services(self.group, 'ielts')
        self.group.students.add(self.student)
        StudentCourseSpecialization.objects.create(
            student=self.student,
            course_type='ielts',
            is_active=True,
        )

        self.ielts_room = Classroom.objects.create(name='IELTS room')
        self.ielts_room.services.add(self.ielts_service)

        self.speaking_room = Classroom.objects.create(name='Speaking room')
        self.speaking_room.services.add(self.speaking_service)

    def test_student_sees_matching_service_classroom(self):
        self.assertTrue(classroom_visible_to_student(self.ielts_room, self.student.pk))
        rows = get_student_classrooms(self.student.pk)
        ids = [row['id'] for row in rows]
        self.assertIn(self.ielts_room.pk, ids)
        ielts_row = next(row for row in rows if row['id'] == self.ielts_room.pk)
        self.assertIn('ielts', ielts_row['services'])

    def test_student_does_not_see_other_service_classroom(self):
        self.assertFalse(classroom_visible_to_student(self.speaking_room, self.student.pk))
        ids = [row['id'] for row in get_student_classrooms(self.student.pk)]
        self.assertNotIn(self.speaking_room.pk, ids)

    def test_teacher_sees_matching_service_classroom(self):
        self.assertTrue(classroom_visible_to_teacher(self.ielts_room, self.teacher.pk))
        ids = [row['id'] for row in get_teacher_classrooms(self.teacher.pk)]
        self.assertIn(self.ielts_room.pk, ids)

    def test_teacher_does_not_see_other_service_classroom(self):
        self.assertFalse(classroom_visible_to_teacher(self.speaking_room, self.teacher.pk))

    def test_classroom_without_service_hidden(self):
        empty_room = Classroom.objects.create(name='No service')
        self.assertFalse(classroom_visible_to_student(empty_room, self.student.pk))

    def test_detail_returns_none_when_not_visible(self):
        data = get_classroom_detail(
            self.speaking_room.pk,
            role='student',
            profile_id=self.student.pk,
        )
        self.assertIsNone(data)
