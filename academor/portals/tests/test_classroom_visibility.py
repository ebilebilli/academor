from django.contrib.auth import get_user_model
from django.test import TestCase

from portals.models import Classroom, StudentProfile, StudyGroup, TeacherProfile
from portals.utils.queries import get_classroom_detail, get_student_classrooms, get_teacher_classrooms
from portals.utils.student_courses import classroom_visible_to_student, classroom_visible_to_teacher


User = get_user_model()


class ClassroomVisibilityTests(TestCase):
    def setUp(self):
        self.teacher_user = User.objects.create_user(username='t_class', password='pass')
        self.student_user = User.objects.create_user(username='s_class', password='pass')
        self.other_teacher_user = User.objects.create_user(username='t2_class', password='pass')

        self.teacher = TeacherProfile.objects.create(user=self.teacher_user)
        self.other_teacher = TeacherProfile.objects.create(user=self.other_teacher_user)
        self.student = StudentProfile.objects.create(user=self.student_user)

        self.group = StudyGroup.objects.create(
            teacher=self.teacher,
            name='IELTS group',
            max_students=10,
        )
        self.group.students.add(self.student)

        self.other_group = StudyGroup.objects.create(
            teacher=self.other_teacher,
            name='Speaking group',
            max_students=10,
        )

        self.group_textbook = Classroom.objects.create(
            name='IELTS textbook',
            group=self.group,
            teacher=self.teacher,
        )

        self.other_textbook = Classroom.objects.create(
            name='Speaking textbook',
            group=self.other_group,
            teacher=self.other_teacher,
        )

    def test_student_sees_group_textbook(self):
        self.assertTrue(classroom_visible_to_student(self.group_textbook, self.student.pk))
        rows = get_student_classrooms(self.student.pk)
        ids = [row['id'] for row in rows]
        self.assertIn(self.group_textbook.pk, ids)

    def test_student_does_not_see_other_group_textbook(self):
        self.assertFalse(classroom_visible_to_student(self.other_textbook, self.student.pk))
        ids = [row['id'] for row in get_student_classrooms(self.student.pk)]
        self.assertNotIn(self.other_textbook.pk, ids)

    def test_teacher_sees_own_group_textbook(self):
        self.assertTrue(classroom_visible_to_teacher(self.group_textbook, self.teacher.pk))
        ids = [row['id'] for row in get_teacher_classrooms(self.teacher.pk)]
        self.assertIn(self.group_textbook.pk, ids)

    def test_teacher_does_not_see_other_group_textbook(self):
        self.assertFalse(classroom_visible_to_teacher(self.other_textbook, self.teacher.pk))

    def test_textbook_without_group_hidden(self):
        empty_textbook = Classroom.objects.create(name='No group')
        self.assertFalse(classroom_visible_to_student(empty_textbook, self.student.pk))

    def test_detail_returns_none_when_not_visible(self):
        data = get_classroom_detail(
            self.other_textbook.pk,
            role='student',
            profile_id=self.student.pk,
        )
        self.assertIsNone(data)
