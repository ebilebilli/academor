from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse
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
from portals.tests.portal_helpers import (
    assign_quiz_to_student,
    ensure_active_portal_services,
    portal_client_login,
)
from portals.utils.quiz_submit import score_variant_quiz, submit_variant_quiz_attempt

User = get_user_model()


def _portal_client_login(client: Client, user) -> None:
    portal_client_login(client, user)


def _ensure_active_portal_services():
    ensure_active_portal_services('ielts')


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
        from portals.tests.group_helpers import create_quiz_category, link_study_group_services

        link_study_group_services(group, 'ielts')
        group.students.add(self.student)

        category = create_quiz_category('Grammar', 'ielts')
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
        assign_quiz_to_student(self.student, self.quiz)

    def test_score_variant_quiz(self):
        score, max_score, breakdown = score_variant_quiz(
            self.quiz,
            {str(self.q1.pk): 0, str(self.q2.pk): 1},
        )
        self.assertEqual(score, 2)
        self.assertEqual(max_score, 2)
        self.assertTrue(all(item['is_correct'] for item in breakdown))

    def test_submit_variant_quiz_with_spr_questions(self):
        spr_question = QuizQuestion.objects.create(
            quiz=self.quiz,
            order=3,
            question='Enter 3.5',
            question_type=QuizQuestion.QuestionType.SPR,
            answer_options=[],
            correct_answer='',
            spr_correct_answers=['7/2', '3.5'],
            spr_max_length=5,
        )
        started_at = timezone.now() - timedelta(seconds=45)
        payload = submit_variant_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=self.quiz.pk,
            given_answers={
                str(self.q1.pk): 0,
                str(self.q2.pk): 1,
                str(spr_question.pk): '3.5',
            },
            duration_sec=45,
            session_started_at=started_at.isoformat(),
        )
        self.assertTrue(payload['success'])
        self.assertEqual(payload['total_score'], 3)
        self.assertEqual(payload['max_score'], 3)
        result = QuizResult.objects.filter(student=self.student, quiz=self.quiz).order_by('-completed_at', '-id').first()
        self.assertEqual(result.given_answers[str(spr_question.pk)], '3.5')

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
        self.assertEqual(QuizResult.objects.filter(student=self.student, quiz=self.quiz).count(), 2)
        result = QuizResult.objects.filter(student=self.student, quiz=self.quiz).order_by('-completed_at', '-id').first()
        self.assertEqual(result.total_score, 2)

    def test_student_can_open_variant_quiz_after_attempt(self):
        submit_variant_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=self.quiz.pk,
            given_answers={str(self.q1.pk): 0, str(self.q2.pk): 0},
            duration_sec=60,
            session_started_at=timezone.now().isoformat(),
        )

        client = Client()
        _portal_client_login(client, self.student_user)
        url = reverse('portals:student-quiz-take', kwargs={'pk': self.quiz.pk})
        response = client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.quiz.topic)

    def test_submit_stores_completion_trigger(self):
        started_at = timezone.now() - timedelta(minutes=15)
        payload = submit_variant_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=self.quiz.pk,
            given_answers={str(self.q1.pk): 0, str(self.q2.pk): 1},
            duration_sec=900,
            session_started_at=started_at.isoformat(),
            completion_trigger='time_limit',
        )
        self.assertTrue(payload['success'])
        self.assertEqual(payload['completion_trigger'], 'time_limit')
        result = QuizResult.objects.filter(student=self.student, quiz=self.quiz).order_by('-completed_at', '-id').first()
        self.assertEqual(result.completion_trigger, 'time_limit')
        self.assertEqual(result.duration_sec, 900)

    def test_time_limit_requires_minutes(self):
        quiz = Quiz(
            category=self.quiz.category,
            topic='Bad timer',
            is_time_limited=True,
        )
        with self.assertRaises(ValidationError):
            quiz.full_clean()
