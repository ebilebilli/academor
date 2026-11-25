"""Homepage blog: left / right featured cards and "door" posts that open the tests page."""

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from projects.models import BlogPost
from projects.utils.queries import _fresh_home_blog_context, serialize_blog_post


def _post(name, **kwargs):
    kwargs.setdefault('on_main_page', True)
    return BlogPost.objects.create(name_az=name, **kwargs)


class BlogPlacementTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_left_post_comes_first_and_right_post_second(self):
        right = _post('Sağ yazı', on_right=True)
        left = _post('Sol yazı', on_left=True)
        right.refresh_from_db()
        self.assertTrue(right.on_top)  # a side implies a featured card
        featured = _fresh_home_blog_context('az')['blog_featured']
        self.assertEqual([p['id'] for p in featured], [left.pk, right.pk])

    def test_only_one_post_per_side_and_not_both_sides(self):
        _post('Birinci', on_left=True)
        with self.assertRaises(ValidationError):
            _post('İkinci', on_left=True)
        with self.assertRaises(ValidationError):
            _post('Hər iki tərəf', on_left=True, on_right=True)

    def test_door_post_opens_the_tests_page(self):
        door = _post('Səviyyəni yoxla', on_way_to_test_page=True)
        self.assertEqual(serialize_blog_post(door)['url'], reverse('projects:tests-page'))
        normal = _post('Adi yazı')
        self.assertEqual(serialize_blog_post(normal)['url'], reverse('projects:blog-detail', kwargs={'slug': normal.slug}))

        response = self.client.get(reverse('projects:blog-detail', kwargs={'slug': door.slug}))
        self.assertRedirects(response, reverse('projects:tests-page'), fetch_redirect_response=False)

        home = self.client.get(reverse('projects:home-page'))
        self.assertContains(home, f'href="{reverse("projects:tests-page")}"')


class BlogPlacementAdminTests(TestCase):
    def test_admin_form_and_list_show_the_placement_fields(self):
        from django.contrib.auth import get_user_model

        admin = get_user_model().objects.create_superuser('blogadmin', 'blogadmin@example.com', 'pass12345')
        self.client.force_login(admin)
        post = _post('Admin yazı')
        page = self.client.get(reverse('admin:projects_blogpost_change', args=[post.pk]))
        self.assertContains(page, 'name="on_left"')
        self.assertContains(page, 'name="on_way_to_test_page"')
        listing = self.client.get(reverse('admin:projects_blogpost_changelist'))
        self.assertContains(listing, 'form-0-on_right')
