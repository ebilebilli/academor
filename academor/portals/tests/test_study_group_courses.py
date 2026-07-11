from django.contrib.auth import get_user_model
from django.test import TestCase

from portals.models import StudyGroup, TeacherCourseSpecialization, TeacherProfile
from portals.tests.group_helpers import link_study_group_courses
from portals.tests.test_quiz_visibility import _ensure_active_portal_services
from portals.utils.group_services import lesson_effective_subject, resolve_group_lesson_service
from portals.utils.portal_services import portal_codes_for_service_ids, services_for_portal_codes
from portals.utils.teacher_courses import (
    teacher_has_all_course_codes,
    teachers_for_portal_course_codes,
)

User = get_user_model()


class StudyGroupCourseTeacherTests(TestCase):
    def setUp(self):
        _ensure_active_portal_services()
        from projects.models.service_models import Service

        Service.objects.get_or_create(
            slug='general-english',
            defaults={
                'name_az': 'General English',
                'name_en': 'General English',
                'is_active': True,
            },
        )
        self.ielts_teacher = TeacherProfile.objects.create(
            user=User.objects.create_user(username='ielts_group_teacher', password='pass'),
        )
        self.general_teacher = TeacherProfile.objects.create(
            user=User.objects.create_user(username='general_group_teacher', password='pass'),
        )
        self.both_teacher = TeacherProfile.objects.create(
            user=User.objects.create_user(username='both_group_teacher', password='pass'),
        )
        TeacherCourseSpecialization.objects.create(
            teacher=self.ielts_teacher,
            course_type='ielts',
        )
        TeacherCourseSpecialization.objects.create(
            teacher=self.general_teacher,
            course_type='general_english',
        )
        TeacherCourseSpecialization.objects.create(teacher=self.both_teacher, course_type='ielts')
        TeacherCourseSpecialization.objects.create(
            teacher=self.both_teacher,
            course_type='general_english',
        )

    def test_group_courses_are_not_synced_from_teacher(self):
        group = StudyGroup.objects.create(
            teacher=self.ielts_teacher,
            name='Course-owned group',
            max_students=10,
        )
        self.assertEqual(list(group.courses.all()), [])

        link_study_group_courses(group, 'general_english')
        group.refresh_from_db()
        codes = group.get_portal_course_codes()
        self.assertIn('general_english', codes)
        self.assertNotIn('ielts', codes)

    def test_teachers_for_portal_course_codes_filters_by_specialization(self):
        ielts_only = teachers_for_portal_course_codes(['ielts'])
        self.assertIn(self.ielts_teacher, list(ielts_only))
        self.assertIn(self.both_teacher, list(ielts_only))
        self.assertNotIn(self.general_teacher, list(ielts_only))

        both_required = teachers_for_portal_course_codes(['ielts', 'general_english'])
        self.assertEqual(list(both_required), [self.both_teacher])

    def test_teacher_has_all_course_codes(self):
        self.assertTrue(teacher_has_all_course_codes(self.both_teacher.pk, ['ielts', 'general_english']))
        self.assertFalse(teacher_has_all_course_codes(self.ielts_teacher.pk, ['ielts', 'general_english']))

    def test_portal_codes_for_service_ids(self):
        services = list(services_for_portal_codes(['ielts', 'general_english']))
        codes = portal_codes_for_service_ids([service.pk for service in services])
        self.assertIn('ielts', codes)
        self.assertIn('general_english', codes)

    def test_resolve_group_lesson_service_prefers_group_linked_sat(self):
        from projects.models.service_models import Service

        Service.objects.get_or_create(
            slug='sat',
            defaults={'name_az': 'SAT', 'name_en': 'SAT', 'is_active': True},
        )
        group = StudyGroup.objects.create(
            teacher=self.ielts_teacher,
            name='SAT online qrup',
            max_students=10,
        )
        link_study_group_courses(group, 'sat')
        group.refresh_from_db()
        self.assertEqual(resolve_group_lesson_service(group), 'sat')

    def test_lesson_effective_subject_uses_group_sat_when_stored_subject_mismatches(self):
        from projects.models.service_models import Service
        from portals.models import Lesson

        Service.objects.get_or_create(
            slug='sat',
            defaults={'name_az': 'SAT', 'name_en': 'SAT', 'is_active': True},
        )
        group = StudyGroup.objects.create(
            teacher=self.ielts_teacher,
            name='SAT online qrup',
            max_students=10,
        )
        link_study_group_courses(group, 'sat')
        lesson = Lesson.objects.create(
            group=group,
            teacher=self.ielts_teacher,
            subject='general-english',
            name='SAT unit 1',
        )
        self.assertEqual(lesson_effective_subject(lesson), 'sat')

    def test_build_lesson_subject_tabs_respects_group_service_codes(self):
        from portals.utils.queries import build_lesson_subject_tabs

        lessons = [
            {'subject': 'general_english', 'group_id': 1},
            {'subject': 'sat', 'group_id': 2},
        ]
        tabs = build_lesson_subject_tabs(lessons, allowed_codes=['sat'])
        codes = [tab['code'] for tab in tabs]
        self.assertEqual(codes, ['all', 'sat'])
        self.assertEqual(tabs[0]['count'], 1)
        self.assertEqual(tabs[1]['count'], 1)

    def test_group_portal_display_labels_use_linked_codes_not_all_service_names(self):
        group = StudyGroup.objects.create(
            teacher=self.ielts_teacher,
            name='Display labels group',
            max_students=10,
        )
        link_study_group_courses(group, 'ielts', 'general_english')
        group.refresh_from_db()
        labels = group.get_course_labels()
        self.assertEqual(len(labels), 2)
        codes = group.get_portal_course_codes()
        self.assertIn('ielts', codes)
        self.assertIn('general_english', codes)
        self.assertNotIn('sat', codes)
