"""Tests for separate portal/admin session cookies.

With portal_sessionid (for /portal/*) and sessionid (for admin),
sessions are completely independent.
"""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import Client, RequestFactory, TestCase, override_settings

from portals.middleware import PortalSessionMiddleware, PortalAuthenticationMiddleware
from portals.models import StudentProfile
from portals.utils.portal_session import (
    PORTAL_COOKIE_NAME,
    PORTAL_SESSION_USER_KEY,
    PortalSessionStore,
    get_portal_user_id,
    get_portal_user,
    is_portal_authenticated,
    portal_login,
    portal_logout,
)

User = get_user_model()


@override_settings(
    PORTAL_SESSION_COOKIE_NAME='portal_sessionid',
    PORTAL_SESSION_COOKIE_PATH='/portal/',
)
class SeparateCookieSessionTests(TestCase):
    """Test that portal and admin use completely separate cookies."""

    def setUp(self):
        self.client = Client()
        self.portal_user = User.objects.create_user(
            username='portal_student',
            password='TestPass123!',
        )
        StudentProfile.objects.create(
            user=self.portal_user,
        )
        self.admin_user = User.objects.create_user(
            username='staff_admin',
            password='TestPass123!',
            is_staff=True,
        )
        self.factory = RequestFactory()

    def test_portal_login_sets_separate_cookie(self):
        """Portal login should set portal_sessionid cookie, not touch sessionid."""
        request = self.factory.get('/portal/')
        request.COOKIES = {}

        # Simulate login
        portal_login(request, self.portal_user)

        # Response processing
        middleware = PortalSessionMiddleware(lambda r: HttpResponse())
        response = middleware(request)

        # Check portal cookie is set
        self.assertIn(PORTAL_COOKIE_NAME, response.cookies)
        portal_cookie = response.cookies[PORTAL_COOKIE_NAME]
        self.assertEqual(portal_cookie['path'], '/portal/')

    def test_portal_logout_deletes_portal_cookie(self):
        """Portal logout should delete portal_sessionid, not sessionid."""
        # First login
        request = self.factory.get('/portal/')
        request.COOKIES = {}
        portal_login(request, self.portal_user)

        middleware = PortalSessionMiddleware(lambda r: HttpResponse())
        response = middleware(request)
        portal_session_key = response.cookies[PORTAL_COOKIE_NAME].value

        # Now logout
        request2 = self.factory.get('/portal/logout/')
        request2.COOKIES = {PORTAL_COOKIE_NAME: portal_session_key}
        portal_logout(request2)

        response2 = middleware(request2)

        # Check portal cookie is deleted
        self.assertIn(PORTAL_COOKIE_NAME, response2.cookies)
        portal_cookie = response2.cookies[PORTAL_COOKIE_NAME]
        self.assertEqual(portal_cookie.value, '')

    def test_admin_session_unchanged_by_portal_login(self):
        """Admin session cookie should be untouched when portal user logs in."""
        # Admin login first (simulated via client)
        self.client.login(username='staff_admin', password='TestPass123!')
        admin_session_key = self.client.session.session_key

        # Portal login via separate cookie
        request = self.factory.get('/portal/')
        request.COOKIES = {settings.SESSION_COOKIE_NAME: admin_session_key}
        portal_login(request, self.portal_user)

        middleware = PortalSessionMiddleware(lambda r: HttpResponse())
        response = middleware(request)

        # Both cookies exist
        self.assertIn(PORTAL_COOKIE_NAME, response.cookies)
        self.assertIn(settings.SESSION_COOKIE_NAME, self.client.cookies)

    def test_portal_user_id_from_cookie(self):
        """get_portal_user_id should read from portal_sessionid cookie."""
        # Create session
        store = PortalSessionStore()
        store[PORTAL_SESSION_USER_KEY] = self.portal_user.pk
        store.save()

        # Request with cookie
        request = self.factory.get('/portal/')
        request.COOKIES = {PORTAL_COOKIE_NAME: store.session_key}

        user_id = get_portal_user_id(request)
        self.assertEqual(user_id, self.portal_user.pk)

    def test_is_portal_authenticated_from_cookie(self):
        """is_portal_authenticated should check portal_sessionid cookie."""
        store = PortalSessionStore()
        store[PORTAL_SESSION_USER_KEY] = self.portal_user.pk
        store.save()

        request = self.factory.get('/portal/')
        request.COOKIES = {PORTAL_COOKIE_NAME: store.session_key}

        self.assertTrue(is_portal_authenticated(request))

        # No cookie
        request2 = self.factory.get('/portal/')
        request2.COOKIES = {}
        self.assertFalse(is_portal_authenticated(request2))

    def test_get_portal_user_from_cookie(self):
        """get_portal_user should return user from portal session."""
        store = PortalSessionStore()
        store[PORTAL_SESSION_USER_KEY] = self.portal_user.pk
        store.save()

        request = self.factory.get('/portal/')
        request.COOKIES = {PORTAL_COOKIE_NAME: store.session_key}

        user = get_portal_user(request)
        self.assertEqual(user.pk, self.portal_user.pk)

    def test_both_sessions_independent(self):
        """Admin and portal can be logged in simultaneously with different users."""
        # Setup: Admin logged in (sessionid cookie)
        self.client.login(username='staff_admin', password='TestPass123!')

        # Setup: Portal user logged in (portal_sessionid cookie)
        store = PortalSessionStore()
        store[PORTAL_SESSION_USER_KEY] = self.portal_user.pk
        store.save()

        # Simulate request with both cookies
        request = self.factory.get('/portal/')
        request.COOKIES = {
            settings.SESSION_COOKIE_NAME: self.client.session.session_key,
            PORTAL_COOKIE_NAME: store.session_key,
        }

        # Portal user should be portal_user
        portal_user = get_portal_user(request)
        self.assertEqual(portal_user.pk, self.portal_user.pk)

        # Django's request.user should be admin_user (via AuthenticationMiddleware)
        # (In real scenario, but here we just test portal isolation)

    def test_admin_logout_does_not_affect_portal(self):
        """Admin logout (sessionid) should not clear portal_sessionid."""
        # Portal login
        store = PortalSessionStore()
        store[PORTAL_SESSION_USER_KEY] = self.portal_user.pk
        store.save()

        # Admin logout simulation
        self.client.logout()  # This clears Django session

        # Portal session should still be valid
        request = self.factory.get('/portal/')
        request.COOKIES = {PORTAL_COOKIE_NAME: store.session_key}

        self.assertTrue(is_portal_authenticated(request))
        self.assertEqual(get_portal_user_id(request), self.portal_user.pk)


