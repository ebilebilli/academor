from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from payments.mock_customer import (
    find_customer_profile_by_phone,
    resolve_or_create_customer_for_mock_purchase,
)
from portals.models import CustomerProfile, StudentProfile

User = get_user_model()


class MockCustomerResolutionTests(TestCase):
    def test_creates_customer_profile_for_new_phone(self):
        profile = resolve_or_create_customer_for_mock_purchase(
            buyer_name='Ali Mammadov',
            buyer_phone='+994501119988',
            buyer_email='ali@example.com',
        )
        self.assertEqual(profile.phone, '+994501119988')
        self.assertEqual(profile.mock_credits, 0)
        self.assertTrue(profile.user.username.startswith('mock'))

    def test_reuses_existing_customer_by_phone(self):
        user = User.objects.create_user(username='existing_customer', password='pass')
        existing = CustomerProfile.objects.create(user=user, phone='+994501112233')
        profile = resolve_or_create_customer_for_mock_purchase(
            buyer_name='Existing',
            buyer_phone='0501112233',
        )
        self.assertEqual(profile.pk, existing.pk)

    def test_rejects_phone_used_by_student(self):
        user = User.objects.create_user(username='student1', password='pass')
        StudentProfile.objects.create(user=user, phone='+994501112233')
        with self.assertRaises(Exception):
            resolve_or_create_customer_for_mock_purchase(
                buyer_name='Blocked',
                buyer_phone='+994501112233',
            )

    def test_find_customer_normalizes_az_phone(self):
        user = User.objects.create_user(username='cust1', password='pass')
        CustomerProfile.objects.create(user=user, phone='+994501112233')
        found = find_customer_profile_by_phone('0501112233')
        self.assertIsNotNone(found)
        self.assertEqual(found.pk, user.customer_profile.pk)
