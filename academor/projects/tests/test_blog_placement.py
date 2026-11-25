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


def _image_file(name, size):
    from io import BytesIO

    from django.core.files.uploadedfile import SimpleUploadedFile
    from PIL import Image

    buf = BytesIO()
    Image.new('RGB', size, (0, 49, 61)).save(buf, format='PNG')
    return SimpleUploadedFile(name, buf.getvalue(), content_type='image/png')


class BlogMobileCoverTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_cards_use_the_mobile_cover_on_phones(self):
        import tempfile

        from django.test import override_settings

        with tempfile.TemporaryDirectory() as media, override_settings(MEDIA_ROOT=media):
            post = _post('Mobil cover', cover=_image_file('wide.png', (1200, 600)), cover_mobile=_image_file('tall.png', (600, 900)))
            data = serialize_blog_post(post)
            self.assertTrue(data['cover_mobile'])
            self.assertNotEqual(data['cover_mobile'], data['cover'])

            home = self.client.get(reverse('projects:home-page')).content.decode()
            self.assertIn('<source media="(max-width: 767.98px)" srcset="%s">' % data['cover_mobile'], home)
            listing = self.client.get(reverse('projects:blog-page')).content.decode()
            self.assertIn('srcset="%s"' % data['cover_mobile'], listing)

            # without a mobile cover nothing changes
            plain = _post('Adi cover', cover=_image_file('only.png', (1200, 600)))
            self.assertIsNone(serialize_blog_post(plain)['cover_mobile'])

    def test_mobile_cover_alone_is_also_the_desktop_cover(self):
        import tempfile

        from django.test import override_settings

        with tempfile.TemporaryDirectory() as media, override_settings(MEDIA_ROOT=media):
            post = _post('Yalnız mobil', cover_mobile=_image_file('tall.png', (600, 900)))
            data = serialize_blog_post(post)
            self.assertTrue(data['cover'])
            self.assertTrue(data['cover_mobile'])
