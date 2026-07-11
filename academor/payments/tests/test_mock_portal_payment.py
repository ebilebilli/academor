from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from payments.mock_fulfillment import fulfill_mock_purchase
from payments.models import Payment
from payments.views import _is_existing_portal_customer_payment
from portals.models import CustomerProfile
from portals.tests.test_quiz_submit import _portal_client_login
from projects.models import CoursePricePackage, Service

User = get_user_model()


class PortalMockPaymentStartTests(TestCase):
    def setUp(self):
        self.mock_service = Service.objects.create(
            name_az='IELTS Mock',
            slug='ielts-mock-test',
            is_active=True,
            ielts_mock_test=True,
        )
        self.package = CoursePricePackage.objects.create(
            course=self.mock_service,
            name_az='1 Mock',
            credits=2,
            price=Decimal('25.00'),
            is_active=True,
        )
        self.customer_user = User.objects.create_user(username='customer1', password='pass')
        self.customer = CustomerProfile.objects.create(
            user=self.customer_user,
            phone='+994501112233',
            ielts_mock_credits=0,
        )
        self.client = Client()
        _portal_client_login(self.client, self.customer_user)

    @patch('payments.views.create_transaction')
    def test_portal_customer_can_start_mock_payment_without_contract_form(self, create_transaction):
        create_transaction.return_value = {
            'ok': True,
            'transaction_id': 'tx-portal-mock-1',
            'payment_url': 'https://pay.example/checkout/1',
        }
        url = reverse(
            'portals:customer-mock-payment-start',
            kwargs={'slug': self.mock_service.slug},
        )
        response = self.client.post(url, {'price_package_id': self.package.pk})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'https://pay.example/checkout/1')

        payment = Payment.objects.get()
        self.assertEqual(payment.customer_id, self.customer.pk)
        self.assertEqual(payment.product_type, Payment.ProductType.MOCK_TEST)
        self.assertEqual(payment.price_package_id, self.package.pk)
        self.assertTrue(payment.contract_number)
        self.assertEqual(payment.buyer_name, self.customer.full_name)

    @patch('payments.views.create_transaction')
    def test_fulfilled_portal_payment_adds_credits(self, create_transaction):
        create_transaction.return_value = {
            'ok': True,
            'transaction_id': 'tx-portal-mock-2',
            'payment_url': 'https://pay.example/checkout/2',
        }
        url = reverse(
            'portals:customer-mock-payment-start',
            kwargs={'slug': self.mock_service.slug},
        )
        self.client.post(url, {'price_package_id': self.package.pk})
        payment = Payment.objects.get()
        payment.status = Payment.Status.SUCCESS
        payment.save(update_fields=['status', 'updated_at'])

        self.assertTrue(fulfill_mock_purchase(payment))
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.ielts_mock_credits, 2)

    def test_public_payment_url_still_requires_contract_form(self):
        client = Client()
        url = reverse('payment_start_course', kwargs={'slug': self.mock_service.slug})
        response = client.post(url, {'price_package_id': self.package.pk})
        self.assertEqual(response.status_code, 302)
        self.assertIn('mock-tests', response['Location'])
        self.assertFalse(Payment.objects.exists())

    def test_existing_portal_customer_payment_detection(self):
        payment = Payment.objects.create(
            transaction_id='tx-detect-1',
            client_order_id='order-detect-1',
            amount=self.package.price,
            status=Payment.Status.SUCCESS,
            product_type=Payment.ProductType.MOCK_TEST,
            course=self.mock_service,
            price_package=self.package,
            customer=self.customer,
            buyer_name='customer1',
            buyer_phone='+994501112233',
        )
        self.assertTrue(_is_existing_portal_customer_payment(payment))

        public_user = User.objects.create_user(username='mock501112233', password='pass')
        public_customer = CustomerProfile.objects.create(
            user=public_user,
            phone='+994501119999',
        )
        public_payment = Payment.objects.create(
            transaction_id='tx-detect-2',
            client_order_id='order-detect-2',
            amount=self.package.price,
            status=Payment.Status.SUCCESS,
            product_type=Payment.ProductType.MOCK_TEST,
            course=self.mock_service,
            price_package=self.package,
            customer=public_customer,
            buyer_name='Ali',
            buyer_phone='+994501119999',
        )
        self.assertFalse(_is_existing_portal_customer_payment(public_payment))
