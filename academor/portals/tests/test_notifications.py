from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from portals.middleware import PortalSessionMiddleware
from portals.models import (
    ParentProfile,
    PortalNotification,
    Quiz,
    QuizCategory,
    QuizQuestion,
    QuizResult,
    QuizResultReview,
    StudentProfile,
    StudyGroup,
    TeacherCourseSpecialization,
    TeacherProfile,
)
from portals.tests.portal_helpers import assign_quiz_to_student
from portals.utils.notifications import (
    delete_notification,
    get_notifications,
    get_unread_notification_count,
    mark_notification_read,
)
from portals.utils.portal_session import PORTAL_COOKIE_NAME, portal_login
from portals.utils.quiz_submit import (
    submit_manual_quiz_attempt,
    submit_teacher_quiz_review,
    submit_variant_quiz_attempt,
)
from projects.models.service_models import Service

User = get_user_model()


def _portal_client_login(client: Client, user) -> None:
    factory = RequestFactory()
    request = factory.get('/portal/')
    request.COOKIES = {}
    portal_login(request, user)
    middleware = PortalSessionMiddleware(lambda r: HttpResponse())
    response = middleware(request)
    client.cookies[PORTAL_COOKIE_NAME] = response.cookies[PORTAL_COOKIE_NAME].value


def _ensure_active_portal_services():
    Service.objects.get_or_create(
        slug='ielts',
        defaults={'name_az': 'IELTS', 'name_en': 'IELTS', 'is_active': True},
    )


