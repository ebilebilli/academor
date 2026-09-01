from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from portals.admin.admin_v1 import study_group_teacher_queryset_for_admin
from portals.models import StudyGroup, TeacherCourseSpecialization, TeacherProfile
from portals.tests.group_helpers import link_study_group_courses
from portals.tests.test_quiz_visibility import _ensure_active_portal_services
from portals.utils.portal_services import services_for_portal_codes

User = get_user_model()


class StudyGroupAdminTeacherQuerysetTests(TestCase):
    def setUp(self):
        _ensure_active_portal_services()
        self.admin_user = User.objects.create_superuser(
            username='study_group_admin',
            password='pass',
            email='admin@example.com',
        )
        self.ielts_teacher = TeacherProfile.objects.create(
            user=User.objects.create_user(username='ielts_admin_teacher', password='pass'),
        )
        self.sat_teacher = TeacherProfile.objects.create(
            user=User.objects.create_user(username='sat_admin_teacher', password='pass'),
        )
        TeacherCourseSpecialization.objects.create(
            teacher=self.ielts_teacher,
            course_type='ielts',
        )
        TeacherCourseSpecialization.objects.create(
            teacher=self.sat_teacher,
            course_type='sat',
        )
        self.group = StudyGroup.objects.create(
            teacher=self.ielts_teacher,
            name='IELTS group',
            max_students=10,
        )
        link_study_group_courses(self.group, 'ielts')
        self.group.refresh_from_db()
        self.ielts_service = services_for_portal_codes(['ielts']).first()
        self.sat_service = services_for_portal_codes(['sat']).first()
        self.assertIsNotNone(self.ielts_service)
        self.assertIsNotNone(self.sat_service)

    def test_teacher_queryset_uses_posted_courses_not_stale_group_courses(self):
        class Request:
            method = 'POST'
            POST = {
                'courses': [str(self.sat_service.pk)],
                'teacher': str(self.sat_teacher.pk),
            }

        queryset = study_group_teacher_queryset_for_admin(
            Request(),
            obj_id=self.group.pk,
        )
        self.assertIn(self.sat_teacher, list(queryset))
        self.assertNotIn(self.ielts_teacher, list(queryset))

    def test_admin_can_change_group_courses_and_teacher_together(self):
        client = Client()
        client.force_login(self.admin_user)
        url = reverse('admin:portals_studygroup_change', args=[self.group.pk])
        response = client.post(
            url,
            {
                'name': self.group.name,
                'courses': [str(self.sat_service.pk)],
                'teacher': str(self.sat_teacher.pk),
                'is_active': 'on',
                'start_date': '',
                'max_students': '10',
                'students': [],
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            'Select a valid choice',
            status_code=200,
        )
        self.group.refresh_from_db()
        self.assertEqual(self.group.teacher_id, self.sat_teacher.pk)
        self.assertEqual(
            list(self.group.courses.values_list('pk', flat=True)),
            [self.sat_service.pk],
        )