@override_settings(
    PORTAL_SESSION_COOKIE_NAME='portal_sessionid',
    PORTAL_SESSION_COOKIE_PATH='/portal/',
)
class PortalAuthenticationMiddlewareTests(TestCase):
    """Test PortalAuthenticationMiddleware with separate cookies."""

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='portal_test',
            password='TestPass123!',
        )
        StudentProfile.objects.create(user=self.user)

    def test_portal_user_attached_from_cookie(self):
        """Middleware should attach portal_user from portal_sessionid cookie."""
        store = PortalSessionStore()
        store[PORTAL_SESSION_USER_KEY] = self.user.pk
        store.save()

        request = self.factory.get('/portal/dashboard/')
        request.COOKIES = {PORTAL_COOKIE_NAME: store.session_key}

        middleware = PortalAuthenticationMiddleware(lambda r: r)
        middleware(request)

        self.assertEqual(request.portal_user.pk, self.user.pk)

    def test_anonymous_when_no_portal_cookie(self):
        """Middleware should attach AnonymousUser when no portal cookie."""
        request = self.factory.get('/portal/dashboard/')
        request.COOKIES = {}  # No portal cookie

        middleware = PortalAuthenticationMiddleware(lambda r: r)
        middleware(request)

        self.assertFalse(request.portal_user.is_authenticated)


@override_settings(
    PORTAL_SESSION_COOKIE_NAME='portal_sessionid',
    PORTAL_SESSION_COOKIE_PATH='/portal/',
)
class PortalSessionMiddlewareTests(TestCase):
    """Test PortalSessionMiddleware cookie handling."""

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='test', password='pass')

    def test_sets_cookie_on_login(self):
        """Middleware should set portal_sessionid cookie after login."""
        request = self.factory.post('/portal/login/')
        request.COOKIES = {}

        portal_login(request, self.user)

        def get_response(r):
            return HttpResponse()

        middleware = PortalSessionMiddleware(get_response)
        response = middleware(request)

        self.assertIn(PORTAL_COOKIE_NAME, response.cookies)
        cookie = response.cookies[PORTAL_COOKIE_NAME]
        self.assertTrue(cookie.value)  # Has session key
        self.assertEqual(cookie['path'], '/portal/')
        self.assertTrue(cookie['httponly'])

    def test_deletes_cookie_on_logout(self):
        """Middleware should delete portal_sessionid cookie after logout."""
        request = self.factory.get('/portal/logout/')
        request.COOKIES = {}

        portal_logout(request)

        def get_response(r):
            return HttpResponse()

        middleware = PortalSessionMiddleware(get_response)
        response = middleware(request)

        self.assertIn(PORTAL_COOKIE_NAME, response.cookies)
        cookie = response.cookies[PORTAL_COOKIE_NAME]
        self.assertEqual(cookie.value, '')  # Deleted

    def test_cookie_path_restriction(self):
        """Portal cookie should only be sent to /portal/* paths."""
        request = self.factory.get('/portal/')
        request.COOKIES = {}
        portal_login(request, self.user)

        def get_response(r):
            return HttpResponse()

        middleware = PortalSessionMiddleware(get_response)
        response = middleware(request)

        cookie = response.cookies[PORTAL_COOKIE_NAME]
        self.assertEqual(cookie['path'], '/portal/')
