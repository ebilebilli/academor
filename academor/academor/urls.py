from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from projects.sitemaps import SITEMAPS
from projects.views.i18n_views import set_language
from projects.views.robots_txt import robots_txt
from projects.views.errors import handler404
from portals.views.crm_views import admin_login


urlpatterns = [
    # CRM for the office team (staff only), under the same secret prefix as the admin
    path(f'{settings.ADMIN_URL}crm/', include('portals.crm_urls')),
    path(f'{settings.ADMIN_URL}login/', admin_login, name='admin_login_to_crm'),
    path(f'{settings.ADMIN_URL}', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('i18n/setlang/', set_language, name='set_language'),
    path('robots.txt', robots_txt, name='robots_txt'),
    path(
        'sitemap.xml',
        sitemap,
        {'sitemaps': SITEMAPS},
        name='django.contrib.sitemaps.views.sitemap',
    ),
    path('', include('projects.urls_v1')),
    path('portal/', include('portals.urls_v1')),
    path("payment/", include("payments.urls")),
]

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)