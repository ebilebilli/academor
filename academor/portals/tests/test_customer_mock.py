from datetime import timedelta
from decimal import Decimal
import json

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from payments.models import CourseEnrollment, Payment
from payments.mock_fulfillment import fulfill_mock_purchase
from portals.models import (
    CustomerProfile,
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
    StudentMockAccess,
)
from portals.tests.test_quiz_submit import _portal_client_login
from portals.tests.test_quiz_visibility import QuizVisibilityTests
from portals.utils.portal_session import (
    PORTAL_COOKIE_NAME,
    PortalSessionStore,
    quiz_start_session_key,
)
from portals.utils.customer_mock import (
    consume_customer_mock_credit_on_quiz_start,
    customer_can_start_mock,
    customer_has_in_progress_mock,
    get_customer_mock_take_url,
    resolve_customer_mock_take_request,
    start_customer_mock_test_attempt,
)
from portals.utils.ielts_mock_test import (
    IELTS_SERVICE,
    NEXT_SECTION_BY_SECTION,
    SAT_SERVICE,
    start_mock_test_attempt,
    validate_mock_section_submit,
)
from portals.utils.queries import get_customer_profile, get_portal_role, serialize_customer
from portals.utils.quiz_submit import (
    submit_listening_quiz_attempt,
    submit_manual_quiz_attempt,
    submit_reading_quiz_attempt,
)
from projects.models import CoursePricePackage, Service

User = get_user_model()


