from decimal import Decimal

from django.contrib.auth import get_user_model
from django.http import QueryDict
from django.test import TestCase

from payments.admin import CourseEnrollmentAdmin
from payments.admin_filters import EnrollmentCourseFilter, EnrollmentProductTypeFilter
from payments.mock_fulfillment import fulfill_mock_purchase
from payments.models import CourseEnrollment, Payment
from portals.models import CustomerProfile
from projects.models import CoursePricePackage, Service

User = get_user_model()


class MockEnrollmentAdminFilterTests(TestCase):
    def setUp(self):
        self.mock_service = Service.objects.create(
            name_az='IELTS Mock',
            slug='ielts-mock',
            is_active=True,
            ielts_mock_test=True,
        )
        self.package = CoursePricePackage.objects.create(
            course=self.mock_service,
            name_az='Mock paket',
            credits=2,
            price=Decimal('20.00'),
            is_active=True,
        )
        self.customer_user = User.objects.create_user(username='cust_filter', password='pass')
        self.customer = CustomerProfile.objects.create(
            user=self.customer_user,
            phone='+994501112244',
        )

    def _mock_payment(self, tx_suffix: str) -> Payment:
        return Payment.objects.create(
            transaction_id=f'tx-mock-filter-{tx_suffix}',
            client_order_id=f'order-mock-filter-{tx_suffix}',
            amount=self.package.price,
            status=Payment.Status.SUCCESS,
            product_type=Payment.ProductType.MOCK_TEST,
            course=self.mock_service,
            price_package=self.package,
            customer=self.customer,
            buyer_name='Ali',
            buyer_phone='+994501112244',
            contract_number='2026-654321',
        )

    def test_fulfill_mock_purchase_creates_course_enrollment(self):
        payment = self._mock_payment('1')
        self.assertTrue(fulfill_mock_purchase(payment))
        enrollment = CourseEnrollment.objects.get(payment=payment)
        self.assertEqual(enrollment.price_package_id, self.package.pk)
        self.assertEqual(enrollment.course_id, self.mock_service.pk)
        self.assertTrue(enrollment.contract_html)
        self.assertIn('2026-654321', enrollment.contract_html)

    def test_product_type_filter_splits_mock_and_course(self):
        course = Service.objects.create(name_az='IELTS kurs', slug='ielts-kurs', is_active=True)
        course_payment = Payment.objects.create(
            transaction_id='tx-course-filter-1',
            client_order_id='order-course-filter-1',
            amount=Decimal('100.00'),
            status=Payment.Status.SUCCESS,
            product_type=Payment.ProductType.COURSE,
            course=course,
            buyer_name='Course buyer',
            buyer_phone='+994501112255',
        )
        CourseEnrollment.objects.create(
            payment=course_payment,
            course=course,
            buyer_name='Course buyer',
            buyer_phone='+994501112255',
        )
        mock_payment = self._mock_payment('2')
        fulfill_mock_purchase(mock_payment)
        CourseEnrollment.objects.get(payment=mock_payment)

        product_params = QueryDict(mutable=True)
        product_params['product_type'] = Payment.ProductType.MOCK_TEST
        product_filter = EnrollmentProductTypeFilter(
            None,
            product_params,
            CourseEnrollment,
            CourseEnrollmentAdmin,
        )
        mock_ids = set(
            product_filter.queryset(None, CourseEnrollment.objects.all()).values_list('pk', flat=True)
        )
        self.assertIn(CourseEnrollment.objects.get(payment=mock_payment).pk, mock_ids)
        self.assertNotIn(CourseEnrollment.objects.get(payment=course_payment).pk, mock_ids)

        course_params = QueryDict(mutable=True)
        course_params['course'] = str(course.pk)
        course_filter = EnrollmentCourseFilter(
            None,
            course_params,
            CourseEnrollment,
            CourseEnrollmentAdmin,
        )
        course_ids = set(course_filter.queryset(None, CourseEnrollment.objects.all()).values_list('pk', flat=True))
        self.assertIn(CourseEnrollment.objects.get(payment=course_payment).pk, course_ids)
        self.assertNotIn(CourseEnrollment.objects.get(payment=mock_payment).pk, course_ids)

    def test_fulfill_sat_mock_purchase_adds_sat_mock_credits(self):
        sat_service = Service.objects.create(
            name_az='SAT Mock',
            slug='sat-mock-enroll',
            is_active=True,
            sat_mock_test=True,
        )
        sat_package = CoursePricePackage.objects.create(
            course=sat_service,
            name_az='SAT paket',
            credits=3,
            price=Decimal('45.00'),
            is_active=True,
        )
        payment = Payment.objects.create(
            transaction_id='tx-sat-mock-enroll-1',
            client_order_id='order-sat-mock-enroll-1',
            amount=sat_package.price,
            status=Payment.Status.SUCCESS,
            product_type=Payment.ProductType.MOCK_TEST,
            course=sat_service,
            price_package=sat_package,
            customer=self.customer,
            buyer_name='Ali',
            buyer_phone='+994501112244',
        )
        self.assertTrue(fulfill_mock_purchase(payment))
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.ielts_mock_credits, 0)
        self.assertEqual(self.customer.sat_mock_credits, 3)
