from types import SimpleNamespace

from django.test import SimpleTestCase

from portals.utils.portal_services import infer_course_type_for_service


class InferCourseTypeForServiceTests(SimpleTestCase):
    def _service(self, **kwargs):
        defaults = {
            'slug': '',
            'name_az': '',
            'name_en': '',
            'name_ru': '',
        }
        defaults.update(kwargs)
        return SimpleNamespace(**defaults)

    def test_conversation_club_is_not_sat(self):
        service = self._service(
            slug='conversation-club',
            name_en='Conversation Club',
            name_az='Conversation Club',
        )
        self.assertIsNone(infer_course_type_for_service(service))

    def test_sat_slug_maps_to_sat(self):
        service = self._service(slug='sat', name_en='SAT')
        self.assertEqual(infer_course_type_for_service(service), 'sat')

    def test_sat_prep_slug_maps_to_sat(self):
        service = self._service(slug='sat-prep', name_en='SAT Prep')
        self.assertEqual(infer_course_type_for_service(service), 'sat')

    def test_ielts_and_general_english(self):
        self.assertEqual(
            infer_course_type_for_service(self._service(slug='ielts-course')),
            'ielts',
        )
        self.assertEqual(
            infer_course_type_for_service(self._service(slug='general-english')),
            'general_english',
        )
