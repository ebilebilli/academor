from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from projects.sitemaps import SITEMAPS
from projects.views.i18n_views import set_language


urlpatterns = [
    path(f'{settings.ADMIN_URL}', admin.site.urls),
    path('i18n/setlang/', set_language, name='set_language'),
    path(
        'sitemap.xml',
        sitemap,
        {'sitemaps': SITEMAPS},
        name='django.contrib.sitemaps.views.sitemap',
    ),
    path('', include('projects.urls_v1')),
]

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)