"""Quiz submit errors must keep a language-stable code (L4)."""
import json

from django.test import SimpleTestCase
from django.utils.translation import override

from portals.utils.quiz_submit import ERROR_QUIZ_NOT_FOUND, quiz_not_found_result
from portals.views.quiz_views import _submit_json_response


class QuizNotFoundErrorCodeTests(SimpleTestCase):
    def test_error_code_is_stable_across_languages(self):
        with override('az'):
            az = quiz_not_found_result()
        with override('en'):
            en = quiz_not_found_result()
        with override('ru'):
            ru = quiz_not_found_result()

        self.assertEqual(az['error_code'], ERROR_QUIZ_NOT_FOUND)
        self.assertEqual(en['error_code'], ru['error_code'])
        self.assertEqual(az['error_code'], en['error_code'])
        self.assertNotEqual(az['error'], 'Quiz not found.')
        self.assertNotEqual(ru['error'], 'Quiz not found.')

    def test_submit_json_uses_code_not_english_literal(self):
        with override('az'):
            response = _submit_json_response(quiz_not_found_result())
        self.assertEqual(response.status_code, 404)
        payload = json.loads(response.content.decode())
        self.assertEqual(payload['error_code'], ERROR_QUIZ_NOT_FOUND)
        self.assertNotEqual(payload['error'], 'Quiz not found.')
