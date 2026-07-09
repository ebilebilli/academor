from unittest.mock import MagicMock

from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import RequestFactory, SimpleTestCase, TestCase

from portals.admin.admin_v1 import PortalUserAdmin
from portals.admin.filters import PortalRoleFilter
from portals.forms import (
    PORTAL_ROLE_ADMIN,
    PORTAL_ROLE_CUSTOMER,
    PORTAL_ROLE_STAFF,
    PORTAL_ROLE_STUDENT,
    PORTAL_ROLE_TEACHER,
    PortalUserCreationForm,
)
from portals.models import CustomerProfile, StudentProfile, TeacherProfile

User = get_user_model()


class PortalRoleFilterTests(TestCase):
    def setUp(self):
        self.admin_site = AdminSite()
        self.user_admin = PortalUserAdmin(User, self.admin_site)
        self.request = RequestFactory().get('/admin/auth/user/')

    def _filter(self, role):
        filter_ = PortalRoleFilter(self.request, {'portal_role': role}, User, self.user_admin)
        return set(filter_.queryset(self.request, User.objects.all()).values_list('pk', flat=True))

    def test_filters_by_teacher_role(self):
        teacher_user = User.objects.create_user(username='teacher_filter', password='pass')
        TeacherProfile.objects.create(user=teacher_user)
        student_user = User.objects.create_user(username='student_filter', password='pass')
        StudentProfile.objects.create(user=student_user)

        result = self._filter(PORTAL_ROLE_TEACHER)
        self.assertIn(teacher_user.pk, result)
        self.assertNotIn(student_user.pk, result)

    def test_superuser_matches_admin_not_teacher(self):
        admin_user = User.objects.create_superuser(username='admin_filter', password='pass')
        TeacherProfile.objects.create(user=admin_user)

        admin_result = self._filter(PORTAL_ROLE_ADMIN)
        teacher_result = self._filter(PORTAL_ROLE_TEACHER)
        self.assertIn(admin_user.pk, admin_result)
        self.assertNotIn(admin_user.pk, teacher_result)

    def test_staff_without_profile_matches_staff_role(self):
        staff_user = User.objects.create_user(username='staff_filter', password='pass', is_staff=True)
        result = self._filter(PORTAL_ROLE_STAFF)
        self.assertIn(staff_user.pk, result)

    def test_customer_profile_matches_customer_role(self):
        customer_user = User.objects.create_user(username='customer_filter', password='pass')
        CustomerProfile.objects.create(user=customer_user)

        result = self._filter(PORTAL_ROLE_CUSTOMER)
        self.assertIn(customer_user.pk, result)

    def test_user_without_role_matches_none(self):
        plain_user = User.objects.create_user(username='plain_filter', password='pass')
        result = self._filter('none')
        self.assertIn(plain_user.pk, result)


class PortalUserAdminSaveFormTests(SimpleTestCase):
    def test_add_user_calls_form_save_with_commit_true(self):
        admin = PortalUserAdmin(User, AdminSite())
        form = MagicMock()
        admin.save_form(MagicMock(), form, change=False)
        form.save.assert_called_once_with(commit=True)


class PortalUserCreationFormTests(TestCase):
    def test_commit_false_does_not_create_profile(self):
        form = PortalUserCreationForm(
            data={
                'username': 'student_commit_false',
                'password1': 'TestPass123!',
                'password2': 'TestPass123!',
                'portal_role': PORTAL_ROLE_STUDENT,
                'phone': '',
            },
        )
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save(commit=False)
        self.assertIsNone(user.pk)
        self.assertFalse(
            StudentProfile.objects.filter(user__username='student_commit_false').exists(),
        )

    def test_commit_true_creates_student_profile(self):
        form = PortalUserCreationForm(
            data={
                'username': 'student_commit_true',
                'password1': 'TestPass123!',
                'password2': 'TestPass123!',
                'portal_role': PORTAL_ROLE_STUDENT,
                'phone': '',
            },
        )
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save(commit=True)
        self.assertTrue(StudentProfile.objects.filter(user=user).exists())
        profile = StudentProfile.objects.get(user=user)
        self.assertEqual(profile.full_name, 'student_commit_true')

    def test_username_with_space_is_valid(self):
        form = PortalUserCreationForm(
            data={
                'username': 'Ali Mammadov',
                'password1': 'TestPass123!',
                'password2': 'TestPass123!',
                'portal_role': PORTAL_ROLE_STUDENT,
                'phone': '',
            },
        )
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save(commit=True)
        self.assertEqual(user.username, 'Ali Mammadov')
        self.assertEqual(StudentProfile.objects.get(user=user).full_name, 'Ali Mammadov')

    def test_commit_true_creates_customer_profile_with_default_credit(self):
        teacher = TeacherProfile.objects.create(
            user=User.objects.create_user(username='ielts_teacher', password='pass'),
            phone='+994501112233',
        )
        form = PortalUserCreationForm(
            data={
                'username': 'customer_default',
                'password1': 'TestPass123!',
                'password2': 'TestPass123!',
                'portal_role': PORTAL_ROLE_CUSTOMER,
                'phone': '+994501234567',
                'assigned_teacher': teacher.pk,
            },
        )
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save(commit=True)
        self.assertTrue(user.check_password('TestPass123!'))
        profile = CustomerProfile.objects.get(user=user)
        self.assertEqual(profile.mock_credits, 1)
        self.assertEqual(profile.phone, '+994501234567')
        self.assertEqual(profile.teacher_id, teacher.pk)
