from django.contrib.auth import get_user_model
from django.test import TestCase

from portals.models import (
    Quiz,
    QuizCategory,
    QuizResult,
    StudentCourseSpecialization,
    StudentProfile,
    StudyGroup,
    TeacherCourseSpecialization,
    TeacherProfile,
)
from portals.utils.queries import (
    get_student_quiz_results,
    get_student_quizzes,
    get_teacher_quizzes,
    get_teacher_scores,
)
from portals.utils.student_courses import (
    quiz_visible_to_student,
    quiz_visible_to_teacher,
    teacher_can_see_quiz_result,
)
from projects.models.service_models import Service

User = get_user_model()


def _ensure_active_portal_services():
    """TeacherCourseSpecialization and QuizCategory require mapped active site services."""
    Service.objects.get_or_create(
        slug='ielts',
        defaults={
            'name_az': 'IELTS',
            'name_en': 'IELTS',
            'is_active': True,
        },
    )
    Service.objects.get_or_create(
        slug='only-speaking',
        defaults={
            'name_az': 'Speaking',
            'name_en': 'Speaking',
            'is_active': True,
        },
    )


class QuizVisibilityTests(TestCase):
    def setUp(self):
        _ensure_active_portal_services()

        self.teacher_user = User.objects.create_user(username='teacher1', password='pass')
        self.student_user = User.objects.create_user(username='student1', password='pass')
        self.other_teacher_user = User.objects.create_user(username='teacher2', password='pass')
        self.other_student_user = User.objects.create_user(username='student2', password='pass')

        self.teacher = TeacherProfile.objects.create(user=self.teacher_user)
        self.other_teacher = TeacherProfile.objects.create(user=self.other_teacher_user)
        self.student = StudentProfile.objects.create(user=self.student_user)
        self.other_student = StudentProfile.objects.create(user=self.other_student_user)

        TeacherCourseSpecialization.objects.create(teacher=self.teacher, course_type='ielts')
        TeacherCourseSpecialization.objects.create(teacher=self.other_teacher, course_type='speaking')

        self.ielts_group = StudyGroup.objects.create(
            teacher=self.teacher,
            name='IELTS A',
            max_students=10,
        )
        self.speaking_group = StudyGroup.objects.create(
            teacher=self.other_teacher,
            name='Speaking B',
            max_students=10,
        )
        from portals.tests.group_helpers import link_study_group_services

        link_study_group_services(self.ielts_group, 'ielts')
        link_study_group_services(self.speaking_group, 'speaking')
        self.ielts_group.students.add(self.student)

        StudentCourseSpecialization.objects.create(
            student=self.student,
            course_type='ielts',
            is_active=True,
        )

        self.ielts_category = QuizCategory.objects.create(service='ielts', name='Reading')
        self.speaking_category = QuizCategory.objects.create(service='speaking', name='Fluency')

        self.ielts_quiz = Quiz.objects.create(
            category=self.ielts_category,
            topic='IELTS Quiz 1',
        )
        self.speaking_quiz = Quiz.objects.create(
            category=self.speaking_category,
            topic='Speaking Quiz 1',
        )

    def test_student_sees_quiz_for_matching_service_enrollment(self):
        self.assertTrue(quiz_visible_to_student(self.ielts_quiz, self.student.pk))
        self.assertIn(self.ielts_quiz.pk, [q['id'] for q in get_student_quizzes(self.student.pk)])

    def test_student_does_not_see_unmatched_service_quiz(self):
        self.assertFalse(quiz_visible_to_student(self.speaking_quiz, self.student.pk))
        quiz_ids = [q['id'] for q in get_student_quizzes(self.student.pk)]
        self.assertNotIn(self.speaking_quiz.pk, quiz_ids)

    def test_student_sees_quizzes_for_all_active_services(self):
        StudentCourseSpecialization.objects.create(
            student=self.student,
            course_type='speaking',
            is_active=True,
        )
        quiz_ids = [q['id'] for q in get_student_quizzes(self.student.pk)]
        self.assertIn(self.ielts_quiz.pk, quiz_ids)
        self.assertIn(self.speaking_quiz.pk, quiz_ids)

    def test_inactive_service_enrollment_hides_quizzes(self):
        StudentCourseSpecialization.objects.filter(
            student=self.student,
            course_type='ielts',
        ).update(is_active=False)
        self.assertFalse(quiz_visible_to_student(self.ielts_quiz, self.student.pk))
        quiz_ids = [q['id'] for q in get_student_quizzes(self.student.pk)]
        self.assertNotIn(self.ielts_quiz.pk, quiz_ids)

    def test_teacher_sees_quiz_for_assigned_service(self):
        self.assertTrue(quiz_visible_to_teacher(self.ielts_quiz, self.teacher.pk))
        quiz_ids = [q['id'] for q in get_teacher_quizzes(self.teacher.pk)]
        self.assertIn(self.ielts_quiz.pk, quiz_ids)

    def test_teacher_sees_other_teachers_quiz_in_same_service(self):
        admin_quiz = Quiz.objects.create(
            category=self.ielts_category,
            topic='IELTS Quiz — admin assigned',
        )
        self.assertTrue(quiz_visible_to_teacher(admin_quiz, self.teacher.pk))
        quiz_ids = [q['id'] for q in get_teacher_quizzes(self.teacher.pk)]
        self.assertIn(admin_quiz.pk, quiz_ids)

    def test_teacher_does_not_see_other_service_quiz(self):
        self.assertFalse(quiz_visible_to_teacher(self.speaking_quiz, self.teacher.pk))

    def test_teacher_sees_result_only_for_own_student_and_service(self):
        QuizResult.objects.create(
            student=self.student,
            quiz=self.ielts_quiz,
            given_answers={},
            total_score=8,
            duration_sec=120,
        )
        QuizResult.objects.create(
            student=self.other_student,
            quiz=self.ielts_quiz,
            given_answers={},
            total_score=5,
            duration_sec=90,
        )

        scores = get_teacher_scores(self.teacher.pk)
        student_ids = {row['student_id'] for row in scores}
        self.assertIn(self.student.pk, student_ids)
        self.assertNotIn(self.other_student.pk, student_ids)

    def test_student_results_filtered_by_current_service(self):
        QuizResult.objects.create(
            student=self.student,
            quiz=self.speaking_quiz,
            given_answers={},
            total_score=6,
            duration_sec=60,
        )
        results = get_student_quiz_results(self.student.pk)
        quiz_ids = {row['quiz_id'] for row in results}
        self.assertNotIn(self.speaking_quiz.pk, quiz_ids)

    def test_teacher_result_requires_shared_group(self):
        self.assertFalse(
            teacher_can_see_quiz_result(
                self.teacher.pk,
                self.other_student.pk,
                self.ielts_quiz,
            ),
        )
