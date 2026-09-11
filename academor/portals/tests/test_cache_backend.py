"""Cache backend: Redis at runtime; DummyCache during tests.

@cached_query stores in django.core.cache (not a function-local memo). Redis
shares values across gunicorn workers. manage.py test uses DummyCache so the
suite does not share keys with the running app and cases stay independent.
"""
import os
from unittest.mock import patch

from django.core.cache import cache, caches
from django.test import SimpleTestCase, override_settings

from academor.cache_config import build_caches, redis_location
from portals.utils.cache_utils import cached_query


_SHARED = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'n20-shared',
    },
    'worker_b': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'n20-shared',
    },
    'isolated': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'n20-isolated',
    },
}


@override_settings(CACHES=_SHARED)
class CacheSharingTests(SimpleTestCase):
    """LocMem with the same LOCATION simulates Redis sharing for unit tests."""

    def setUp(self):
        caches.close_all()
        cache.clear()

    def tearDown(self):
        cache.clear()
        caches.close_all()

    def test_set_get_roundtrip(self):
        cache.set('n20-probe', {'ok': True}, 30)
        self.assertEqual(cache.get('n20-probe'), {'ok': True})

    def test_cached_query_values_are_shared(self):
        calls = {'n': 0}

        @cached_query(timeout=60)
        def expensive(student_id):
            calls['n'] += 1
            return {'student_id': student_id, 'rows': [1, 2, 3]}

        first = expensive(42)
        second = expensive(42)
        self.assertEqual(first, {'student_id': 42, 'rows': [1, 2, 3]})
        self.assertEqual(second, first)
        self.assertEqual(calls['n'], 1)

        cache.set('n20-share', 'from-worker-a', 30)
        self.assertEqual(caches['worker_b'].get('n20-share'), 'from-worker-a')
        self.assertIsNone(caches['isolated'].get('n20-share'))


class CacheConfigTests(SimpleTestCase):
    def test_redis_location_includes_password(self):
        url = redis_location(host='redis', port='6379', password='s3cret', db='1')
        self.assertEqual(url, 'redis://:s3cret@redis:6379/1')

    def test_redis_location_without_password(self):
        url = redis_location(host='redis', port='6379', password='', db='1')
        self.assertEqual(url, 'redis://redis:6379/1')

    def test_build_caches_uses_redis_when_host_set(self):
        env = {
            'REDIS_HOST': 'redis',
            'REDIS_PORT': '6379',
            'REDIS_PASSWORD': 's3cret',
            'REDIS_CACHE_DB': '1',
        }
        with patch.dict(os.environ, env, clear=False):
            cfg = build_caches(force_tests=False)
        self.assertEqual(cfg['default']['BACKEND'], 'django.core.cache.backends.redis.RedisCache')
        self.assertEqual(cfg['default']['LOCATION'], 'redis://:s3cret@redis:6379/1')

    def test_build_caches_requires_host_outside_tests(self):
        env = os.environ.copy()
        env.pop('REDIS_HOST', None)
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(ValueError):
                build_caches(force_tests=False)

    def test_build_caches_uses_dummy_during_tests(self):
        with patch.dict(os.environ, {'REDIS_HOST': 'redis'}, clear=False):
            cfg = build_caches(force_tests=True)
        self.assertEqual(
            cfg['default']['BACKEND'],
            'django.core.cache.backends.dummy.DummyCache',
        )
