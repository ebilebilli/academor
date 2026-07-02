from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.test import TestCase
from django.utils import timezone

from portals.models import (
    Quiz,
    QuizCategory,
    QuizQuestion,
    QuizResult,
    StudentProfile,
    StudyGroup,
    TeacherCourseSpecialization,
    TeacherProfile,
)
from portals.utils.quiz_submit import score_variant_quiz, submit_variant_quiz_attempt
from projects.models.service_models import Service

User = get_user_model()


def _ensure_active_portal_services():
    Service.objects.get_or_create(
        slug='ielts',
        defaults={'name_az': 'IELTS', 'name_en': 'IELTS', 'is_active': True},
    )


class QuizSubmitTests(TestCase):
    def setUp(self):
        _ensure_active_portal_services()

        self.teacher_user = User.objects.create_user(username='quiz_submit_teacher', password='pass')
        self.student_user = User.objects.create_user(username='quiz_submit_student', password='pass')
        self.teacher = TeacherProfile.objects.create(user=self.teacher_user)
        self.student = StudentProfile.objects.create(user=self.student_user)
        TeacherCourseSpecialization.objects.create(teacher=self.teacher, course_type='ielts')

        group = StudyGroup.objects.create(
            teacher=self.teacher,
            name='IELTS',
            max_students=10,
        )
        from portals.tests.group_helpers import link_study_group_services

        link_study_group_services(group, 'ielts')
        group.students.add(self.student)

        category = QuizCategory.objects.create(service='ielts', name='Grammar')
        self.quiz = Quiz.objects.create(
            category=category,
            topic='Quick test',
            is_time_limited=True,
            time_limit_minutes=15,
        )
        self.q1 = QuizQuestion.objects.create(
            quiz=self.quiz,
            order=1,
            question='Q1',
            answer_options=['A', 'B'],
            correct_answer='A',
        )
        self.q2 = QuizQuestion.objects.create(
            quiz=self.quiz,
            order=2,
            question='Q2',
            answer_options=['X', 'Y'],
            correct_answer='Y',
        )

    def test_score_variant_quiz(self):
        score, max_score, breakdown = score_variant_quiz(
            self.quiz,
            {str(self.q1.pk): 0, str(self.q2.pk): 1},
        )
        self.assertEqual(score, 2)
        self.assertEqual(max_score, 2)
        self.assertTrue(all(item['is_correct'] for item in breakdown))

    def test_submit_creates_result(self):
        started_at = timezone.now() - timedelta(seconds=90)
        payload = submit_variant_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=self.quiz.pk,
            given_answers={str(self.q1.pk): 0, str(self.q2.pk): 0},
            duration_sec=90,
            session_started_at=started_at.isoformat(),
        )
        self.assertTrue(payload['success'])
        self.assertEqual(payload['total_score'], 1)
        self.assertEqual(payload['max_score'], 2)
        self.assertEqual(payload['percent'], 50.0)
        self.assertEqual(payload['duration_sec'], 90)
        self.assertEqual(len(payload['questions']), 2)
        self.assertEqual(QuizResult.objects.filter(student=self.student, quiz=self.quiz).count(), 1)

    def test_retake_updates_result(self):
        submit_variant_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=self.quiz.pk,
            given_answers={str(self.q1.pk): 0, str(self.q2.pk): 0},
            duration_sec=60,
            session_started_at=timezone.now().isoformat(),
        )
        retry = submit_variant_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=self.quiz.pk,
            given_answers={str(self.q1.pk): 0, str(self.q2.pk): 1},
            duration_sec=30,
            session_started_at=timezone.now().isoformat(),
        )
        self.assertTrue(retry['success'])
        self.assertEqual(retry['total_score'], 2)
        self.assertEqual(retry['percent'], 100.0)
        self.assertEqual(QuizResult.objects.filter(student=self.student, quiz=self.quiz).count(), 1)
        result = QuizResult.objects.get(student=self.student, quiz=self.quiz)
        self.assertEqual(result.total_score, 2)

    def test_time_limit_requires_minutes(self):
        quiz = Quiz(
            category=self.quiz.category,
            topic='Bad timer',
            is_time_limited=True,
        )
        with self.assertRaises(ValidationError):
            quiz.full_clean()
