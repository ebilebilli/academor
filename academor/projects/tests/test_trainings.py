import re
from html.parser import HTMLParser

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


class _NavParentFinder(HTMLParser):
    """Records the classes of the open <div>s around each link (to catch unbalanced markup)."""

    def __init__(self):
        super().__init__()
        self.stack = []
        self.parents = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'div':
            self.stack.append(attrs.get('class') or '')
        elif tag == 'a' and attrs.get('href'):
            self.parents.setdefault(attrs['href'], list(self.stack))

    def handle_endtag(self, tag):
        if tag == 'div' and self.stack:
            self.stack.pop()


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

    def test_navbar_dropdown_shows_courses_and_trainings_side_by_side(self):
        html = self.client.get(reverse('projects:about-page')).content.decode()
        self.assertIn('nav-courses-dropdown--split', html)
        menu = html.split('nav-courses-dropdown--split', 1)[1].split('nav-item dropdown', 1)[0]
        courses_col, trainings_col = menu.split('nav-courses-dropdown__col--trainings', 1)
        self.assertIn('nav-courses-dropdown__col--courses', courses_col)
        self.assertIn('nav-courses-dropdown__icon-svg', courses_col)
        self.assertIn('nav-courses-dropdown__icon-svg', trainings_col)
        self.assertIn('/courses/ielts-test/', courses_col)
        self.assertNotIn('/courses/pmp-test/', courses_col)
        self.assertIn('/courses/pmp-test/', trainings_col)
        self.assertIn(reverse('projects:trainings-page'), trainings_col)

    def test_menu_items_after_the_courses_dropdown_stay_in_the_navbar(self):
        for trainings in (True, False):
            with self.subTest(trainings=trainings):
                self.training.is_training = trainings
                self.training.save()
                cache.clear()
                finder = _NavParentFinder()
                finder.feed(self.client.get(reverse('projects:about-page')).content.decode())
                parents = finder.parents[reverse('projects:mock-tests-page')]
                self.assertTrue(any('navbar-nav' in c for c in parents), parents)

    def test_navbar_dropdown_is_a_single_list_without_trainings(self):
        self.training.is_training = False
        self.training.save()
        cache.clear()
        html = self.client.get(reverse('projects:about-page')).content.decode()
        self.assertNotIn('nav-courses-dropdown--split', html)

    def test_home_trainings_are_their_own_section(self):
        html = self.client.get(reverse('projects:home-page')).content.decode()
        self.assertIn('id="home-trainings" class="hsvc-section hsvc-section--trainings"', html)

    def test_training_detail_keeps_its_url(self):
        self.assertEqual(self.client.get(reverse('projects:course-detail', args=['pmp-test'])).status_code, 200)

    def test_a_mock_test_cannot_be_a_training(self):
        service = Service(name_az='IELTS Mock', is_training=True, ielts_mock_test=True)
        with self.assertRaises(ValidationError):
            service.clean()
