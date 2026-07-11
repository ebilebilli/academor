from django.contrib.auth import get_user_model
from django.test import TestCase

from portals.models import StudentCourseSpecialization, StudentProfile, StudyGroup, TeacherProfile
from portals.tests.group_helpers import link_study_group_services
from portals.tests.test_quiz_visibility import _ensure_active_portal_services
from portals.utils.ielts_mock_test import get_student_mock_exam_programs

User = get_user_model()


class StudyGroupEnrollmentSyncTests(TestCase):
    def setUp(self):
        _ensure_active_portal_services()
        self.teacher = TeacherProfile.objects.create(
            user=User.objects.create_user(username='group_sync_teacher', password='pass'),
        )
        self.student = StudentProfile.objects.create(
            user=User.objects.create_user(username='group_sync_student', password='pass'),
        )
        self.group = StudyGroup.objects.create(
            teacher=self.teacher,
            name='IELTS sync group',
            max_students=10,
        )
        link_study_group_services(self.group, 'ielts')

    def test_adding_student_to_group_creates_course_specialization(self):
        self.assertFalse(
            StudentCourseSpecialization.objects.filter(
                student=self.student,
                course_type='ielts',
            ).exists()
        )
        self.group.students.add(self.student)
        enrollment = StudentCourseSpecialization.objects.get(
            student=self.student,
            course_type='ielts',
        )
        self.assertTrue(enrollment.is_active)
        self.assertIn('ielts', get_student_mock_exam_programs(self.student.pk))

    def test_removing_student_from_group_keeps_enrollment(self):
        self.group.students.add(self.student)
        self.group.students.remove(self.student)
        self.assertTrue(
            StudentCourseSpecialization.objects.filter(
                student=self.student,
                course_type='ielts',
                is_active=True,
            ).exists()
        )

    def test_general_english_slug_maps_to_portal_course_type(self):
        from projects.models.service_models import Service

        Service.objects.get_or_create(
            slug='general-english',
            defaults={
                'name_az': 'General English',
                'name_en': 'General English',
                'is_active': True,
            },
        )
        link_study_group_services(self.group, 'general_english')
        self.group.students.add(self.student)
        self.assertTrue(
            StudentCourseSpecialization.objects.filter(
                student=self.student,
                course_type='general_english',
                is_active=True,
            ).exists()
        )
        self.assertFalse(
            StudentCourseSpecialization.objects.filter(
                student=self.student,
                course_type='general-english',
            ).exists()
        )
