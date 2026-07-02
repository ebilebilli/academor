from unittest.mock import MagicMock

from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase

from portals.admin.admin_v1 import PortalUserAdmin
from portals.forms import PORTAL_ROLE_STUDENT, PortalUserCreationForm
from portals.models import StudentProfile

User = get_user_model()


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
