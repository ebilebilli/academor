"""Single canonical HTTPS URL per public page — reduces crawler \"duplicate URL\" noise."""

from __future__ import annotations

from urllib.parse import urlencode

from django.conf import settings


def _canonical_origin() -> str:
    """HTTPS origin only; matches sitemap semantics (always https)."""
    host = (
        getattr(settings, "SITE_CANONICAL_DOMAIN", None) or "academor.az"
    ).strip().rstrip("/")
    host = host.removeprefix("https://").removeprefix("http://").strip("/")
    return f"https://{host}" if host else "https://academor.az"


def canonical_url_for_request(request, *, allow_query=frozenset()) -> str:
    """
    Build the canonical absolute URL.

    - Path only by default — strips utm_*, fbclid, meaningless sort params so
      `/path?utm_source=x` duplicates collapse to `/path`.
    - If you add pagination, pass allow_query={'page'} and only whitelist `page`
      when paginated URLs are intentional indexable URLs.
    """
    if not getattr(request, "path", None):
        origin = _canonical_origin()
        return f"{origin}/"

    origin = _canonical_origin()
    path = request.path or "/"
    if not path.startswith("/"):
        path = "/" + path

    if allow_query:
        pairs = []
        for key in sorted(allow_query):
            if key not in request.GET:
                continue
            for val in request.GET.getlist(key):
                if val is not None and str(val).strip():
                    pairs.append((key, val))
        if pairs:
            return f"{origin}{path}?{urlencode(pairs, doseq=True)}"
    return f"{origin}{path}"
