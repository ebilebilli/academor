from decimal import Decimal

from django.test import TestCase

from payments.enrollment import fulfill_course_enrollment
from payments.models import Payment
from projects.models import CoursePricePackage, Service


class CourseEnrollmentContractTests(TestCase):
    def test_bron_price_package_renders_bron_contract(self):
        service = Service.objects.create(
            name_az='IELTS Kursu',
            slug='ielts-kursu-bron',
            is_active=True,
        )
        package = CoursePricePackage.objects.create(
            course=service,
            name_az='Bron paket',
            months=1,
            lesson_count=8,
            lesson_minutes=90,
            price=Decimal('120.00'),
            is_active=True,
            is_bron=True,
        )
        payment = Payment.objects.create(
            transaction_id='tx-course-bron-1',
            client_order_id='order-course-bron-1',
            amount=package.price,
            status=Payment.Status.SUCCESS,
            product_type=Payment.ProductType.COURSE,
            course=service,
            price_package=package,
            buyer_name='Ali Vəliyev',
            buyer_phone='+994501112244',
            contract_number='2026-999001',
        )

        enrollment = fulfill_course_enrollment(payment)

        self.assertIsNotNone(enrollment)
        self.assertIn('Bron Müqaviləsi', enrollment.contract_html)
        self.assertNotIn('Training agreement', enrollment.contract_html)