class CustomerMockRoleTests(QuizVisibilityTests):
    def setUp(self):
        super().setUp()
        from portals.tests.group_helpers import create_quiz_category

        self.mock_listening_category = create_quiz_category('Listening practice', 'ielts')
        self.mock_reading_category = create_quiz_category('Reading practice', 'ielts')
        self.mock_writing_category = create_quiz_category('Writing task 2', 'ielts')
        self.mock_speaking_category = create_quiz_category('Speaking', 'ielts')
        self._create_mock_quizzes()
        StudentMockAccess.objects.update_or_create(
            student=self.student,
            exam_program='ielts',
            defaults={'is_active': True},
        )

        self.customer_user = User.objects.create_user(username='customer1', password='pass')
        self.customer = CustomerProfile.objects.create(
            user=self.customer_user,
            phone='+994501112233',
            ielts_mock_credits=1,
            teacher=self.teacher,
        )
        self.mock_service = Service.objects.create(
            name_az='IELTS Mock',
            slug='ielts-mock-test',
            is_active=True,
            ielts_mock_test=True,
        )
        self.package = CoursePricePackage.objects.create(
            course=self.mock_service,
            name_az='1 Mock',
            credits=1,
            price=Decimal('25.00'),
            is_active=True,
        )

    def _create_mock_quizzes(self):
        listening = Quiz.objects.create(
            category=self.mock_listening_category,
            topic='IELTS Listening Mock',
            is_listening=True,
            is_ielts=True,
        )
        audio = ListeningAudio.objects.create(
            quiz=listening,
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

        reading = Quiz.objects.create(
            category=self.mock_reading_category,
            topic='IELTS Reading Mock',
            is_reading=True,
            is_ielts=True,
        )
        passage = ReadingPassage.objects.create(
            quiz=reading,
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

        writing = Quiz.objects.create(
            category=self.mock_writing_category,
            topic='IELTS Writing Mock',
            is_essay=True,
            is_ielts=True,
        )
        QuizQuestion.objects.create(
            quiz=writing,
            order=1,
            question='Write an essay.',
            prompt_type='text',
        )

        speaking = Quiz.objects.create(
            category=self.mock_speaking_category,
            topic='IELTS Speaking Mock',
            is_speaking=True,
            is_ielts=True,
        )
        part = SpeakingPart.objects.create(quiz=speaking, order=1, part_type='part_1')
        SpeakingQuestion.objects.create(part=part, order=1, question='Tell me about yourself.')

    def test_customer_role_resolution(self):
        self.assertEqual(get_portal_role(self.customer_user), 'customer')

    def test_customer_dashboard_requires_login(self):
        response = self.client.get(reverse('portals:customer-dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_customer_dashboard_ok(self):
        client = Client()
        _portal_client_login(client, self.customer_user)
        response = client.get(reverse('portals:customer-dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('portals:customer-mock-packages'))

    def test_customer_dashboard_splits_mock_program_sections(self):
        self.customer.sat_mock_credits = 2
        self.customer.save(update_fields=['sat_mock_credits'])
        client = Client()
        _portal_client_login(client, self.customer_user)
        response = client.get(reverse('portals:customer-dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            reverse('portals:customer-mock-landing', kwargs={'program': IELTS_SERVICE}),
        )
        self.assertContains(
            response,
            reverse('portals:customer-mock-landing', kwargs={'program': SAT_SERVICE}),
        )

    def test_customer_picker_includes_completed_program_without_credits(self):
        from portals.utils.customer_mock import get_customer_selectable_mock_programs

        attempt, error = start_customer_mock_test_attempt(self.customer.pk, IELTS_SERVICE)
        self.assertIsNone(error)
        attempt.status = IeltsMockTestAttempt.Status.COMPLETED
        attempt.completed_at = timezone.now()
        attempt.save(update_fields=['status', 'completed_at'])
        self.customer.ielts_mock_credits = 0
        self.customer.sat_mock_credits = 1
        self.customer.save(update_fields=['ielts_mock_credits', 'sat_mock_credits'])

        self.assertEqual(
            get_customer_selectable_mock_programs(self.customer.pk),
            [IELTS_SERVICE, SAT_SERVICE],
        )
        client = Client()
        _portal_client_login(client, self.customer_user)
        response = client.get(reverse('portals:customer-mock-picker'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'IELTS')
        self.assertContains(response, 'SAT')

    def test_mock_start_does_not_consume_credit_until_quiz_start(self):
        self.assertTrue(customer_can_start_mock(self.customer.pk))
        attempt, error = start_customer_mock_test_attempt(self.customer.pk, IELTS_SERVICE)
        self.assertIsNone(error)
        self.assertIsNotNone(attempt)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.ielts_mock_credits, 1)
        self.assertEqual(self.customer.sat_mock_credits, 0)
        self.assertFalse(attempt.credit_consumed)

        client = Client()
        _portal_client_login(client, self.customer_user)
        start_url = reverse('portals:customer-quiz-start', kwargs={'pk': attempt.listening_quiz_id})
        response = client.post(f'{start_url}?mock={attempt.pk}')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.mock_credits, 0)
        attempt.refresh_from_db()
        self.assertTrue(attempt.credit_consumed)

    def test_no_credit_blocks_start(self):
        self.customer.ielts_mock_credits = 0
        self.customer.sat_mock_credits = 0
        self.customer.save(update_fields=['ielts_mock_credits', 'sat_mock_credits'])
        self.assertFalse(customer_can_start_mock(self.customer.pk))
        attempt, error = start_customer_mock_test_attempt(self.customer.pk, IELTS_SERVICE)
        self.assertIsNone(attempt)
        self.assertIsNotNone(error)

    def test_mock_start_post_redirects_to_listening(self):
        client = Client()
        _portal_client_login(client, self.customer_user)
        response = client.post(reverse('portals:customer-ielts-mock-start'))
        self.assertEqual(response.status_code, 302)
        attempt = IeltsMockTestAttempt.objects.filter(customer=self.customer).first()
        self.assertIsNotNone(attempt)
        self.assertIn('mock=', response.url)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.ielts_mock_credits, 1)
        self.assertEqual(self.customer.sat_mock_credits, 0)

    def test_fulfill_mock_purchase_idempotent(self):
        payment = Payment.objects.create(
            transaction_id='tx-customer-mock-1',
            client_order_id='order-customer-mock-1',
            amount=self.package.price,
            status=Payment.Status.SUCCESS,
            product_type=Payment.ProductType.MOCK_TEST,
            course=self.mock_service,
            price_package=self.package,
            customer=self.customer,
            buyer_name='customer1',
            buyer_phone='+994501112233',
        )
        self.customer.ielts_mock_credits = 0
        self.customer.sat_mock_credits = 0
        self.customer.save(update_fields=['ielts_mock_credits', 'sat_mock_credits'])

        self.assertTrue(fulfill_mock_purchase(payment))
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.ielts_mock_credits, 1)
        self.assertEqual(self.customer.sat_mock_credits, 0)
        enrollment = CourseEnrollment.objects.get(payment=payment)
        self.assertEqual(enrollment.price_package_id, self.package.pk)
        self.assertEqual(enrollment.course_id, self.mock_service.pk)
        self.assertEqual(enrollment.customer_id, self.customer.pk)
        self.assertTrue(enrollment.contract_html)

        self.assertTrue(fulfill_mock_purchase(payment))
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.ielts_mock_credits, 1)
        self.assertEqual(self.customer.sat_mock_credits, 0)

    def test_student_mock_access_unchanged(self):
        attempt, error = start_mock_test_attempt(self.student.pk, 'ielts')
        self.assertIsNone(error)
        self.assertIsNotNone(attempt)
        self.assertEqual(attempt.student_id, self.student.pk)

    def test_customer_mock_cancel_get_redirects_without_abandon(self):
        client = Client()
        _portal_client_login(client, self.customer_user)
        attempt, _ = start_customer_mock_test_attempt(self.customer.pk, IELTS_SERVICE)
        listening_url = (
            reverse('portals:customer-manual-quiz-take', kwargs={'pk': attempt.listening_quiz_id})
            + f'?mock={attempt.pk}'
        )
        client.get(listening_url)
        cancel_url = (
            reverse('portals:customer-quiz-cancel', kwargs={'pk': attempt.listening_quiz_id})
            + f'?mock={attempt.pk}&next={reverse("portals:customer-ielts-mock")}'
        )
        response = client.get(cancel_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('portals:customer-ielts-mock'))
        attempt.refresh_from_db()
        self.assertEqual(attempt.status, IeltsMockTestAttempt.Status.IN_PROGRESS)

    def test_customer_mock_cancel_post_abandons_attempt(self):
        client = Client()
        _portal_client_login(client, self.customer_user)
        attempt, _ = start_customer_mock_test_attempt(self.customer.pk, IELTS_SERVICE)
        listening_url = (
            reverse('portals:customer-manual-quiz-take', kwargs={'pk': attempt.listening_quiz_id})
            + f'?mock={attempt.pk}'
        )
        client.get(listening_url)
        start_url = reverse('portals:customer-quiz-start', kwargs={'pk': attempt.listening_quiz_id})
        client.post(f'{start_url}?mock={attempt.pk}')
        cancel_url = (
            reverse('portals:customer-quiz-cancel', kwargs={'pk': attempt.listening_quiz_id})
            + f'?mock={attempt.pk}&next={reverse("portals:customer-ielts-mock")}'
        )
        response = client.post(cancel_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('portals:customer-ielts-mock'))
        attempt.refresh_from_db()
        self.assertEqual(attempt.status, IeltsMockTestAttempt.Status.ABANDONED)

    def test_customer_reading_submit_accepts_mock_in_json_body(self):
        client = Client()
        _portal_client_login(client, self.customer_user)
        attempt, _ = start_customer_mock_test_attempt(self.customer.pk, IELTS_SERVICE)
        reading = attempt.reading_quiz
        attempt.current_section = IeltsMockTestAttempt.Section.READING
        attempt.save(update_fields=['current_section'])
        question = ReadingQuestion.objects.filter(passage__quiz=reading).first()
        client.get(get_customer_mock_take_url(attempt, IeltsMockTestAttempt.Section.READING))
        start_url = reverse('portals:customer-quiz-start', kwargs={'pk': reading.pk})
        client.post(f'{start_url}?mock={attempt.pk}')

        submit_url = reverse('portals:customer-reading-quiz-submit', kwargs={'pk': reading.pk})
        response = client.post(
            submit_url,
            data=json.dumps({
                'mock': attempt.pk,
                'answers': {str(question.pk): 0},
                'duration_sec': 60,
                'completion_trigger': 'manual',
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload['success'])
        self.assertTrue(payload.get('mock_continue'))
        self.assertIn('next_url', payload)

    def test_customer_listening_submit_via_manual_endpoint(self):
        client = Client()
        _portal_client_login(client, self.customer_user)
        attempt, _ = start_customer_mock_test_attempt(self.customer.pk, IELTS_SERVICE)
        listening_url = (
            reverse('portals:customer-manual-quiz-take', kwargs={'pk': attempt.listening_quiz_id})
            + f'?mock={attempt.pk}'
        )
        client.get(listening_url)
        start_url = reverse('portals:customer-quiz-start', kwargs={'pk': attempt.listening_quiz_id})
        client.post(f'{start_url}?mock={attempt.pk}')

        question = ListeningQuestion.objects.filter(audio__quiz=attempt.listening_quiz).first()
        submit_url = reverse('portals:customer-manual-quiz-submit', kwargs={'pk': attempt.listening_quiz_id})
        response = client.post(
            submit_url,
            data={
                'mock': attempt.pk,
                'answers': {str(question.pk): 'Anna'},
                'duration_sec': 30,
                'completion_trigger': 'manual',
            },
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200, response.content)
        payload = response.json()
        self.assertTrue(payload['success'], payload.get('error'))
        self.assertTrue(payload.get('mock_continue'))

    def test_assigned_teacher_can_review_customer_quiz_result(self):
        from portals.models import QuizResult
        from portals.utils.student_courses import (
            teacher_can_review_quiz_result,
            teacher_can_see_customer_quiz_result,
        )

        writing = Quiz.objects.get(category=self.mock_writing_category, is_essay=True)
        result = QuizResult.objects.create(
            customer=self.customer,
            quiz=writing,
            student_submission='Sample writing response.',
        )
        self.assertTrue(
            teacher_can_see_customer_quiz_result(self.teacher.pk, self.customer.pk, writing)
        )
        self.assertFalse(
            teacher_can_see_customer_quiz_result(self.other_teacher.pk, self.customer.pk, writing)
        )
        self.assertTrue(teacher_can_review_quiz_result(self.teacher.pk, result))
        self.assertFalse(teacher_can_review_quiz_result(self.other_teacher.pk, result))


class CustomerProfileIntegrationTests(CustomerMockRoleTests):
    """End-to-end customer portal, mock flow, and access-control coverage."""

    def _login_client(self):
        client = Client()
        _portal_client_login(client, self.customer_user)
        return client

    def _post_json(self, client, url, payload):
        return client.post(url, data=json.dumps(payload), content_type='application/json')

    def _start_section(self, client, attempt, quiz_id):
        start_url = reverse('portals:customer-quiz-start', kwargs={'pk': quiz_id})
        return client.post(f'{start_url}?mock={attempt.pk}')

    def _open_section(self, client, attempt, section):
        url = get_customer_mock_take_url(attempt, section)
        return client.get(url)

    def _submit_listening(self, client, attempt):
        question = ListeningQuestion.objects.filter(audio__quiz=attempt.listening_quiz).first()
        submit_url = reverse('portals:customer-manual-quiz-submit', kwargs={'pk': attempt.listening_quiz_id})
        return self._post_json(
            client,
            submit_url,
            {
                'mock': attempt.pk,
                'answers': {str(question.pk): 'Anna'},
                'duration_sec': 30,
                'completion_trigger': 'manual',
            },
        )

    def _submit_reading(self, client, attempt):
        question = ReadingQuestion.objects.filter(passage__quiz=attempt.reading_quiz).first()
        submit_url = reverse('portals:customer-reading-quiz-submit', kwargs={'pk': attempt.reading_quiz_id})
        return self._post_json(
            client,
            submit_url,
            {
                'mock': attempt.pk,
                'answers': {str(question.pk): 0},
                'duration_sec': 30,
                'completion_trigger': 'manual',
            },
        )

    def _submit_writing(self, client, attempt):
        question = QuizQuestion.objects.filter(quiz=attempt.writing_quiz).first()
        submit_url = reverse('portals:customer-manual-quiz-submit', kwargs={'pk': attempt.writing_quiz_id})
        return self._post_json(
            client,
            submit_url,
            {
                'mock': attempt.pk,
                'answers': {str(question.pk): 'My essay answer.'},
                'duration_sec': 60,
                'completion_trigger': 'manual',
            },
        )

    def _submit_speaking(self, client, attempt):
        question = SpeakingQuestion.objects.filter(part__quiz=attempt.speaking_quiz).first()
        submit_url = reverse('portals:customer-speaking-quiz-submit', kwargs={'pk': attempt.speaking_quiz_id})
        audio = SimpleUploadedFile('answer.webm', b'fake-audio', content_type='audio/webm')
        return client.post(
            submit_url,
            data={
                'mock': str(attempt.pk),
                'duration_sec': '45',
                'completion_trigger': 'manual',
                f'recording_{question.pk}': audio,
            },
        )

    def test_customer_profile_default_mock_credit(self):
        user = User.objects.create_user(username='customer_default_credit', password='pass')
        profile = CustomerProfile.objects.create(user=user, phone='+994501119999')
        self.assertEqual(profile.mock_credits, 0)
        self.assertEqual(profile.ielts_mock_credits, 0)
        self.assertEqual(profile.sat_mock_credits, 0)

    def test_serialize_customer_includes_teacher(self):
        data = serialize_customer(self.customer)
        self.assertEqual(data['mock_credits'], 1)
        self.assertEqual(data['teacher_id'], self.teacher.pk)
        self.assertEqual(data['teacher_name'], self.teacher.full_name)
        self.assertEqual(data['full_name'], self.customer.full_name)

    def test_get_customer_profile_resolves_user(self):
        profile = get_customer_profile(self.customer_user)
        self.assertEqual(profile.pk, self.customer.pk)

    def test_student_cannot_access_customer_dashboard(self):
        client = Client()
        _portal_client_login(client, self.student_user)
        response = client.get(reverse('portals:customer-dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertNotEqual(response['Location'], reverse('portals:customer-dashboard'))

    def test_teacher_cannot_access_customer_mock_packages(self):
        client = Client()
        _portal_client_login(client, self.teacher_user)
        response = client.get(reverse('portals:customer-mock-packages'))
        self.assertEqual(response.status_code, 302)

    def test_customer_cannot_access_student_dashboard(self):
        client = self._login_client()
        response = client.get(reverse('portals:dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_customer_mock_landing_ok(self):
        client = self._login_client()
        response = client.get(reverse('portals:customer-ielts-mock'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('portals:customer-mock-start', kwargs={'program': IELTS_SERVICE}))

    def test_customer_mock_packages_lists_active_package(self):
        client = self._login_client()
        response = client.get(reverse('portals:customer-mock-packages'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.package.name_az)
        self.assertContains(
            response,
            reverse(
                'portals:customer-mock-payment-start',
                kwargs={'slug': self.mock_service.slug},
            ),
        )

    def test_customer_notifications_page_ok(self):
        client = self._login_client()
        response = client.get(reverse('portals:customer-notifications'))
        self.assertEqual(response.status_code, 200)

    def test_quiz_take_without_mock_redirects_to_dashboard(self):
        client = self._login_client()
        attempt, _ = start_customer_mock_test_attempt(self.customer.pk, IELTS_SERVICE)
        take_url = reverse('portals:customer-manual-quiz-take', kwargs={'pk': attempt.listening_quiz_id})
        response = client.get(take_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('portals:customer-dashboard'))

    def test_mock_start_with_zero_credits_redirects_to_packages(self):
        self.customer.ielts_mock_credits = 0
        self.customer.sat_mock_credits = 0
        self.customer.save(update_fields=['ielts_mock_credits', 'sat_mock_credits'])
        client = self._login_client()
        response = client.post(reverse('portals:customer-ielts-mock-start'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('portals:customer-mock-packages'))

    def test_customer_can_continue_in_progress_mock_with_zero_credits(self):
        attempt, _ = start_customer_mock_test_attempt(self.customer.pk, IELTS_SERVICE)
        self.customer.ielts_mock_credits = 0
        self.customer.sat_mock_credits = 0
        self.customer.save(update_fields=['ielts_mock_credits', 'sat_mock_credits'])
        self.assertTrue(customer_can_start_mock(self.customer.pk))
        self.assertTrue(customer_has_in_progress_mock(self.customer.pk))
        client = self._login_client()
        response = client.get(get_customer_mock_take_url(attempt, IeltsMockTestAttempt.Section.LISTENING))
        self.assertEqual(response.status_code, 200)

    def test_new_mock_start_abandons_previous_attempt(self):
        first, _ = start_customer_mock_test_attempt(self.customer.pk, IELTS_SERVICE)
        second, _ = start_customer_mock_test_attempt(self.customer.pk, IELTS_SERVICE)
        first.refresh_from_db()
        self.assertEqual(first.status, IeltsMockTestAttempt.Status.ABANDONED)
        self.assertEqual(second.status, IeltsMockTestAttempt.Status.IN_PROGRESS)

    def test_wrong_section_returns_not_found(self):
        client = self._login_client()
        attempt, _ = start_customer_mock_test_attempt(self.customer.pk, IELTS_SERVICE)
        reading_url = get_customer_mock_take_url(attempt, IeltsMockTestAttempt.Section.READING)
        response = client.get(reading_url)
        self.assertEqual(response.status_code, 404)

    def test_mock_complete_page_requires_completed_attempt(self):
        client = self._login_client()
        attempt, _ = start_customer_mock_test_attempt(self.customer.pk, IELTS_SERVICE)
        complete_url = reverse('portals:customer-ielts-mock-complete', kwargs={'pk': attempt.pk})
        response = client.get(complete_url)
        self.assertEqual(response.status_code, 404)

    def test_reading_start_does_not_consume_credit_again(self):
        client = self._login_client()
        attempt, _ = start_customer_mock_test_attempt(self.customer.pk, IELTS_SERVICE)
        self._open_section(client, attempt, IeltsMockTestAttempt.Section.LISTENING)
        self._start_section(client, attempt, attempt.listening_quiz_id)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.mock_credits, 0)
        self._submit_listening(client, attempt)
        attempt.refresh_from_db()
        self._open_section(client, attempt, IeltsMockTestAttempt.Section.READING)
        start_response = self._start_section(client, attempt, attempt.reading_quiz_id)
        self.assertEqual(start_response.status_code, 200)
        self.assertTrue(start_response.json()['success'])
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.mock_credits, 0)

    def test_listening_submit_advances_to_reading(self):
        client = self._login_client()
        attempt, _ = start_customer_mock_test_attempt(self.customer.pk, IELTS_SERVICE)
        self._open_section(client, attempt, IeltsMockTestAttempt.Section.LISTENING)
        self._start_section(client, attempt, attempt.listening_quiz_id)
        response = self._submit_listening(client, attempt)
        self.assertEqual(response.status_code, 200, response.content)
        payload = response.json()
        self.assertTrue(payload['success'], payload.get('error'))
        self.assertIn('reading', payload['next_url'])
        attempt.refresh_from_db()
        self.assertEqual(attempt.current_section, IeltsMockTestAttempt.Section.READING)

    def test_writing_submit_via_manual_endpoint(self):
        client = self._login_client()
        attempt, _ = start_customer_mock_test_attempt(self.customer.pk, IELTS_SERVICE)
        submit_listening_quiz_attempt(
            customer_id=self.customer.pk,
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
            customer_id=self.customer.pk,
            quiz_id=attempt.reading_quiz_id,
            given_answers={str(reading_question.pk): 0},
            mock_attempt_id=attempt.pk,
            defer_notifications=True,
        )
        attempt.refresh_from_db()
        self._open_section(client, attempt, IeltsMockTestAttempt.Section.WRITING)
        self._start_section(client, attempt, attempt.writing_quiz_id)
        response = self._submit_writing(client, attempt)
        self.assertEqual(response.status_code, 200, response.content)
        payload = response.json()
        self.assertTrue(payload['success'], payload.get('error'))
        self.assertTrue(payload.get('mock_continue'))
        attempt.refresh_from_db()
        self.assertEqual(attempt.current_section, IeltsMockTestAttempt.Section.SPEAKING)

    def test_full_customer_mock_flow_completes_all_sections(self):
        client = self._login_client()
        response = client.post(reverse('portals:customer-ielts-mock-start'))
        self.assertEqual(response.status_code, 302)
        attempt = IeltsMockTestAttempt.objects.get(customer=self.customer, status='in_progress')

        self._open_section(client, attempt, IeltsMockTestAttempt.Section.LISTENING)
        self._start_section(client, attempt, attempt.listening_quiz_id)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.mock_credits, 0)
        listening_response = self._submit_listening(client, attempt)
        self.assertTrue(listening_response.json()['success'], listening_response.content)

        attempt.refresh_from_db()
        self._open_section(client, attempt, IeltsMockTestAttempt.Section.READING)
        self._start_section(client, attempt, attempt.reading_quiz_id)
        reading_response = self._submit_reading(client, attempt)
        self.assertTrue(reading_response.json()['success'], reading_response.content)

        attempt.refresh_from_db()
        self._open_section(client, attempt, IeltsMockTestAttempt.Section.WRITING)
        self._start_section(client, attempt, attempt.writing_quiz_id)
        writing_response = self._submit_writing(client, attempt)
        self.assertTrue(writing_response.json()['success'], writing_response.content)

        attempt.refresh_from_db()
        self._open_section(client, attempt, IeltsMockTestAttempt.Section.SPEAKING)
        self._start_section(client, attempt, attempt.speaking_quiz_id)
        speaking_response = self._submit_speaking(client, attempt)
        self.assertEqual(speaking_response.status_code, 200, speaking_response.content)
        self.assertTrue(speaking_response.json()['success'], speaking_response.content)

        attempt.refresh_from_db()
        self.assertEqual(attempt.status, IeltsMockTestAttempt.Status.COMPLETED)
        self.assertIsNotNone(attempt.listening_result_id)
        self.assertIsNotNone(attempt.reading_result_id)
        self.assertIsNotNone(attempt.writing_result_id)
        self.assertIsNotNone(attempt.speaking_result_id)

        complete_url = reverse('portals:customer-ielts-mock-complete', kwargs={'pk': attempt.pk})
        complete_response = client.get(complete_url)
        self.assertEqual(complete_response.status_code, 200)

        dashboard_response = client.get(reverse('portals:customer-dashboard'))
        self.assertEqual(dashboard_response.status_code, 200)
        self.assertFalse(customer_has_in_progress_mock(self.customer.pk))

    def test_mock_completion_defers_customer_notifications_during_mock(self):
        client = self._login_client()
        client.post(reverse('portals:customer-ielts-mock-start'))
        attempt = IeltsMockTestAttempt.objects.get(customer=self.customer, status='in_progress')
        self._open_section(client, attempt, IeltsMockTestAttempt.Section.LISTENING)
        self._start_section(client, attempt, attempt.listening_quiz_id)
        self._submit_listening(client, attempt)
        attempt.refresh_from_db()
        self._open_section(client, attempt, IeltsMockTestAttempt.Section.READING)
        self._start_section(client, attempt, attempt.reading_quiz_id)
        self._submit_reading(client, attempt)
        attempt.refresh_from_db()
        self._open_section(client, attempt, IeltsMockTestAttempt.Section.WRITING)
        self._start_section(client, attempt, attempt.writing_quiz_id)
        self._submit_writing(client, attempt)
        attempt.refresh_from_db()
        self._open_section(client, attempt, IeltsMockTestAttempt.Section.SPEAKING)
        self._start_section(client, attempt, attempt.speaking_quiz_id)
        self._submit_speaking(client, attempt)
        attempt.refresh_from_db()

        self.assertEqual(attempt.status, IeltsMockTestAttempt.Status.COMPLETED)
        self.assertEqual(QuizResult.objects.filter(customer=self.customer).count(), 4)
        self.assertEqual(PortalNotification.objects.filter(customer=self.customer).count(), 0)

    def test_customer_quiz_results_belong_to_customer_not_student(self):
        client = self._login_client()
        client.post(reverse('portals:customer-ielts-mock-start'))
        attempt = IeltsMockTestAttempt.objects.get(customer=self.customer, status='in_progress')
        self._open_section(client, attempt, IeltsMockTestAttempt.Section.LISTENING)
        self._start_section(client, attempt, attempt.listening_quiz_id)
        self._submit_listening(client, attempt)
        result = QuizResult.objects.filter(customer=self.customer, quiz=attempt.listening_quiz).first()
        self.assertIsNotNone(result)
        self.assertIsNone(result.student_id)
        self.assertEqual(result.ielts_mock_attempt_id, attempt.pk)

    def test_teacher_review_publishes_customer_result_notification(self):
        from portals.utils.quiz_submit import submit_teacher_quiz_review

        writing = Quiz.objects.get(category=self.mock_writing_category, is_essay=True)
        result = QuizResult.objects.create(
            customer=self.customer,
            quiz=writing,
            student_submission='Essay text',
            total_score=None,
        )

        outcome = submit_teacher_quiz_review(
            teacher_id=self.teacher.pk,
            result_id=result.pk,
            total_score=7,
            teacher_feedback='Good work',
        )
        self.assertTrue(outcome['success'])
        self.assertTrue(
            PortalNotification.objects.filter(
                customer=self.customer,
                quiz_result=result,
                kind=PortalNotification.Kind.RESULT_PUBLISHED,
                is_read=False,
            ).exists()
        )
        client = self._login_client()
        notifications_response = client.get(reverse('portals:customer-notifications'))
        self.assertEqual(notifications_response.status_code, 200)
        score_detail_response = client.get(
            reverse('portals:customer-score-detail', kwargs={'result_pk': result.pk})
        )
        self.assertEqual(score_detail_response.status_code, 200)


class CustomerMockSectionTransitionAndCreditTests(CustomerProfileIntegrationTests):
    """Section-to-section flow and credit timing for customer mock tests."""

    def _assert_credits(self, expected: int):
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.mock_credits, expected)

    def _assert_credit_consumed(self, attempt, *, consumed: bool):
        attempt.refresh_from_db()
        self.assertEqual(attempt.credit_consumed, consumed)

    def _advance_through(self, client, attempt, through_section):
        """Start and submit sections in order up to and including through_section."""
        order = IeltsMockTestAttempt.SECTION_ORDER
        submitters = {
            IeltsMockTestAttempt.Section.LISTENING: self._submit_listening,
            IeltsMockTestAttempt.Section.READING: self._submit_reading,
            IeltsMockTestAttempt.Section.WRITING: self._submit_writing,
            IeltsMockTestAttempt.Section.SPEAKING: self._submit_speaking,
        }
        for section in order:
            self._open_section(client, attempt, section)
            quiz_id = attempt.quiz_for_section(section).pk
            start_response = self._start_section(client, attempt, quiz_id)
            self.assertEqual(start_response.status_code, 200, start_response.content)
            self.assertTrue(start_response.json()['success'], start_response.content)
            submit_response = submitters[section](client, attempt)
            self.assertEqual(submit_response.status_code, 200, submit_response.content)
            self.assertTrue(submit_response.json()['success'], submit_response.content)
            attempt.refresh_from_db()
            if section == through_section:
                break

    # --- Credit: only deducted when Listening quiz actually starts ---

    def test_credit_not_touched_on_mock_attempt_create(self):
        self._assert_credits(1)
        attempt, error = start_customer_mock_test_attempt(self.customer.pk, IELTS_SERVICE)
        self.assertIsNone(error)
        self._assert_credits(1)
        self._assert_credit_consumed(attempt, consumed=False)

    def test_credit_not_touched_on_http_mock_start_before_quiz(self):
        client = self._login_client()
        self._assert_credits(1)
        response = client.post(reverse('portals:customer-ielts-mock-start'))
        self.assertEqual(response.status_code, 302)
        attempt = IeltsMockTestAttempt.objects.get(customer=self.customer, status='in_progress')
        self._assert_credits(1)
        self._assert_credit_consumed(attempt, consumed=False)

    def test_credit_not_touched_opening_listening_page(self):
        client = self._login_client()
        attempt, _ = start_customer_mock_test_attempt(self.customer.pk, IELTS_SERVICE)
        response = self._open_section(client, attempt, IeltsMockTestAttempt.Section.LISTENING)
        self.assertEqual(response.status_code, 200)
        self._assert_credits(1)
        self._assert_credit_consumed(attempt, consumed=False)

    def test_credit_deducted_only_when_listening_quiz_starts(self):
        client = self._login_client()
        attempt, _ = start_customer_mock_test_attempt(self.customer.pk, IELTS_SERVICE)
        self._open_section(client, attempt, IeltsMockTestAttempt.Section.LISTENING)
        start_response = self._start_section(client, attempt, attempt.listening_quiz_id)
        self.assertEqual(start_response.status_code, 200)
        self.assertTrue(start_response.json()['success'])
        self._assert_credits(0)
        self._assert_credit_consumed(attempt, consumed=True)

    def test_credit_not_deducted_again_on_second_listening_start(self):
        client = self._login_client()
        attempt, _ = start_customer_mock_test_attempt(self.customer.pk, IELTS_SERVICE)
        self._start_section(client, attempt, attempt.listening_quiz_id)
        self._assert_credits(0)
        second_start = self._start_section(client, attempt, attempt.listening_quiz_id)
        self.assertEqual(second_start.status_code, 200)
        self.assertTrue(second_start.json()['success'])
        self._assert_credits(0)

    def test_credit_not_deducted_starting_reading_writing_speaking(self):
        client = self._login_client()
        attempt, _ = start_customer_mock_test_attempt(self.customer.pk, IELTS_SERVICE)
        self._open_section(client, attempt, IeltsMockTestAttempt.Section.LISTENING)
        self._start_section(client, attempt, attempt.listening_quiz_id)
        self._submit_listening(client, attempt)
        attempt.refresh_from_db()
        self._assert_credits(0)

        self._open_section(client, attempt, IeltsMockTestAttempt.Section.READING)
        reading_start = self._start_section(client, attempt, attempt.reading_quiz_id)
        self.assertEqual(reading_start.status_code, 200)
        self._assert_credits(0)
        self._submit_reading(client, attempt)
        attempt.refresh_from_db()

        self._open_section(client, attempt, IeltsMockTestAttempt.Section.WRITING)
        writing_start = self._start_section(client, attempt, attempt.writing_quiz_id)
        self.assertEqual(writing_start.status_code, 200)
        self._assert_credits(0)
        self._submit_writing(client, attempt)
        attempt.refresh_from_db()

        self._open_section(client, attempt, IeltsMockTestAttempt.Section.SPEAKING)
        speaking_start = self._start_section(client, attempt, attempt.speaking_quiz_id)
        self.assertEqual(speaking_start.status_code, 200)
        self._assert_credits(0)

    def test_credit_not_consumed_on_cancel_before_listening_start(self):
        client = self._login_client()
        attempt, _ = start_customer_mock_test_attempt(self.customer.pk, IELTS_SERVICE)
        self._open_section(client, attempt, IeltsMockTestAttempt.Section.LISTENING)
        cancel_url = (
            reverse('portals:customer-quiz-cancel', kwargs={'pk': attempt.listening_quiz_id})
            + f'?mock={attempt.pk}&next={reverse("portals:customer-ielts-mock")}'
        )
        client.post(cancel_url)
        self._assert_credits(1)
        self._assert_credit_consumed(attempt, consumed=False)

    def test_credit_not_refunded_after_consumption_and_abandon(self):
        client = self._login_client()
        attempt, _ = start_customer_mock_test_attempt(self.customer.pk, IELTS_SERVICE)
        self._open_section(client, attempt, IeltsMockTestAttempt.Section.LISTENING)
        self._start_section(client, attempt, attempt.listening_quiz_id)
        self._assert_credits(0)
        cancel_url = (
            reverse('portals:customer-quiz-cancel', kwargs={'pk': attempt.listening_quiz_id})
            + f'?mock={attempt.pk}&next={reverse("portals:customer-ielts-mock")}'
        )
        client.post(cancel_url)
        self._assert_credits(0)
        attempt.refresh_from_db()
        self.assertEqual(attempt.status, IeltsMockTestAttempt.Status.ABANDONED)
        self.assertTrue(attempt.credit_consumed)

    def test_consume_credit_rejects_non_listening_section_directly(self):
        attempt, _ = start_customer_mock_test_attempt(self.customer.pk, IELTS_SERVICE)
        ok, error = consume_customer_mock_credit_on_quiz_start(
            self.customer.pk,
            attempt.pk,
            attempt.reading_quiz_id,
        )
        self.assertFalse(ok)
        self.assertIsNotNone(error)
        self._assert_credits(1)
        self._assert_credit_consumed(attempt, consumed=False)

    # --- Section transitions ---

    def test_section_order_after_each_submit(self):
        client = self._login_client()
        attempt, _ = start_customer_mock_test_attempt(self.customer.pk, IELTS_SERVICE)
        expected_chain = list(IeltsMockTestAttempt.SECTION_ORDER)

        self._open_section(client, attempt, IeltsMockTestAttempt.Section.LISTENING)
        self._start_section(client, attempt, attempt.listening_quiz_id)
        listening_response = self._submit_listening(client, attempt)
        payload = listening_response.json()
        self.assertTrue(payload['success'])
        self.assertEqual(payload['mock_section_completed'], IeltsMockTestAttempt.Section.LISTENING)
        self.assertEqual(payload['mock_next_section'], expected_chain[1])
        attempt.refresh_from_db()
        self.assertEqual(attempt.current_section, expected_chain[1])

        self._open_section(client, attempt, expected_chain[1])
        self._start_section(client, attempt, attempt.quiz_for_section(expected_chain[1]).pk)
        reading_response = self._submit_reading(client, attempt)
        payload = reading_response.json()
        self.assertTrue(payload['success'])
        self.assertEqual(payload['mock_next_section'], expected_chain[2])
        attempt.refresh_from_db()
        self.assertEqual(attempt.current_section, expected_chain[2])

    def test_each_transition_next_url_points_to_following_section(self):
        client = self._login_client()
        attempt, _ = start_customer_mock_test_attempt(self.customer.pk, IELTS_SERVICE)
        transitions = [
            (self._submit_listening, IeltsMockTestAttempt.Section.READING, 'reading'),
            (self._submit_reading, IeltsMockTestAttempt.Section.WRITING, 'manual'),
            (self._submit_writing, IeltsMockTestAttempt.Section.SPEAKING, 'speaking'),
        ]
        self._open_section(client, attempt, IeltsMockTestAttempt.Section.LISTENING)
        self._start_section(client, attempt, attempt.listening_quiz_id)

        for submit_fn, next_section, url_fragment in transitions:
            attempt.refresh_from_db()
            response = submit_fn(client, attempt)
            payload = response.json()
            self.assertTrue(payload['success'], payload.get('error'))
            self.assertTrue(payload.get('mock_continue'))
            self.assertIn(url_fragment, payload['next_url'])
            attempt.refresh_from_db()
            self.assertEqual(attempt.current_section, next_section)
            self._open_section(client, attempt, next_section)
            self._start_section(client, attempt, attempt.quiz_for_section(next_section).pk)

    def test_final_section_submit_marks_mock_completed(self):
        client = self._login_client()
        attempt, _ = start_customer_mock_test_attempt(self.customer.pk, IELTS_SERVICE)
        self._advance_through(client, attempt, IeltsMockTestAttempt.Section.SPEAKING)
        attempt.refresh_from_db()
        self.assertEqual(attempt.status, IeltsMockTestAttempt.Status.COMPLETED)
        self.assertIsNone(NEXT_SECTION_BY_SECTION.get(IeltsMockTestAttempt.Section.SPEAKING))

    def test_cannot_submit_reading_while_listening_is_current(self):
        client = self._login_client()
        attempt, _ = start_customer_mock_test_attempt(self.customer.pk, IELTS_SERVICE)
        self._open_section(client, attempt, IeltsMockTestAttempt.Section.LISTENING)
        self._start_section(client, attempt, attempt.listening_quiz_id)
        question = ReadingQuestion.objects.filter(passage__quiz=attempt.reading_quiz).first()
        submit_url = reverse('portals:customer-reading-quiz-submit', kwargs={'pk': attempt.reading_quiz_id})
        response = self._post_json(
            client,
            submit_url,
            {
                'mock': attempt.pk,
                'answers': {str(question.pk): 0},
                'duration_sec': 30,
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])
        attempt.refresh_from_db()
        self.assertEqual(attempt.current_section, IeltsMockTestAttempt.Section.LISTENING)
        self.assertIsNone(attempt.reading_result_id)

    def test_cannot_submit_listening_twice(self):
        client = self._login_client()
        attempt, _ = start_customer_mock_test_attempt(self.customer.pk, IELTS_SERVICE)
        self._open_section(client, attempt, IeltsMockTestAttempt.Section.LISTENING)
        self._start_section(client, attempt, attempt.listening_quiz_id)
        first = self._submit_listening(client, attempt)
        self.assertTrue(first.json()['success'])
        attempt.refresh_from_db()
        second = self._submit_listening(client, attempt)
        self.assertEqual(second.status_code, 400)
        self.assertFalse(second.json()['success'])

    def test_future_section_page_not_accessible(self):
        client = self._login_client()
        attempt, _ = start_customer_mock_test_attempt(self.customer.pk, IELTS_SERVICE)
        for section in (
            IeltsMockTestAttempt.Section.READING,
            IeltsMockTestAttempt.Section.WRITING,
            IeltsMockTestAttempt.Section.SPEAKING,
        ):
            response = self._open_section(client, attempt, section)
            self.assertEqual(response.status_code, 404, section)

    def test_completed_mock_blocks_section_pages(self):
        client = self._login_client()
        attempt, _ = start_customer_mock_test_attempt(self.customer.pk, IELTS_SERVICE)
        self._advance_through(client, attempt, IeltsMockTestAttempt.Section.SPEAKING)
        attempt.refresh_from_db()
        complete_url = reverse('portals:customer-ielts-mock-complete', kwargs={'pk': attempt.pk})
        self.assertEqual(client.get(complete_url).status_code, 200)
        for section in IeltsMockTestAttempt.SECTION_ORDER:
            response = self._open_section(client, attempt, section)
            self.assertEqual(response.status_code, 404, section)

    def test_resolve_take_request_redirects_stale_section_url(self):
        attempt, _ = start_customer_mock_test_attempt(self.customer.pk, IELTS_SERVICE)
        ctx = resolve_customer_mock_take_request(
            self.customer.pk,
            attempt.pk,
            attempt.reading_quiz_id,
        )
        self.assertIn('mock_redirect', ctx)
        self.assertEqual(ctx['mock_redirect'], get_customer_mock_take_url(attempt, attempt.current_section))

    def test_validate_submit_rejects_out_of_order_section(self):
        attempt, _ = start_customer_mock_test_attempt(self.customer.pk, IELTS_SERVICE)
        error = validate_mock_section_submit(attempt, attempt.writing_quiz_id)
        self.assertIsNotNone(error)
        self.assertEqual(attempt.current_section, IeltsMockTestAttempt.Section.LISTENING)

    def _age_quiz_start_session(self, client, quiz_id, *, hours: int):
        cookie = client.cookies.get(PORTAL_COOKIE_NAME)
        if not cookie:
            raise AssertionError('Portal session cookie missing')
        store = PortalSessionStore(cookie.value)
        store[quiz_start_session_key(quiz_id)] = (
            timezone.now() - timedelta(hours=hours)
        ).isoformat()
        store.save()
        client.cookies[PORTAL_COOKIE_NAME] = store.session_key

    def test_timed_listening_submit_succeeds_after_quiz_restart_refreshes_session(self):
        client = self._login_client()
        attempt, _ = start_customer_mock_test_attempt(self.customer.pk, IELTS_SERVICE)
        listening = attempt.listening_quiz
        listening.is_time_limited = True
        listening.time_limit_minutes = 30
        listening.save(update_fields=['is_time_limited', 'time_limit_minutes'])

        start_url = reverse('portals:customer-quiz-start', kwargs={'pk': listening.pk})
        client.post(f'{start_url}?mock={attempt.pk}')
        self._age_quiz_start_session(client, listening.pk, hours=2)

        self._open_section(client, attempt, IeltsMockTestAttempt.Section.LISTENING)
        restart = client.post(f'{start_url}?mock={attempt.pk}')
        self.assertEqual(restart.status_code, 200)
        self.assertTrue(restart.json()['success'])

        submit_response = self._submit_listening(client, attempt)
        self.assertEqual(submit_response.status_code, 200, submit_response.content)
        payload = submit_response.json()
        self.assertTrue(payload['success'], payload.get('error'))
        self.assertNotEqual(payload.get('error'), 'Time limit exceeded.')

    def test_timed_reading_submit_uses_server_quiz_session(self):
        client = self._login_client()
        attempt, _ = start_customer_mock_test_attempt(self.customer.pk, IELTS_SERVICE)

        self._open_section(client, attempt, IeltsMockTestAttempt.Section.LISTENING)
        self._start_section(client, attempt, attempt.listening_quiz_id)
        listening_response = self._submit_listening(client, attempt)
        self.assertTrue(listening_response.json()['success'], listening_response.content)

        reading = attempt.reading_quiz
        reading.is_time_limited = True
        reading.time_limit_minutes = 60
        reading.save(update_fields=['is_time_limited', 'time_limit_minutes'])

        self._open_section(client, attempt, IeltsMockTestAttempt.Section.READING)
        start_url = reverse('portals:customer-quiz-start', kwargs={'pk': reading.pk})
        start_response = client.post(f'{start_url}?mock={attempt.pk}')
        self.assertEqual(start_response.status_code, 200)
        self.assertTrue(start_response.json()['success'])

        submit_response = self._submit_reading(client, attempt)
        self.assertEqual(submit_response.status_code, 200, submit_response.content)
        payload = submit_response.json()
        self.assertTrue(payload['success'], payload.get('error'))
        self.assertNotEqual(payload.get('error'), 'Quiz session expired. Open the quiz again and finish within the time limit.')

    def test_stale_quiz_timer_session_succeeds_after_restart_start(self):
        client = self._login_client()
        attempt, _ = start_customer_mock_test_attempt(self.customer.pk, IELTS_SERVICE)
        listening = attempt.listening_quiz
        listening.is_time_limited = True
        listening.time_limit_minutes = 30
        listening.save(update_fields=['is_time_limited', 'time_limit_minutes'])

        start_url = reverse('portals:customer-quiz-start', kwargs={'pk': listening.pk})
        client.post(f'{start_url}?mock={attempt.pk}')
        self._age_quiz_start_session(client, listening.pk, hours=2)

        self._open_section(client, attempt, IeltsMockTestAttempt.Section.LISTENING)
        client.post(f'{start_url}?mock={attempt.pk}')
        submit_response = self._submit_listening(client, attempt)
        self.assertEqual(submit_response.status_code, 200, submit_response.content)
        self.assertTrue(submit_response.json()['success'], submit_response.content)

    def test_resolve_duration_uses_client_elapsed_when_server_session_is_stale(self):
        from portals.utils.quiz_submit import _resolve_duration_sec

        listening = Quiz.objects.filter(is_listening=True).first()
        listening.is_time_limited = True
        listening.time_limit_minutes = 30
        listening.save(update_fields=['is_time_limited', 'time_limit_minutes'])

        stale_started_at = (timezone.now() - timedelta(hours=2)).isoformat()
        duration, error = _resolve_duration_sec(
            listening,
            client_duration_sec=90,
            session_started_at=stale_started_at,
            require_session=True,
        )
        self.assertIsNone(error)
        self.assertEqual(duration, 90)

    def test_resolve_duration_zero_client_ignores_stale_server_session(self):
        from portals.utils.quiz_submit import _resolve_duration_sec

        listening = Quiz.objects.filter(is_listening=True).first()
        listening.is_time_limited = True
        listening.time_limit_minutes = 30
        listening.save(update_fields=['is_time_limited', 'time_limit_minutes'])

        stale_started_at = (timezone.now() - timedelta(hours=2)).isoformat()
        duration, error = _resolve_duration_sec(
            listening,
            client_duration_sec=0,
            session_started_at=stale_started_at,
            require_session=True,
        )
        self.assertIsNone(error)
        self.assertEqual(duration, 0)


class CustomerSatMockTests(TestCase):
    def setUp(self):
        from portals.tests.test_quiz_visibility import _ensure_active_portal_services

        _ensure_active_portal_services()
        Service.objects.get_or_create(
            slug='sat',
            defaults={'name_az': 'SAT', 'name_en': 'SAT', 'is_active': True},
        )

        self.customer_user = User.objects.create_user(username='sat_customer', password='pass')
        self.customer = CustomerProfile.objects.create(
            user=self.customer_user,
            phone='+994501113333',
            sat_mock_credits=1,
        )
        self.sat_service = Service.objects.create(
            name_az='SAT Mock',
            slug='sat-mock-test',
            is_active=True,
            sat_mock_test=True,
        )
        self.sat_package = CoursePricePackage.objects.create(
            course=self.sat_service,
            name_az='1 SAT Mock',
            credits=1,
            price=Decimal('30.00'),
            is_active=True,
        )

        from portals.tests.group_helpers import create_quiz_category

        reading_category = create_quiz_category('SAT Reading and Writing', 'sat')
        math_category = create_quiz_category('SAT Math', 'sat')
        self.sat_reading_quiz = Quiz.objects.create(
            category=reading_category,
            topic='SAT RW Mock',
            is_sat=True,
            sat_section='reading',
        )
        QuizQuestion.objects.create(
            quiz=self.sat_reading_quiz,
            order=1,
            question='<p>Pick one.</p>',
            answer_options=['A', 'B'],
            correct_answer='A',
            correct_option_index=0,
        )
        self.sat_math_quiz = Quiz.objects.create(
            category=math_category,
            topic='SAT Math Mock',
            is_sat=True,
            sat_section='algebra',
        )
        QuizQuestion.objects.create(
            quiz=self.sat_math_quiz,
            order=1,
            question='<p>2 + 2 = ?</p>',
            answer_options=['3', '4'],
            correct_answer='4',
            correct_option_index=1,
        )

    def test_sat_fulfillment_adds_sat_credits_only(self):
        payment = Payment.objects.create(
            transaction_id='tx-sat-customer-1',
            client_order_id='order-sat-customer-1',
            amount=self.sat_package.price,
            status=Payment.Status.SUCCESS,
            product_type=Payment.ProductType.MOCK_TEST,
            course=self.sat_service,
            price_package=self.sat_package,
            customer=self.customer,
            buyer_name='sat_customer',
            buyer_phone='+994501113333',
        )
        self.customer.ielts_mock_credits = 0
        self.customer.sat_mock_credits = 0
        self.customer.save(update_fields=['ielts_mock_credits', 'sat_mock_credits'])

        self.assertTrue(fulfill_mock_purchase(payment))
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.ielts_mock_credits, 0)
        self.assertEqual(self.customer.sat_mock_credits, 1)

    def test_customer_sat_mock_start_uses_sat_credits(self):
        attempt, error = start_customer_mock_test_attempt(self.customer.pk, SAT_SERVICE)
        self.assertIsNone(error)
        self.assertEqual(attempt.exam_program, SAT_SERVICE)
        self.assertEqual(attempt.reading_quiz_id, self.sat_reading_quiz.pk)
        self.assertEqual(attempt.math_quiz_id, self.sat_math_quiz.pk)

    def test_customer_with_both_program_credits_sees_picker(self):
        self.customer.ielts_mock_credits = 1
        self.customer.save(update_fields=['ielts_mock_credits'])
        client = Client()
        _portal_client_login(client, self.customer_user)
        response = client.get(reverse('portals:customer-mock-picker'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('portals:customer-mock-landing', kwargs={'program': IELTS_SERVICE}))
        self.assertContains(response, reverse('portals:customer-mock-landing', kwargs={'program': SAT_SERVICE}))

    def test_customer_sat_mock_take_page_loads(self):
        attempt, error = start_customer_mock_test_attempt(self.customer.pk, SAT_SERVICE)
        self.assertIsNone(error)
        client = Client()
        _portal_client_login(client, self.customer_user)
        take_url = get_customer_mock_take_url(attempt, 'reading_writing')
        response = client.get(take_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'portals/student/quiz_take.html')
        self.assertIn('/take/', take_url)
        self.assertNotIn('/manual/', take_url)

    def test_customer_sat_mock_submit_advances_sections(self):
        attempt, error = start_customer_mock_test_attempt(self.customer.pk, SAT_SERVICE)
        self.assertIsNone(error)
        client = Client()
        _portal_client_login(client, self.customer_user)
        rw_question = self.sat_reading_quiz.questions.first()

        client.get(get_customer_mock_take_url(attempt, 'reading_writing'))
        start_url = reverse('portals:customer-quiz-start', kwargs={'pk': attempt.reading_quiz_id})
        self.assertEqual(client.post(f'{start_url}?mock={attempt.pk}').status_code, 200)

        submit_url = reverse('portals:customer-quiz-submit', kwargs={'pk': attempt.reading_quiz_id})
        response = client.post(
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
        self.assertEqual(data.get('mock_rest_seconds'), 10 * 60)
        self.assertEqual(data.get('mock_next_section'), 'math')

        attempt.refresh_from_db()
        self.assertEqual(attempt.current_section, 'math')

        math_question = self.sat_math_quiz.questions.first()
        client.get(get_customer_mock_take_url(attempt, 'math'))
        start_url = reverse('portals:customer-quiz-start', kwargs={'pk': attempt.math_quiz_id})
        self.assertEqual(client.post(f'{start_url}?mock={attempt.pk}').status_code, 200)

        response = client.post(
            reverse('portals:customer-quiz-submit', kwargs={'pk': attempt.math_quiz_id}),
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
