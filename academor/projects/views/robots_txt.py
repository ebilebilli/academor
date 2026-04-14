from django.conf import settings
from django.http import HttpResponse


def robots_txt(request):
    """RFC 9309-friendly robots.txt (plain UTF-8, absolute Sitemap URL)."""
    admin_segment = (getattr(settings, 'ADMIN_URL', '') or '').strip().strip('/')
    domain = (getattr(settings, 'SITE_CANONICAL_DOMAIN', '') or 'academor.az').strip()
    domain = domain.removeprefix('https://').removeprefix('http://').strip().rstrip('/')

    lines = ['User-agent: *']
    if admin_segment:
        lines.append(f'Disallow: /{admin_segment}/')
    lines.append('')
    lines.append(f'Sitemap: https://{domain}/sitemap.xml')

    body = '\n'.join(lines) + '\n'
    return HttpResponse(body, content_type='text/plain; charset=utf-8')
