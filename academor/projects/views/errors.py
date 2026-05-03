"""Custom HTTP error pages (semantic status + crawl hints)."""

from django.shortcuts import render
from django.utils.translation import gettext as _


def handler404(request, exception):
    return render(
        request,
        "404.html",
        {
            "page_title": _("Page not found"),
            "page_description": _("The page you requested is not available on Academor."),
            "seo_noindex": True,
        },
        status=404,
    )
