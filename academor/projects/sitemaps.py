from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from projects.models import AbroadModel, ServiceCategory, Team, Test


class StaticViewSitemap(Sitemap):
    changefreq = 'weekly'

    def items(self):
        return [
            'projects:home-page',
            'projects:courses-page',
            'projects:about-page',
            'projects:services-page',
            'projects:abroad-page',
            'projects:contact-page',
            'projects:team-page',
            'projects:reviews-page',
            'projects:tests-page',
        ]

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return 1.0 if item == 'projects:home-page' else 0.8


class CourseSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return ServiceCategory.objects.filter(is_active=True).order_by('order', 'id')

    def location(self, obj):
        return reverse('projects:course-detail', kwargs={'slug': obj.slug})

    def lastmod(self, obj):
        return obj.created_at


class AbroadSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return AbroadModel.objects.filter(is_active=True).order_by('id')

    def location(self, obj):
        return reverse('projects:abroad-detail', kwargs={'pk': obj.pk})

    def lastmod(self, obj):
        return obj.created_at


class TeamSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return Team.objects.order_by('order', 'id')

    def location(self, obj):
        return reverse('projects:team-detail', kwargs={'pk': obj.pk})


class TestSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return Test.objects.filter(is_active=True).order_by('-created_at')

    def location(self, obj):
        return reverse('projects:test-take', kwargs={'test_id': obj.pk})

    def lastmod(self, obj):
        return obj.created_at


SITEMAPS = {
    'static': StaticViewSitemap,
    'courses': CourseSitemap,
    'abroad': AbroadSitemap,
    'team': TeamSitemap,
    'tests': TestSitemap,
}
