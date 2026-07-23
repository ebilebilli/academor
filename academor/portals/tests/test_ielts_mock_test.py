import json

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.translation import gettext as _

from portals.models import (
    IeltsMockTestAttempt,
    ListeningAudio,
    ListeningQuestion,
    ParentProfile,
    PortalNotification,
    Quiz,
    QuizAssignment,
    QuizCategory,
    QuizQuestion,
    QuizResult,
    ReadingPassage,
    ReadingQuestion,
    ReadingQuestionType,
    SpeakingPart,
    SpeakingQuestion,
    StudentCourseSpecialization,
    StudentMockAccess,
    StudyGroup,
)
from portals.tests.test_quiz_submit import _portal_client_login
from portals.tests.test_quiz_visibility import QuizVisibilityTests, _ensure_active_portal_services
from portals.utils.ielts_mock_test import (
    IELTS_SERVICE,
    SAT_SERVICE,
    get_mock_take_url,
    pick_random_section_quizzes,
    resolve_mock_start_request,
    resolve_mock_take_request,
    serialize_mock_attempt_summary,
    start_mock_test_attempt,
)
from portals.utils.quiz_submit import (
    submit_listening_quiz_attempt,
    submit_manual_quiz_attempt,
    submit_reading_quiz_attempt,
    submit_speaking_quiz_attempt,
    submit_teacher_quiz_review,
    submit_variant_quiz_attempt,
)
from portals.utils.student_courses import quiz_visible_to_student

User = get_user_model()


