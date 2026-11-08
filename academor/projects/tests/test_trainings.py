import re

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from projects.models import Service


def _grid_slugs(html):
    """Course slugs per service grid (<ul class="hsvc-grid">) in the page body, navbar excluded."""
    return [
        sorted(set(re.findall(r'/courses/([a-z0-9-]+)/', grid)))
        for grid in re.findall(r'class="hsvc-grid".*?</ul>', html, re.S)
    ]


class TrainingSplitTests(TestCase):
    def setUp(self):
        cache.clear()
        self.course = Service.objects.create(name_az='IELTS', slug='ielts-test', is_active=True, order=1)
        self.training = Service.objects.create(
            name_az='PMP Təlimi', slug='pmp-test', is_active=True, is_training=True, order=2,
        )

    def tearDown(self):
        cache.clear()

    def test_services_and_courses_pages_list_courses_only(self):
        for name in ('projects:services-page', 'projects:courses-page'):
            with self.subTest(page=name):
                html = self.client.get(reverse(name)).content.decode()
                self.assertEqual(_grid_slugs(html), [['ielts-test']])

    def test_trainings_page_lists_trainings_only(self):
        response = self.client.get(reverse('projects:trainings-page'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(_grid_slugs(response.content.decode()), [['pmp-test']])

    def test_home_shows_courses_and_trainings_in_two_groups(self):
        html = self.client.get(reverse('projects:home-page')).content.decode()
        self.assertEqual(_grid_slugs(html), [['ielts-test'], ['pmp-test']])
        self.assertIn(reverse('projects:trainings-page'), html)

    def test_home_has_no_trainings_group_without_trainings(self):
        self.training.is_training = False
        self.training.save()
        cache.clear()
        html = self.client.get(reverse('projects:home-page')).content.decode()
        self.assertEqual(_grid_slugs(html), [['ielts-test', 'pmp-test']])
        self.assertNotIn('hsvc-trainings-heading', html)

    def test_navbar_dropdown_has_two_groups(self):
        html = self.client.get(reverse('projects:about-page')).content.decode()
        menu = re.search(r'nav-courses-dropdown shadow-sm">(.*?)</div>\s*</div>', html, re.S).group(1)
        self.assertEqual(menu.count('nav-courses-dropdown__group'), 2)
        courses_part, trainings_part = menu.split('nav-courses-dropdown__group', 2)[1:]
        self.assertIn('/courses/ielts-test/', courses_part)
        self.assertNotIn('/courses/pmp-test/', courses_part)
        self.assertIn('/courses/pmp-test/', trainings_part)

    def test_training_detail_keeps_its_url(self):
        self.assertEqual(self.client.get(reverse('projects:course-detail', args=['pmp-test'])).status_code, 200)

    def test_a_mock_test_cannot_be_a_training(self):
        service = Service(name_az='IELTS Mock', is_training=True, ielts_mock_test=True)
        with self.assertRaises(ValidationError):
            service.clean()
