from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from projects.models import ServiceCategory, Team, Test


class AcademorSitemap(Sitemap):
    """https:// + canonical host; never rely on django.contrib.sites (example.com)."""

    protocol = 'https'

    def get_domain(self, site=None):
        domain = (getattr(settings, 'SITE_CANONICAL_DOMAIN', '') or '').strip()
        if domain:
            return domain
        return 'academor.az'


# Home 1.0 · main hubs 0.8 · courses index 0.7 · study-abroad hub 0.6 (detail URLs omitted on purpose).
_STATIC_PRIORITY = {
    'projects:home-page': 1.0,
    'projects:about-page': 0.8,
    'projects:services-page': 0.8,
    'projects:contact-page': 0.8,
    'projects:team-page': 0.8,
    'projects:reviews-page': 0.8,
    'projects:tests-page': 0.8,
    'projects:courses-page': 0.7,
    'projects:abroad-page': 0.6,
}


class StaticViewSitemap(AcademorSitemap):
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
        return _STATIC_PRIORITY.get(item, 0.8)

    def changefreq(self, item):
        return 'daily' if item == 'projects:home-page' else 'weekly'

    def lastmod(self, item):
        return getattr(settings, 'SITEMAP_STATIC_LASTMOD', None)


class CourseSitemap(AcademorSitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return ServiceCategory.objects.filter(is_active=True).order_by('order', 'id')

    def location(self, obj):
        return reverse('projects:course-detail', kwargs={'slug': obj.slug})

    def lastmod(self, obj):
        return obj.created_at


class TeamSitemap(AcademorSitemap):
    changefreq = 'weekly'
    priority = 0.55

    def items(self):
        return Team.objects.order_by('order', 'id')

    def location(self, obj):
        return reverse('projects:team-detail', kwargs={'pk': obj.pk})

    def lastmod(self, obj):
        # Team has no created_at; align with static hub refresh date.
        return getattr(settings, 'SITEMAP_STATIC_LASTMOD', None)


class TestSitemap(AcademorSitemap):
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
    'team': TeamSitemap,
    'tests': TestSitemap,
}