class IeltsMockTestTests(QuizVisibilityTests):
    def setUp(self):
        super().setUp()
        from portals.tests.group_helpers import create_quiz_category

        self.mock_listening_category = create_quiz_category('Listening practice', 'ielts')
        self.mock_reading_category = create_quiz_category('Reading practice', 'ielts')
        self.mock_writing_category = create_quiz_category('Writing task 2', 'ielts')
        self.mock_speaking_category = create_quiz_category('Speaking', 'ielts')

        self.mock_listening_quiz = self._create_listening_quiz()
        self.mock_reading_quiz = self._create_reading_quiz()
        self.mock_writing_quiz = self._create_writing_quiz()
        self.mock_speaking_quiz = self._create_speaking_quiz()
        self.assign_student_quizzes(
            self.mock_listening_quiz,
            self.mock_reading_quiz,
            self.mock_writing_quiz,
            self.mock_speaking_quiz,
        )
        StudentMockAccess.objects.update_or_create(
            student=self.student,
            exam_program='ielts',
            defaults={'is_active': True},
        )

        self.parent_user = User.objects.create_user(username='mock_parent', password='pass')
        self.parent = ParentProfile.objects.create(user=self.parent_user)
        self.parent.students.add(self.student)

        self.client = Client()
        _portal_client_login(self.client, self.student_user)

    def _create_listening_quiz(self):
        quiz = Quiz.objects.create(
            category=self.mock_listening_category,
            topic='IELTS Listening Mock',
            is_listening=True,
            is_ielts=True,
        )
        audio = ListeningAudio.objects.create(
            quiz=quiz,
            order=1,
            title='Section 1',
            audio_url='https://example.com/audio.mp3',
        )
        ListeningQuestion.objects.create(
            audio=audio,
            order=1,
            question='Name?',
            correct_answer='Anna',
        )
        return quiz

    def _create_reading_quiz(self):
        quiz = Quiz.objects.create(
            category=self.mock_reading_category,
            topic='IELTS Reading Mock',
            is_reading=True,
            is_ielts=True,
        )
        passage = ReadingPassage.objects.create(
            quiz=quiz,
            order=1,
            title='Passage 1',
            body='<p>Sample text.</p>',
        )
        ReadingQuestion.objects.create(
            passage=passage,
            order=1,
            question_type=ReadingQuestionType.MCQ,
            question='<p>Pick one.</p>',
            answer_options=['A', 'B'],
            correct_answer='A',
        )
        return quiz

    def _create_writing_quiz(self):
        quiz = Quiz.objects.create(
            category=self.mock_writing_category,
            topic='IELTS Writing Mock',
            is_essay=True,
            is_ielts=True,
        )
        QuizQuestion.objects.create(
            quiz=quiz,
            order=1,
            question='Write an essay.',
        )
        return quiz

    def _create_speaking_quiz(self):
        quiz = Quiz.objects.create(
            category=self.mock_speaking_category,
            topic='IELTS Speaking Mock',
            is_speaking=True,
            is_ielts=True,
        )
        part = SpeakingPart.objects.create(
            quiz=quiz,
            order=1,
            part_type='part_1',
            title='Part 1',
        )
        SpeakingQuestion.objects.create(
            part=part,
            order=1,
            question='<p>Tell me about yourself.</p>',
        )
        return quiz

    def _complete_full_mock_attempt(self):
        attempt, _ = start_mock_test_attempt(self.student.pk, IELTS_SERVICE)
        submit_listening_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=attempt.listening_quiz_id,
            given_answers={
                str(ListeningQuestion.objects.filter(audio__quiz=attempt.listening_quiz).first().pk): 'Anna',
            },
            mock_attempt_id=attempt.pk,
            defer_notifications=True,
        )
        attempt.refresh_from_db()
        reading_question = ReadingQuestion.objects.filter(passage__quiz=attempt.reading_quiz).first()
        submit_reading_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=attempt.reading_quiz_id,
            given_answers={str(reading_question.pk): 0},
            mock_attempt_id=attempt.pk,
            defer_notifications=True,
        )
        attempt.refresh_from_db()
        writing_question = QuizQuestion.objects.filter(quiz=attempt.writing_quiz).first()
        submit_manual_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=attempt.writing_quiz_id,
            given_answers={str(writing_question.pk): 'My essay answer.'},
            mock_attempt_id=attempt.pk,
            defer_notifications=True,
        )
        attempt.refresh_from_db()
        speaking_question = SpeakingQuestion.objects.filter(part__quiz=attempt.speaking_quiz).first()
        from django.core.files.uploadedfile import SimpleUploadedFile

        audio = SimpleUploadedFile('answer.webm', b'fake-audio', content_type='audio/webm')
        submit_speaking_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=attempt.speaking_quiz_id,
            recording_files={str(speaking_question.pk): audio},
            mock_attempt_id=attempt.pk,
            defer_notifications=True,
        )
        attempt.refresh_from_db()
        return attempt

    def test_non_ielts_student_cannot_access_landing(self):
        StudentCourseSpecialization.objects.filter(student=self.student).update(is_active=False)
        response = self.client.get(reverse('portals:student-ielts-mock'))
        self.assertEqual(response.status_code, 404)

    def test_start_creates_attempt_and_redirects_to_listening(self):
        response = self.client.post(reverse('portals:student-ielts-mock-start'))
        self.assertEqual(response.status_code, 302)
        attempt = IeltsMockTestAttempt.objects.get(student=self.student, status='in_progress')
        self.assertEqual(response.url, get_mock_take_url(attempt, IeltsMockTestAttempt.Section.LISTENING))
        self.assertIn(f'mock={attempt.pk}', response.url)

    def test_new_start_abandons_previous_attempt(self):
        first, _ = start_mock_test_attempt(self.student.pk, IELTS_SERVICE)
        second, _ = start_mock_test_attempt(self.student.pk, IELTS_SERVICE)
        first.refresh_from_db()
        self.assertEqual(first.status, IeltsMockTestAttempt.Status.ABANDONED)
        self.assertEqual(second.status, IeltsMockTestAttempt.Status.IN_PROGRESS)

    def test_listening_submit_advances_to_reading_without_teacher_notification(self):
        attempt, _ = start_mock_test_attempt(self.student.pk, IELTS_SERVICE)
        outcome = submit_listening_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=attempt.listening_quiz_id,
            given_answers={
                str(ListeningQuestion.objects.filter(audio__quiz=attempt.listening_quiz).first().pk): 'Anna',
            },
            mock_attempt_id=attempt.pk,
            defer_notifications=True,
        )
        self.assertTrue(outcome['success'])
        self.assertIn('reading', outcome['next_url'])
        self.assertTrue(outcome.get('mock_continue'))
        self.assertIn('mock_next_section_label', outcome)
        attempt.refresh_from_db()
        self.assertEqual(attempt.current_section, IeltsMockTestAttempt.Section.READING)
        self.assertFalse(
            PortalNotification.objects.filter(
                kind=PortalNotification.Kind.RESULT_PUBLISHED,
            ).exists()
        )

    def test_mock_listening_submit_via_http_without_quiz_assignment(self):
        attempt, _ = start_mock_test_attempt(self.student.pk, IELTS_SERVICE)
        QuizAssignment.objects.filter(
            student=self.student,
            quiz_id=attempt.listening_quiz_id,
        ).delete()
        self.assertFalse(quiz_visible_to_student(attempt.listening_quiz, self.student.pk))

        self.client.get(get_mock_take_url(attempt, IeltsMockTestAttempt.Section.LISTENING))
        start_url = reverse('portals:student-quiz-start', kwargs={'pk': attempt.listening_quiz_id})
        self.assertEqual(self.client.post(f'{start_url}?mock={attempt.pk}').status_code, 200)

        question = ListeningQuestion.objects.filter(audio__quiz=attempt.listening_quiz).first()
        submit_url = reverse('portals:student-manual-quiz-submit', kwargs={'pk': attempt.listening_quiz_id})
        response = self.client.post(
            submit_url,
            data=json.dumps({
                'answers': {str(question.pk): 'Anna'},
                'duration_sec': 30,
                'mock': attempt.pk,
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()
        self.assertTrue(data['success'], data.get('error'))
        self.assertTrue(data.get('mock_continue'))

    def test_mock_reading_submit_via_http_without_quiz_assignment(self):
        attempt, _ = start_mock_test_attempt(self.student.pk, IELTS_SERVICE)
        submit_listening_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=attempt.listening_quiz_id,
            given_answers={
                str(ListeningQuestion.objects.filter(audio__quiz=attempt.listening_quiz).first().pk): 'Anna',
            },
            mock_attempt_id=attempt.pk,
            defer_notifications=True,
        )
        attempt.refresh_from_db()
        QuizAssignment.objects.filter(
            student=self.student,
            quiz_id=attempt.reading_quiz_id,
        ).delete()
        self.assertFalse(quiz_visible_to_student(attempt.reading_quiz, self.student.pk))

        self.client.get(get_mock_take_url(attempt, IeltsMockTestAttempt.Section.READING))
        start_url = reverse('portals:student-quiz-start', kwargs={'pk': attempt.reading_quiz_id})
        self.assertEqual(self.client.post(f'{start_url}?mock={attempt.pk}').status_code, 200)

        reading_question = ReadingQuestion.objects.filter(passage__quiz=attempt.reading_quiz).first()
        submit_url = reverse('portals:student-reading-quiz-submit', kwargs={'pk': attempt.reading_quiz_id})
        response = self.client.post(
            submit_url,
            data=json.dumps({
                'answers': {str(reading_question.pk): 0},
                'duration_sec': 30,
                'mock': attempt.pk,
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()
        self.assertTrue(data['success'], data.get('error'))
        self.assertTrue(data.get('mock_continue'))

    def test_mock_cancel_abandons_without_submitting_section(self):
        attempt, _ = start_mock_test_attempt(self.student.pk, IELTS_SERVICE)
        listening_url = get_mock_take_url(attempt, IeltsMockTestAttempt.Section.LISTENING)
        self.client.get(listening_url)
        start_url = reverse('portals:student-quiz-start', kwargs={'pk': attempt.listening_quiz_id})
        self.client.post(f'{start_url}?mock={attempt.pk}')
        cancel_url = (
            reverse('portals:student-quiz-cancel', kwargs={'pk': attempt.listening_quiz_id})
            + f'?mock={attempt.pk}&next={reverse("portals:student-ielts-mock")}'
        )
        # State-changing cancel requires POST; GET is redirect-only (CSRF safety).
        response = self.client.post(cancel_url)
        self.assertEqual(response.status_code, 302)
        attempt.refresh_from_db()
        self.assertEqual(attempt.status, IeltsMockTestAttempt.Status.ABANDONED)
        self.assertIsNone(attempt.listening_result_id)

    def test_mock_cancel_get_without_mock_param_redirects_with_next(self):
        attempt, _ = start_mock_test_attempt(self.student.pk, IELTS_SERVICE)
        listening_url = get_mock_take_url(attempt, IeltsMockTestAttempt.Section.LISTENING)
        self.client.get(listening_url)
        cancel_url = (
            reverse('portals:student-quiz-cancel', kwargs={'pk': attempt.listening_quiz_id})
            + f'?next={reverse("portals:student-ielts-mock")}'
        )
        response = self.client.get(cancel_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('portals:student-ielts-mock'))

    def test_mock_cancel_post_without_mock_param_infers_active_attempt(self):
        attempt, _ = start_mock_test_attempt(self.student.pk, IELTS_SERVICE)
        listening_url = get_mock_take_url(attempt, IeltsMockTestAttempt.Section.LISTENING)
        self.client.get(listening_url)
        start_url = reverse('portals:student-quiz-start', kwargs={'pk': attempt.listening_quiz_id})
        self.client.post(f'{start_url}?mock={attempt.pk}')
        cancel_url = (
            reverse('portals:student-quiz-cancel', kwargs={'pk': attempt.listening_quiz_id})
            + f'?next={reverse("portals:student-ielts-mock")}'
        )
        response = self.client.post(cancel_url)
        self.assertEqual(response.status_code, 302)
        attempt.refresh_from_db()
        self.assertEqual(attempt.status, IeltsMockTestAttempt.Status.ABANDONED)

    def test_stale_listening_page_redirects_to_current_section(self):
        attempt, _ = start_mock_test_attempt(self.student.pk, IELTS_SERVICE)
        submit_listening_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=attempt.listening_quiz_id,
            given_answers={
                str(ListeningQuestion.objects.filter(audio__quiz=attempt.listening_quiz).first().pk): 'Anna',
            },
            mock_attempt_id=attempt.pk,
            defer_notifications=True,
        )
        attempt.refresh_from_db()
        resolved = resolve_mock_take_request(
            self.student.pk,
            attempt.pk,
            attempt.listening_quiz_id,
        )
        self.assertEqual(
            resolved['mock_redirect'],
            get_mock_take_url(attempt, IeltsMockTestAttempt.Section.READING),
        )

    def test_stale_mock_start_redirects_to_current_section(self):
        attempt, _ = start_mock_test_attempt(self.student.pk, IELTS_SERVICE)
        submit_listening_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=attempt.listening_quiz_id,
            given_answers={
                str(ListeningQuestion.objects.filter(audio__quiz=attempt.listening_quiz).first().pk): 'Anna',
            },
            mock_attempt_id=attempt.pk,
            defer_notifications=True,
        )
        attempt.refresh_from_db()
        outcome = resolve_mock_start_request(
            self.student.pk,
            attempt.pk,
            attempt.listening_quiz_id,
        )
        self.assertTrue(outcome['success'])
        self.assertIn('reading', outcome['redirect_url'])

    def test_stale_listening_take_page_redirects_over_http(self):
        attempt, _ = start_mock_test_attempt(self.student.pk, IELTS_SERVICE)
        submit_listening_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=attempt.listening_quiz_id,
            given_answers={
                str(ListeningQuestion.objects.filter(audio__quiz=attempt.listening_quiz).first().pk): 'Anna',
            },
            mock_attempt_id=attempt.pk,
            defer_notifications=True,
        )
        attempt.refresh_from_db()
        listening_url = get_mock_take_url(attempt, IeltsMockTestAttempt.Section.LISTENING)
        response = self.client.get(listening_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            get_mock_take_url(attempt, IeltsMockTestAttempt.Section.READING),
        )

    def test_writing_submit_advances_to_speaking_in_mock(self):
        attempt, _ = start_mock_test_attempt(self.student.pk, IELTS_SERVICE)
        submit_listening_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=attempt.listening_quiz_id,
            given_answers={
                str(ListeningQuestion.objects.filter(audio__quiz=attempt.listening_quiz).first().pk): 'Anna',
            },
            mock_attempt_id=attempt.pk,
            defer_notifications=True,
        )
        attempt.refresh_from_db()
        reading_question = ReadingQuestion.objects.filter(passage__quiz=attempt.reading_quiz).first()
        submit_reading_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=attempt.reading_quiz_id,
            given_answers={str(reading_question.pk): 0},
            mock_attempt_id=attempt.pk,
            defer_notifications=True,
        )
        attempt.refresh_from_db()
        writing_question = QuizQuestion.objects.filter(quiz=attempt.writing_quiz).first()
        outcome = submit_manual_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=attempt.writing_quiz_id,
            given_answers={str(writing_question.pk): 'My essay answer.'},
            mock_attempt_id=attempt.pk,
            defer_notifications=True,
        )
        self.assertTrue(outcome['success'])
        self.assertIn('speaking', outcome['next_url'])
        self.assertTrue(outcome.get('mock_continue'))
        attempt.refresh_from_db()
        self.assertEqual(attempt.current_section, IeltsMockTestAttempt.Section.SPEAKING)

    def test_regular_quiz_submit_has_no_mock_continue(self):
        writing_question = QuizQuestion.objects.filter(quiz=self.mock_writing_quiz).first()
        outcome = submit_manual_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=self.mock_writing_quiz.pk,
            given_answers={str(writing_question.pk): 'Standalone essay.'},
        )
        self.assertTrue(outcome['success'])
        self.assertNotIn('mock_continue', outcome)
        self.assertNotIn('next_url', outcome)

    def test_full_mock_flow_puts_manual_sections_in_teacher_review_queue(self):
        attempt, _ = start_mock_test_attempt(self.student.pk, IELTS_SERVICE)

        submit_listening_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=attempt.listening_quiz_id,
            given_answers={
                str(ListeningQuestion.objects.filter(audio__quiz=attempt.listening_quiz).first().pk): 'Anna',
            },
            mock_attempt_id=attempt.pk,
            defer_notifications=True,
        )
        attempt.refresh_from_db()
        reading_question = ReadingQuestion.objects.filter(passage__quiz=attempt.reading_quiz).first()
        submit_reading_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=attempt.reading_quiz_id,
            given_answers={str(reading_question.pk): 0},
            mock_attempt_id=attempt.pk,
            defer_notifications=True,
        )
        attempt.refresh_from_db()
        writing_question = QuizQuestion.objects.filter(quiz=attempt.writing_quiz).first()
        submit_manual_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=attempt.writing_quiz_id,
            given_answers={str(writing_question.pk): 'My essay answer.'},
            mock_attempt_id=attempt.pk,
            defer_notifications=True,
        )
        attempt.refresh_from_db()
        speaking_question = SpeakingQuestion.objects.filter(part__quiz=attempt.speaking_quiz).first()
        from django.core.files.uploadedfile import SimpleUploadedFile

        audio = SimpleUploadedFile('answer.webm', b'fake-audio', content_type='audio/webm')
        outcome = submit_speaking_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=attempt.speaking_quiz_id,
            recording_files={str(speaking_question.pk): audio},
            mock_attempt_id=attempt.pk,
            defer_notifications=True,
        )
        self.assertTrue(outcome['success'])
        self.assertTrue(outcome.get('mock_completed'))
        self.assertTrue(outcome.get('mock_continue'))
        self.assertNotIn('mock_next_section_label', outcome)
        attempt.refresh_from_db()
        self.assertEqual(attempt.status, IeltsMockTestAttempt.Status.COMPLETED)
        complete_url = reverse('portals:student-mock-complete', kwargs={'program': IELTS_SERVICE, 'pk': attempt.pk})
        self.assertEqual(outcome['next_url'], complete_url)
        response = self.client.get(complete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            PortalNotification.objects.filter(
                teacher=self.teacher,
                kind=PortalNotification.Kind.MOCK_TEST_COMPLETED,
                ielts_mock_test=attempt,
            ).exists()
        )
        self.assertFalse(
            PortalNotification.objects.filter(
                teacher=self.teacher,
                kind=PortalNotification.Kind.MOCK_TEST_SECTION_REVIEW,
            ).exists()
        )
        from portals.utils.queries import get_teacher_pending_quiz_results

        pending_ids = {row['id'] for row in get_teacher_pending_quiz_results(self.teacher.pk)}
        self.assertIn(attempt.writing_result_id, pending_ids)
        self.assertIn(attempt.speaking_result_id, pending_ids)
        self.assertFalse(
            PortalNotification.objects.filter(
                teacher=self.teacher,
                kind=PortalNotification.Kind.SUBMISSION_PENDING,
            ).exists()
        )
        self.assertEqual(
            PortalNotification.objects.filter(kind=PortalNotification.Kind.RESULT_PUBLISHED).count(),
            0,
        )

    def test_speaking_take_page_loads_after_writing_in_mock(self):
        from portals.utils.queries import get_student_speaking_quiz_take_data

        attempt, _ = start_mock_test_attempt(self.student.pk, IELTS_SERVICE)
        submit_listening_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=attempt.listening_quiz_id,
            given_answers={
                str(ListeningQuestion.objects.filter(audio__quiz=attempt.listening_quiz).first().pk): 'Anna',
            },
            mock_attempt_id=attempt.pk,
            defer_notifications=True,
        )
        attempt.refresh_from_db()
        reading_question = ReadingQuestion.objects.filter(passage__quiz=attempt.reading_quiz).first()
        submit_reading_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=attempt.reading_quiz_id,
            given_answers={str(reading_question.pk): 0},
            mock_attempt_id=attempt.pk,
            defer_notifications=True,
        )
        attempt.refresh_from_db()
        writing_question = QuizQuestion.objects.filter(quiz=attempt.writing_quiz).first()
        submit_manual_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=attempt.writing_quiz_id,
            given_answers={str(writing_question.pk): 'My essay answer.'},
            mock_attempt_id=attempt.pk,
            defer_notifications=True,
        )
        attempt.refresh_from_db()
        self.assertEqual(attempt.current_section, IeltsMockTestAttempt.Section.SPEAKING)

        take_data = get_student_speaking_quiz_take_data(
            self.student.pk,
            attempt.speaking_quiz_id,
            mock_attempt_id=attempt.pk,
        )
        self.assertIsNotNone(take_data)
        self.assertFalse(take_data['view_only'])

        speaking_url = get_mock_take_url(attempt, IeltsMockTestAttempt.Section.SPEAKING)
        response = self.client.get(speaking_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-quiz-speaking-take')

    def test_writing_submit_in_mock_appears_in_teacher_review_queue(self):
        from portals.utils.queries import get_teacher_pending_quiz_results

        attempt, _ = start_mock_test_attempt(self.student.pk, IELTS_SERVICE)
        submit_listening_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=attempt.listening_quiz_id,
            given_answers={
                str(ListeningQuestion.objects.filter(audio__quiz=attempt.listening_quiz).first().pk): 'Anna',
            },
            mock_attempt_id=attempt.pk,
            defer_notifications=True,
        )
        attempt.refresh_from_db()
        reading_question = ReadingQuestion.objects.filter(passage__quiz=attempt.reading_quiz).first()
        submit_reading_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=attempt.reading_quiz_id,
            given_answers={str(reading_question.pk): 0},
            mock_attempt_id=attempt.pk,
            defer_notifications=True,
        )
        attempt.refresh_from_db()
        writing_question = QuizQuestion.objects.filter(quiz=attempt.writing_quiz).first()
        submit_manual_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=attempt.writing_quiz_id,
            given_answers={str(writing_question.pk): 'My essay answer.'},
            mock_attempt_id=attempt.pk,
            defer_notifications=True,
        )
        attempt.refresh_from_db()
        self.assertEqual(attempt.current_section, IeltsMockTestAttempt.Section.SPEAKING)
        pending = get_teacher_pending_quiz_results(self.teacher.pk)
        pending_ids = {row['id'] for row in pending}
        self.assertIn(attempt.writing_result_id, pending_ids)
        self.assertFalse(
            PortalNotification.objects.filter(
                teacher=self.teacher,
                kind=PortalNotification.Kind.MOCK_TEST_SECTION_REVIEW,
            ).exists()
        )
        self.assertFalse(
            PortalNotification.objects.filter(
                kind=PortalNotification.Kind.MOCK_TEST_COMPLETED,
                ielts_mock_test=attempt,
            ).exists()
        )

    def test_parent_notified_when_mock_test_completed(self):
        self.student.phone = '+994501112233'
        self.student.save(update_fields=['phone'])
        attempt = self._complete_full_mock_attempt()
        self.assertTrue(
            PortalNotification.objects.filter(
                parent=self.parent,
                kind=PortalNotification.Kind.MOCK_TEST_COMPLETED,
                ielts_mock_test=attempt,
                is_read=False,
            ).exists()
        )
        self.assertTrue(
            PortalNotification.objects.filter(
                teacher=self.teacher,
                kind=PortalNotification.Kind.MOCK_TEST_COMPLETED,
                ielts_mock_test=attempt,
            ).exists()
        )
        from portals.utils.notifications import get_notifications

        teacher_items = get_notifications(teacher_id=self.teacher.pk, period='all')
        mock_items = [item for item in teacher_items if item.get('is_mock_test_completed')]
        self.assertEqual(len(mock_items), 1)
        self.assertEqual(mock_items[0]['contact_phone'], '+994501112233')

    def test_mock_completed_notifies_teacher_via_group_when_quiz_category_has_no_services(self):
        """Teacher recipients fall back to study-group + exam program when quiz codes are empty."""
        from portals.utils.notifications import create_mock_test_completed_notifications

        attempt = self._complete_full_mock_attempt()
        PortalNotification.objects.filter(ielts_mock_test=attempt).delete()
        for quiz in (
            self.mock_listening_quiz,
            self.mock_reading_quiz,
            self.mock_writing_quiz,
            self.mock_speaking_quiz,
        ):
            quiz.category.services.clear()

        create_mock_test_completed_notifications(attempt)
        self.assertTrue(
            PortalNotification.objects.filter(
                teacher=self.teacher,
                kind=PortalNotification.Kind.MOCK_TEST_COMPLETED,
                ielts_mock_test=attempt,
            ).exists()
        )

    def test_parent_notified_when_mock_manual_section_reviewed(self):
        attempt = self._complete_full_mock_attempt()
        writing_review = submit_teacher_quiz_review(
            teacher_id=self.teacher.pk,
            result_id=attempt.writing_result_id,
            total_score=8,
        )
        self.assertTrue(writing_review['success'])
        self.assertTrue(
            PortalNotification.objects.filter(
                parent=self.parent,
                kind=PortalNotification.Kind.RESULT_PUBLISHED,
                quiz_result_id=attempt.writing_result_id,
                is_read=False,
            ).exists()
        )

    def test_mock_overall_score_hidden_until_manual_sections_reviewed(self):
        attempt = self._complete_full_mock_attempt()
        summary = serialize_mock_attempt_summary(attempt)
        self.assertFalse(summary['is_fully_graded'])
        self.assertIsNone(summary['overall_band'])
        self.assertEqual(summary['pending_review_count'], 2)
        self.assertIsNotNone(summary['auto_score_total'])
        self.assertIsNone(summary['manual_score_total'])

        complete_url = reverse('portals:student-mock-complete', kwargs={'program': IELTS_SERVICE, 'pk': attempt.pk})
        response = self.client.get(complete_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _('Awaiting review'))
        self.assertNotIn(b'7.5', response.content)

        self.assertFalse(
            PortalNotification.objects.filter(
                kind=PortalNotification.Kind.MOCK_TEST_RESULTS_PUBLISHED,
                ielts_mock_test=attempt,
            ).exists()
        )

    def test_mock_overall_score_published_after_teacher_reviews_manual_sections(self):
        attempt = self._complete_full_mock_attempt()
        writing_review = submit_teacher_quiz_review(
            teacher_id=self.teacher.pk,
            result_id=attempt.writing_result_id,
            total_score=8,
        )
        self.assertTrue(writing_review['success'])
        attempt.refresh_from_db()
        summary = serialize_mock_attempt_summary(attempt)
        self.assertFalse(summary['is_fully_graded'])
        self.assertIsNone(summary['overall_band'])

        speaking_review = submit_teacher_quiz_review(
            teacher_id=self.teacher.pk,
            result_id=attempt.speaking_result_id,
            total_score=6,
        )
        self.assertTrue(speaking_review['success'])
        attempt.refresh_from_db()
        summary = serialize_mock_attempt_summary(attempt)
        self.assertTrue(summary['is_fully_graded'])
        self.assertEqual(summary['overall_band'], 7.5)
        self.assertEqual(summary['auto_score_total'], 2)
        self.assertEqual(summary['manual_score_total'], 14)
        self.assertEqual(summary['auto_band_average'], 9)
        self.assertEqual(summary['manual_band_average'], 6.5)

        self.assertTrue(
            PortalNotification.objects.filter(
                student=self.student,
                kind=PortalNotification.Kind.MOCK_TEST_RESULTS_PUBLISHED,
                ielts_mock_test=attempt,
            ).exists()
        )
        self.assertTrue(
            PortalNotification.objects.filter(
                parent=self.parent,
                kind=PortalNotification.Kind.MOCK_TEST_RESULTS_PUBLISHED,
                ielts_mock_test=attempt,
                is_read=False,
            ).exists()
        )

        complete_url = reverse('portals:student-mock-complete', kwargs={'program': IELTS_SERVICE, 'pk': attempt.pk})
        response = self.client.get(complete_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _('Overall result'))
        self.assertContains(response, '7.5')

    def test_missing_section_blocks_start(self):
        Quiz.objects.filter(is_listening=True).delete()
        response = self.client.post(reverse('portals:student-ielts-mock-start'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('portals:student-mock-landing', kwargs={'program': IELTS_SERVICE}))
        self.assertFalse(
            IeltsMockTestAttempt.objects.filter(student=self.student, status='in_progress').exists()
        )

    def test_mock_start_ignores_pending_standalone_manual_quizzes(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        writing_question = QuizQuestion.objects.filter(quiz=self.mock_writing_quiz).first()
        submit_manual_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=self.mock_writing_quiz.pk,
            given_answers={str(writing_question.pk): 'Standalone essay pending review.'},
        )
        speaking_question = SpeakingQuestion.objects.filter(part__quiz=self.mock_speaking_quiz).first()
        audio = SimpleUploadedFile('standalone.webm', b'fake-audio', content_type='audio/webm')
        submit_speaking_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=self.mock_speaking_quiz.pk,
            recording_files={str(speaking_question.pk): audio},
        )

        attempt, error = start_mock_test_attempt(self.student.pk, IELTS_SERVICE)
        self.assertIsNone(error)
        self.assertIsNotNone(attempt)

    def test_mock_results_are_linked_to_attempt_not_standalone(self):
        attempt, _ = start_mock_test_attempt(self.student.pk, IELTS_SERVICE)
        submit_listening_quiz_attempt(
            student_id=self.student.pk,
            quiz_id=attempt.listening_quiz_id,
            given_answers={
                str(ListeningQuestion.objects.filter(audio__quiz=attempt.listening_quiz).first().pk): 'Anna',
            },
            mock_attempt_id=attempt.pk,
            defer_notifications=True,
        )
        attempt.refresh_from_db()
        self.assertEqual(attempt.listening_result.ielts_mock_attempt_id, attempt.pk)
        self.assertFalse(
            QuizResult.objects.filter(
                student_id=self.student.pk,
                quiz_id=attempt.listening_quiz_id,
                ielts_mock_attempt__isnull=True,
            ).exists()
        )

    def test_mock_pool_ignores_quizzes_without_program_flag(self):
        Quiz.objects.filter(pk=self.mock_listening_quiz.pk).update(is_ielts=False)
        attempt, error = start_mock_test_attempt(self.student.pk, IELTS_SERVICE)
        self.assertIsNotNone(error)
        self.assertIsNone(attempt)

    def test_quiz_cannot_be_both_ielts_and_sat(self):
        quiz = Quiz(
            category=self.mock_listening_category,
            topic='Invalid dual flag',
            is_listening=True,
            is_ielts=True,
            is_sat=True,
        )
        from django.core.exceptions import ValidationError
        from django.db import IntegrityError

        with self.assertRaises(ValidationError):
            quiz.full_clean()
        with self.assertRaises(IntegrityError):
            Quiz.objects.create(
                category=self.mock_listening_category,
                topic='Invalid dual flag saved',
                is_listening=True,
                is_ielts=True,
                is_sat=True,
            )

    def test_student_with_ielts_and_sat_enrollment_sees_mock_picker(self):
        from projects.models.service_models import Service

        Service.objects.get_or_create(
            slug='sat',
            defaults={'name_az': 'SAT', 'name_en': 'SAT', 'is_active': True},
        )
        StudentCourseSpecialization.objects.update_or_create(
            student=self.student,
            course_type='sat',
            defaults={'is_active': True},
        )
        StudentMockAccess.objects.update_or_create(
            student=self.student,
            exam_program='ielts',
            defaults={'is_active': True},
        )
        client = Client()
        _portal_client_login(client, self.student_user)
        response = client.get(reverse('portals:student-mock-picker'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('portals:student-mock-landing', kwargs={'program': IELTS_SERVICE}))
        self.assertContains(response, reverse('portals:student-mock-landing', kwargs={'program': SAT_SERVICE}))


class SatMockTestTests(TestCase):
    def setUp(self):
        _ensure_active_portal_services()
        from projects.models.service_models import Service
        from portals.models import StudentProfile, TeacherCourseSpecialization, TeacherProfile
        from portals.tests.group_helpers import link_study_group_services

        Service.objects.get_or_create(
            slug='sat',
            defaults={'name_az': 'SAT', 'name_en': 'SAT', 'is_active': True},
        )

        self.student_user = User.objects.create_user(username='sat_student', password='pass')
        self.student = StudentProfile.objects.create(user=self.student_user)
        self.teacher = TeacherProfile.objects.create(
            user=User.objects.create_user(username='sat_teacher', password='pass'),
        )
        TeacherCourseSpecialization.objects.create(teacher=self.teacher, course_type='sat')
        self.sat_group = StudyGroup.objects.create(
            teacher=self.teacher,
            name='SAT A',
            max_students=10,
        )
        link_study_group_services(self.sat_group, 'sat')
        self.sat_group.students.add(self.student)

        from portals.tests.group_helpers import create_quiz_category

        self.rw_category = create_quiz_category('SAT Reading and Writing', 'sat')
        self.math_category = create_quiz_category('SAT Math', 'sat')

        self.sat_reading_quiz = self._create_sat_quiz(
            self.rw_category,
            'SAT Reading and Writing Mock',
            sat_section='reading',
        )
        self.sat_math_quiz = self._create_sat_quiz(
            self.math_category,
            'SAT Math Mock',
            sat_section='algebra',
        )
        for quiz in (self.sat_reading_quiz, self.sat_math_quiz):
            QuizAssignment.objects.update_or_create(
                student=self.student,
                quiz=quiz,
                defaults={'is_active': True},
            )
        StudentMockAccess.objects.update_or_create(
            student=self.student,
            exam_program='sat',
            defaults={'is_active': True},
        )
        self.client = Client()
        _portal_client_login(self.client, self.student_user)

    def _create_sat_quiz(self, category, topic, *, sat_section='algebra'):
        quiz = Quiz.objects.create(
            category=category,
            topic=topic,
            is_sat=True,
            sat_section=sat_section,
        )
        QuizQuestion.objects.create(
            quiz=quiz,
            order=1,
            question='<p>Sample SAT question?</p>',
            answer_options=['A', 'B'],
            correct_answer='A',
            correct_option_index=0,
        )
        return quiz

    def test_sat_student_mock_picks_flagged_quizzes_in_section_order(self):
        picked = pick_random_section_quizzes(self.student.pk, SAT_SERVICE)
        self.assertEqual(picked['reading_writing'].pk, self.sat_reading_quiz.pk)
        self.assertEqual(picked['math'].pk, self.sat_math_quiz.pk)

        attempt, error = start_mock_test_attempt(self.student.pk, SAT_SERVICE)
        self.assertIsNone(error)
        self.assertEqual(attempt.exam_program, SAT_SERVICE)
        self.assertEqual(attempt.reading_quiz_id, self.sat_reading_quiz.pk)
        self.assertEqual(attempt.math_quiz_id, self.sat_math_quiz.pk)
        self.assertIsNone(attempt.listening_quiz_id)
        self.assertIsNone(attempt.writing_quiz_id)
        self.assertIsNone(attempt.speaking_quiz_id)

    def test_sat_student_start_redirects_to_first_section(self):
        response = self.client.post(
            reverse('portals:student-mock-start', kwargs={'program': SAT_SERVICE}),
        )
        self.assertEqual(response.status_code, 302)
        attempt = IeltsMockTestAttempt.objects.get(student=self.student, status='in_progress')
        expected_url = get_mock_take_url(attempt, 'reading_writing')
        self.assertEqual(response.url, expected_url)
        self.assertIn('student/quizzes/', expected_url)
        self.assertIn('/take/', expected_url)
        self.assertNotIn('/manual/', expected_url)

    def test_sat_mock_take_page_loads(self):
        attempt, _ = start_mock_test_attempt(self.student.pk, SAT_SERVICE)
        take_url = get_mock_take_url(attempt, 'reading_writing')
        response = self.client.get(take_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'portals/student/quiz_take.html')
        self.assertContains(response, self.sat_reading_quiz.topic)

    def test_sat_mock_section_submit_advances(self):
        attempt, _ = start_mock_test_attempt(self.student.pk, SAT_SERVICE)
        rw_question = self.sat_reading_quiz.questions.first()

        self.client.get(get_mock_take_url(attempt, 'reading_writing'))
        start_url = reverse('portals:student-quiz-start', kwargs={'pk': attempt.reading_quiz_id})
        self.assertEqual(self.client.post(f'{start_url}?mock={attempt.pk}').status_code, 200)

        submit_url = reverse('portals:student-quiz-submit', kwargs={'pk': attempt.reading_quiz_id})
        response = self.client.post(
            submit_url,
            data=json.dumps({
                'answers': {str(rw_question.pk): rw_question.correct_option_index},
                'duration_sec': 30,
                'mock': attempt.pk,
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()
        self.assertTrue(data['success'], data.get('error'))
        self.assertTrue(data.get('mock_continue'))
        self.assertIn('/take/', data['next_url'])
        self.assertNotIn('/manual/', data['next_url'])

        attempt.refresh_from_db()
        self.assertEqual(attempt.current_section, 'math')

        math_question = self.sat_math_quiz.questions.first()
        self.client.get(get_mock_take_url(attempt, 'math'))
        start_url = reverse('portals:student-quiz-start', kwargs={'pk': attempt.math_quiz_id})
        self.assertEqual(self.client.post(f'{start_url}?mock={attempt.pk}').status_code, 200)

        response = self.client.post(
            submit_url.replace(str(attempt.reading_quiz_id), str(attempt.math_quiz_id)),
            data=json.dumps({
                'answers': {str(math_question.pk): math_question.correct_option_index},
                'duration_sec': 25,
                'mock': attempt.pk,
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()
        self.assertTrue(data['success'], data.get('error'))
        self.assertTrue(data.get('mock_completed'))
        attempt.refresh_from_db()
        self.assertEqual(attempt.status, IeltsMockTestAttempt.Status.COMPLETED)

    def test_sat_quiz_requires_sat_section(self):
        quiz = Quiz(
            category=self.rw_category,
            topic='Invalid SAT quiz',
            is_sat=True,
        )
        with self.assertRaises(ValidationError):
            quiz.full_clean()

    def test_sat_reading_section_sets_reading_format(self):
        quiz = Quiz(
            category=self.rw_category,
            topic='SAT Reading passages',
            is_sat=True,
            sat_section=Quiz.SatSection.READING,
        )
        quiz.full_clean()
        self.assertTrue(quiz.is_reading)
        self.assertFalse(quiz.is_math)

    def test_sat_writing_section_stays_variant(self):
        quiz = Quiz(
            category=self.rw_category,
            topic='SAT Writing MCQ',
            is_sat=True,
            sat_section=Quiz.SatSection.WRITING,
        )
        quiz.full_clean()
        self.assertFalse(quiz.is_reading)
        self.assertTrue(quiz.is_variant_quiz)


class IeltsMockAccessWithoutEnrollmentTests(TestCase):
    def setUp(self):
        _ensure_active_portal_services()
        self.user = User.objects.create_user(username='plain', password='pass')
        from portals.models import StudentProfile

        StudentProfile.objects.create(user=self.user)
        self.client = Client()
        _portal_client_login(self.client, self.user)

    def test_landing_requires_ielts_enrollment(self):
        response = self.client.get(reverse('portals:student-ielts-mock'))
        self.assertEqual(response.status_code, 404)
