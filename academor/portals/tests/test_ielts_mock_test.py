from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from portals.models import (
    IeltsMockTestAttempt,
    ListeningAudio,
    ListeningQuestion,
    PortalNotification,
    Quiz,
    QuizCategory,
    QuizQuestion,
    QuizResult,
    ReadingPassage,
    ReadingQuestion,
    ReadingQuestionType,
    SpeakingPart,
    SpeakingQuestion,
    StudentCourseSpecialization,
)
from portals.tests.test_quiz_submit import _portal_client_login
from portals.tests.test_quiz_visibility import QuizVisibilityTests, _ensure_active_portal_services
from portals.utils.ielts_mock_test import (
    get_mock_take_url,
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
)

User = get_user_model()


class IeltsMockTestTests(QuizVisibilityTests):
    def setUp(self):
        super().setUp()
        self.mock_listening_category = QuizCategory.objects.create(
            service='ielts',
            name='Listening practice',
        )
        self.mock_reading_category = QuizCategory.objects.create(
            service='ielts',
            name='Reading practice',
        )
        self.mock_writing_category = QuizCategory.objects.create(
            service='ielts',
            name='Writing task 2',
        )
        self.mock_speaking_category = QuizCategory.objects.create(
            service='ielts',
            name='Speaking',
        )

        self.mock_listening_quiz = self._create_listening_quiz()
        self.mock_reading_quiz = self._create_reading_quiz()
        self.mock_writing_quiz = self._create_writing_quiz()
        self.mock_speaking_quiz = self._create_speaking_quiz()

        self.client = Client()
        _portal_client_login(self.client, self.student_user)

    def _create_listening_quiz(self):
        quiz = Quiz.objects.create(
            category=self.mock_listening_category,
            topic='IELTS Listening Mock',
            is_listening=True,
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
        attempt, _ = start_mock_test_attempt(self.student.pk)
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
        first, _ = start_mock_test_attempt(self.student.pk)
        second, _ = start_mock_test_attempt(self.student.pk)
        first.refresh_from_db()
        self.assertEqual(first.status, IeltsMockTestAttempt.Status.ABANDONED)
        self.assertEqual(second.status, IeltsMockTestAttempt.Status.IN_PROGRESS)

    def test_listening_submit_advances_to_reading_without_teacher_notification(self):
        attempt, _ = start_mock_test_attempt(self.student.pk)
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

    def test_mock_cancel_abandons_without_submitting_section(self):
        attempt, _ = start_mock_test_attempt(self.student.pk)
        listening_url = get_mock_take_url(attempt, IeltsMockTestAttempt.Section.LISTENING)
        self.client.get(listening_url)
        start_url = reverse('portals:student-quiz-start', kwargs={'pk': attempt.listening_quiz_id})
        self.client.post(f'{start_url}?mock={attempt.pk}')
        cancel_url = (
            reverse('portals:student-quiz-cancel', kwargs={'pk': attempt.listening_quiz_id})
            + f'?mock={attempt.pk}&next={reverse("portals:student-ielts-mock")}'
        )
        response = self.client.get(cancel_url)
        self.assertEqual(response.status_code, 302)
        attempt.refresh_from_db()
        self.assertEqual(attempt.status, IeltsMockTestAttempt.Status.ABANDONED)
        self.assertIsNone(attempt.listening_result_id)

    def test_stale_listening_page_redirects_to_current_section(self):
        attempt, _ = start_mock_test_attempt(self.student.pk)
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
        attempt, _ = start_mock_test_attempt(self.student.pk)
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
        attempt, _ = start_mock_test_attempt(self.student.pk)
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
        attempt, _ = start_mock_test_attempt(self.student.pk)
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

    def test_full_mock_flow_notifies_teacher_once(self):
        attempt, _ = start_mock_test_attempt(self.student.pk)

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
        complete_url = reverse('portals:student-ielts-mock-complete', kwargs={'pk': attempt.pk})
        self.assertEqual(outcome['next_url'], complete_url)
        response = self.client.get(complete_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            PortalNotification.objects.filter(
                teacher=self.teacher,
                kind=PortalNotification.Kind.MOCK_TEST_COMPLETED,
                ielts_mock_test=attempt,
            ).count(),
            1,
        )
        self.assertEqual(
            PortalNotification.objects.filter(
                teacher=self.teacher,
                kind=PortalNotification.Kind.MOCK_TEST_SECTION_REVIEW,
                ielts_mock_test=attempt,
            ).count(),
            0,
        )
        self.assertEqual(
            PortalNotification.objects.filter(
                teacher=self.teacher,
                kind=PortalNotification.Kind.MOCK_TEST_SECTION_REVIEW,
                quiz_result__in=[attempt.writing_result, attempt.speaking_result],
            ).count(),
            2,
        )
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

        attempt, _ = start_mock_test_attempt(self.student.pk)
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

    def test_writing_submit_in_mock_creates_section_review_notification(self):
        attempt, _ = start_mock_test_attempt(self.student.pk)
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
        self.assertTrue(
            PortalNotification.objects.filter(
                teacher=self.teacher,
                kind=PortalNotification.Kind.MOCK_TEST_SECTION_REVIEW,
                quiz_result=attempt.writing_result,
            ).exists()
        )
        self.assertFalse(
            PortalNotification.objects.filter(
                kind=PortalNotification.Kind.MOCK_TEST_COMPLETED,
                ielts_mock_test=attempt,
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

        complete_url = reverse('portals:student-ielts-mock-complete', kwargs={'pk': attempt.pk})
        response = self.client.get(complete_url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Overall result')
        self.assertContains(response, 'Awaiting review')

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

        complete_url = reverse('portals:student-ielts-mock-complete', kwargs={'pk': attempt.pk})
        response = self.client.get(complete_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Overall result')
        self.assertContains(response, '7.5')

    def test_missing_section_blocks_start(self):
        Quiz.objects.filter(is_listening=True).delete()
        response = self.client.post(reverse('portals:student-ielts-mock-start'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('portals:student-ielts-mock'))
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

        attempt, error = start_mock_test_attempt(self.student.pk)
        self.assertIsNone(error)
        self.assertIsNotNone(attempt)

    def test_mock_results_are_linked_to_attempt_not_standalone(self):
        attempt, _ = start_mock_test_attempt(self.student.pk)
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