class PortalNotificationTests(TestCase):
    def setUp(self):
        _ensure_active_portal_services()

        self.teacher_user = User.objects.create_user(username='notify_teacher', password='pass')
        self.student_user = User.objects.create_user(username='notify_student', password='pass')
        self.parent_user = User.objects.create_user(username='notify_parent', password='pass')

        self.teacher = TeacherProfile.objects.create(user=self.teacher_user)
        self.student = StudentProfile.objects.create(user=self.student_user)
        self.parent = ParentProfile.objects.create(user=self.parent_user)
        self.parent.students.add(self.student)

        TeacherCourseSpecialization.objects.create(teacher=self.teacher, course_type='ielts')
        self.group = StudyGroup.objects.create(
            teacher=self.teacher,
            name='IELTS',
            max_students=10,
        )
        from portals.tests.group_helpers import create_quiz_category, link_study_group_services

        link_study_group_services(self.group, 'ielts')
        self.group.students.add(self.student)

        category = create_quiz_category('Grammar', 'ielts')
        self.quiz = Quiz.objects.create(
            category=category,
            topic='Notify test',
        )
        self.q1 = QuizQuestion.objects.create(
            quiz=self.quiz,
            order=1,
            question='Q1',
            answer_options=['A', 'B'],
            correct_answer='A',
        )
        assign_quiz_to_student(self.student, self.quiz)

    def test_variant_quiz_auto_publishes_and_notifies_teacher_and_parent_only(self):
        payload = submit_variant_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=self.quiz.pk,
            given_answers={str(self.q1.pk): 0},
            duration_sec=30,
            session_started_at=timezone.now().isoformat(),
        )
        self.assertTrue(payload['success'])
        self.assertEqual(
            PortalNotification.objects.filter(
                teacher=self.teacher,
                kind=PortalNotification.Kind.RESULT_PUBLISHED,
                is_read=False,
            ).count(),
            1,
        )
        self.assertEqual(
            PortalNotification.objects.filter(
                parent=self.parent,
                kind=PortalNotification.Kind.RESULT_PUBLISHED,
                is_read=False,
            ).count(),
            1,
        )
        self.assertEqual(
            PortalNotification.objects.filter(
                student=self.student,
                kind=PortalNotification.Kind.RESULT_PUBLISHED,
            ).count(),
            0,
        )

    def test_variant_quiz_notifies_teacher_when_category_has_multiple_services(self):
        from projects.models.service_models import Service

        Service.objects.get_or_create(
            slug='speaking',
            defaults={'name_az': 'Speaking', 'name_en': 'Speaking', 'is_active': True},
        )
        from portals.tests.group_helpers import link_quiz_category_services

        link_quiz_category_services(self.quiz.category, 'ielts', 'speaking')
        payload = submit_variant_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=self.quiz.pk,
            given_answers={str(self.q1.pk): 0},
            duration_sec=30,
            session_started_at=timezone.now().isoformat(),
        )
        self.assertTrue(payload['success'])
        self.assertEqual(
            PortalNotification.objects.filter(
                teacher=self.teacher,
                kind=PortalNotification.Kind.RESULT_PUBLISHED,
                is_read=False,
            ).count(),
            1,
        )
        from portals.utils.notifications import get_teacher_portal_bell_count

        self.assertEqual(get_teacher_portal_bell_count(self.teacher.pk), 1)

    def test_manual_submit_notifies_teacher_to_review(self):
        self.quiz.is_essay = True
        self.quiz.save(update_fields=['is_essay'])
        question_two = QuizQuestion.objects.create(
            quiz=self.quiz,
            order=2,
            question='Write an essay',
        )
        payload = submit_manual_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=self.quiz.pk,
            given_answers={
                str(self.q1.pk): 'Answer for task one.',
                str(question_two.pk): 'My essay text',
            },
            duration_sec=60,
        )
        self.assertTrue(payload['success'])
        from portals.utils.notifications import (
            get_teacher_pending_review_count,
            get_teacher_portal_bell_count,
        )

        self.assertEqual(get_teacher_pending_review_count(self.teacher.pk), 1)
        self.assertEqual(
            PortalNotification.objects.filter(
                teacher=self.teacher,
                kind=PortalNotification.Kind.SUBMISSION_PENDING,
            ).count(),
            0,
        )
        self.assertEqual(get_teacher_portal_bell_count(self.teacher.pk), 0)
        self.assertEqual(PortalNotification.objects.filter(parent=self.parent).count(), 0)
        self.assertEqual(
            PortalNotification.objects.filter(
                student=self.student,
                kind=PortalNotification.Kind.SUBMISSION_PENDING,
            ).count(),
            1,
        )
        items = get_notifications(student_id=self.student.pk)
        self.assertEqual(len(items), 1)
        self.assertTrue(items[0]['is_submission_pending'])
        self.assertFalse(items[0]['is_read'])

    def test_manual_review_publishes_to_student_and_parent(self):
        self.quiz.is_essay = True
        self.quiz.save(update_fields=['is_essay'])
        result = QuizResult.objects.create(
            student=self.student,
            quiz=self.quiz,
            student_submission='Essay answer',
            total_score=None,
        )

        outcome = submit_teacher_quiz_review(
            teacher_id=self.teacher.pk,
            result_id=result.pk,
            total_score=8,
            teacher_feedback='Well done',
        )
        self.assertTrue(outcome['success'])
        self.assertEqual(QuizResultReview.objects.filter(result=result).count(), 1)
        self.assertEqual(
            PortalNotification.objects.filter(
                parent=self.parent,
                kind=PortalNotification.Kind.RESULT_PUBLISHED,
            ).count(),
            1,
        )
        self.assertEqual(
            PortalNotification.objects.filter(
                student=self.student,
                kind=PortalNotification.Kind.RESULT_PUBLISHED,
            ).count(),
            1,
        )
        self.assertFalse(
            PortalNotification.objects.filter(
                teacher=self.teacher,
                kind=PortalNotification.Kind.RESULT_PUBLISHED,
            ).exists(),
        )
        self.assertEqual(get_unread_notification_count(student_id=self.student.pk), 1)
        self.assertEqual(get_unread_notification_count(parent_id=self.parent.pk), 1)

    def test_manual_review_removes_pending_submission_notification(self):
        self.quiz.is_essay = True
        self.quiz.save(update_fields=['is_essay'])
        question_two = QuizQuestion.objects.create(
            quiz=self.quiz,
            order=2,
            question='Write an essay',
        )
        payload = submit_manual_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=self.quiz.pk,
            given_answers={
                str(self.q1.pk): 'Answer for task one.',
                str(question_two.pk): 'My essay text',
            },
        )
        self.assertTrue(payload['success'])
        result = QuizResult.objects.filter(student=self.student, quiz=self.quiz).order_by('-completed_at', '-id').first()
        pending = PortalNotification.objects.get(
            student=self.student,
            quiz_result=result,
            kind=PortalNotification.Kind.SUBMISSION_PENDING,
        )
        self.assertFalse(pending.is_read)

        outcome = submit_teacher_quiz_review(
            teacher_id=self.teacher.pk,
            result_id=result.pk,
            total_score=8,
            teacher_feedback='Well done',
        )
        self.assertTrue(outcome['success'])
        self.assertFalse(
            PortalNotification.objects.filter(
                student=self.student,
                kind=PortalNotification.Kind.SUBMISSION_PENDING,
            ).exists(),
        )
        published = PortalNotification.objects.get(student=self.student, quiz_result=result)
        self.assertEqual(published.kind, PortalNotification.Kind.RESULT_PUBLISHED)
        self.assertFalse(published.is_read)
        self.assertEqual(PortalNotification.objects.filter(student=self.student).count(), 1)
        self.assertEqual(get_unread_notification_count(student_id=self.student.pk), 1)

    def test_manual_re_review_marks_student_notification_unread_again(self):
        from portals.utils.quiz_submit import submit_manual_quiz_attempt

        self.quiz.is_essay = True
        self.quiz.save(update_fields=['is_essay'])
        question_two = QuizQuestion.objects.create(
            quiz=self.quiz,
            order=2,
            question='Write an essay',
        )
        submit_manual_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=self.quiz.pk,
            given_answers={
                str(self.q1.pk): 'Answer for task one.',
                str(question_two.pk): 'First essay.',
            },
        )
        result = QuizResult.objects.filter(student=self.student, quiz=self.quiz).order_by('-completed_at', '-id').first()

        submit_teacher_quiz_review(
            teacher_id=self.teacher.pk,
            result_id=result.pk,
            total_score=7,
            teacher_feedback='Good first try.',
        )
        note = PortalNotification.objects.get(student=self.student, quiz_result=result)
        mark_notification_read(notification_id=note.pk, student_id=self.student.pk)
        self.assertEqual(get_unread_notification_count(student_id=self.student.pk), 0)

        submit_manual_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=self.quiz.pk,
            given_answers={
                str(self.q1.pk): 'Answer for task one.',
                str(question_two.pk): 'Retake essay.',
            },
        )
        latest_result = QuizResult.objects.filter(student=self.student, quiz=self.quiz).order_by('-completed_at', '-id').first()
        submit_teacher_quiz_review(
            teacher_id=self.teacher.pk,
            result_id=latest_result.pk,
            total_score=9,
            teacher_feedback='Much better.',
        )
        new_note = PortalNotification.objects.get(student=self.student, quiz_result=latest_result)
        self.assertFalse(new_note.is_read)
        self.assertEqual(get_unread_notification_count(student_id=self.student.pk), 1)

    def test_mark_read_and_delete(self):
        result = QuizResult.objects.create(
            student=self.student,
            quiz=self.quiz,
            given_answers={str(self.q1.pk): 0},
            total_score=1,
        )
        note = PortalNotification.objects.create(
            teacher=self.teacher,
            quiz_result=result,
            is_read=False,
        )
        self.assertTrue(
            mark_notification_read(notification_id=note.pk, teacher_id=self.teacher.pk),
        )
        note.refresh_from_db()
        self.assertTrue(note.is_read)
        self.assertEqual(get_unread_notification_count(teacher_id=self.teacher.pk), 0)
        self.assertTrue(
            delete_notification(notification_id=note.pk, teacher_id=self.teacher.pk),
        )
        self.assertFalse(PortalNotification.objects.filter(pk=note.pk).exists())

    def test_teacher_mark_all_read_clears_all_bell_kinds(self):
        from portals.models import IeltsMockTestAttempt
        from portals.utils.notifications import (
            get_teacher_portal_bell_count,
            mark_all_notifications_read,
        )

        result = QuizResult.objects.create(
            student=self.student,
            quiz=self.quiz,
            given_answers={str(self.q1.pk): 0},
            total_score=1,
        )
        attempt = IeltsMockTestAttempt.objects.create(
            student=self.student,
            exam_program='ielts',
            status=IeltsMockTestAttempt.Status.COMPLETED,
            reading_quiz=self.quiz,
        )
        PortalNotification.objects.create(
            teacher=self.teacher,
            quiz_result=result,
            kind=PortalNotification.Kind.RESULT_PUBLISHED,
            is_read=False,
        )
        PortalNotification.objects.create(
            teacher=self.teacher,
            ielts_mock_test=attempt,
            kind=PortalNotification.Kind.MOCK_TEST_COMPLETED,
            is_read=False,
        )
        self.assertEqual(get_teacher_portal_bell_count(self.teacher.pk), 2)
        mark_all_notifications_read(teacher_id=self.teacher.pk)
        self.assertEqual(get_teacher_portal_bell_count(self.teacher.pk), 0)

    def test_score_detail_marks_notification_read(self):
        result = QuizResult.objects.create(
            student=self.student,
            quiz=self.quiz,
            given_answers={str(self.q1.pk): 0},
            total_score=1,
        )
        PortalNotification.objects.create(
            parent=self.parent,
            quiz_result=result,
            is_read=False,
        )
        client = Client()
        _portal_client_login(client, self.parent_user)
        url = reverse('portals:parent-score-detail', kwargs={'result_pk': result.pk})
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            PortalNotification.objects.filter(parent=self.parent, is_read=False).exists(),
        )

    def test_portal_badges_endpoint_returns_teacher_counts(self):
        result = QuizResult.objects.create(
            student=self.student,
            quiz=self.quiz,
            given_answers={str(self.q1.pk): 0},
            total_score=1,
        )
        PortalNotification.objects.create(
            teacher=self.teacher,
            quiz_result=result,
            kind=PortalNotification.Kind.RESULT_PUBLISHED,
            is_read=False,
        )
        client = Client()
        _portal_client_login(client, self.teacher_user)
        response = client.get(
            reverse('portals:portal-badges'),
            HTTP_ACCEPT='application/json',
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['unread'], 1)
        self.assertIn('pending_reviews', payload)
