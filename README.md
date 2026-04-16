# Academor

## Overview

Academor is the web application for **Academor**, an English-language and test-prep education centre in Baku, Azerbaijan. The public site promotes courses (including IELTS, GMAT, GRE, SAT, YÖS, ALES), study-abroad information, team profiles, level tests, English conversation topics, reviews, and contact flows. Content is managed through Django’s admin interface, with rich text editing where configured.

The stack is **Django 5.2** on **Python 3.11+**, with **PostgreSQL** for data, server-rendered HTML templates, and optional **CKEditor** integration for CMS-style fields.

## Main site areas

- **Home** — hero carousel, highlights, study-abroad grid, team preview, testimonials  
- **Courses** — listing and per-course detail pages (slug-based URLs)  
- **About** and **Services** — institutional and service information  
- **Study abroad** — overview and detail pages for programmes or destinations  
- **Team** — teacher listing and individual profiles  
- **Level test** — test listing and taking flow  
- **English conversation topics** — topic index and detail pages  
- **Contact** and **Reviews** — visitor-facing forms and social proof  
- **Internationalization** — Azerbaijani (default), English, and Russian, with language switching and locale-aware SEO defaults  
- **SEO and discovery** — meta titles and descriptions, sitemap, robots.txt, canonical URLs aligned with production domain settings  

## Technology highlights

- **Django** with a primary app named **projects** (models, views, admin, sitemaps, middleware)  
- **django-ckeditor** for rich text where used  
- **django-cleanup** to help manage file lifecycle on model deletes  
- **Pillow** for image handling  
- **psycopg2** for PostgreSQL  
- **python-dotenv** for loading environment-based configuration  
- **Gunicorn** as a typical production WSGI server  
- **Unidecode** for slug and text normalization tasks  
- In-memory **LocMem** cache with tiered timeouts for page fragments and lists  

## Repository layout (conceptual)

- The **Django project package** lives under the **academor** directory (settings, root URLconf, WSGI, middleware).  
- The **projects** application contains business logic: URL routing, class-based views, models, migrations, admin registrations, static assets scoped to the app, and sitemap definitions.  
- **HTML templates** are grouped under **academor/templates**, with shared includes for layout, navigation, footer, and head metadata.  
- **Locale** translations are stored under **academor/locale**.  
- **Media** uploads and collected **staticfiles** paths are configured relative to the project base directory as usual for Django.  

## Prerequisites

- **Python** 3.11 or newer  
- **PostgreSQL** (version compatible with your hosting; credentials supplied via environment)  
- A way to install dependencies from **pyproject.toml** (for example **uv** or **pip** with a PEP 517–compatible workflow)  

## Environment variables

Configuration is driven by the environment. At minimum, plan for:

- **SECRET_KEY** — Django secret key; must not be committed or shared.  
- **DEBUG** — typically true for local development and false in production.  
- **ADMIN_URL** — required secret path prefix for the admin site (must end with a trailing slash in effective configuration).  
- **POSTGRES_DB**, **POSTGRES_USER**, **POSTGRES_PASSWORD**, **POSTGRES_HOST**, **POSTGRES_PORT** — database connection.  
- **ALLOWED_HOSTS** — optional comma-separated list merged with the project’s default production hostnames when you need extra hosts (for example Docker or staging).  
- **SITE_CANONICAL_DOMAIN** — optional override for canonical domain used in sitemap and similar absolute URLs (defaults are aligned with the live Academor domain).  
- **SITEMAP_STATIC_LASTMOD** — optional ISO date string for static sitemap last-mod hints.  

Cookie and CSRF settings in settings assume HTTPS in non-debug environments; local HTTP origins may be listed for trusted CSRF origins where needed.

## Local development (high level)

1. Clone the repository and open a terminal in the repository root.  
2. Create and activate a virtual environment using your usual tool.  
3. Install the project in editable mode or install dependencies from **pyproject.toml** according to your workflow.  
4. Create a PostgreSQL database and user matching your environment variables.  
5. Place a **.env** file (or export variables in your shell) with at least **SECRET_KEY**, **ADMIN_URL**, and all **POSTGRES_*** values. **DEBUG** may be set to true for local work.  
6. Change into the directory that contains **manage.py** (the inner **academor** folder).  
7. Run Django database migrations so the schema matches the models.  
8. Create a superuser if you need access to the admin.  
9. Start the development server with Django’s **runserver** command.  
10. Open the site in a browser at the host and port shown in the terminal; use the configured **ADMIN_URL** path to reach the admin.  

For production, collect static files into **STATIC_ROOT**, serve **MEDIA** via your reverse proxy or object storage as appropriate, and run the app behind **Gunicorn** (or equivalent) with a reverse proxy that terminates TLS.

## Database and migrations

Schema changes are applied through Django migrations under **projects/migrations**. After pulling updates, run migrate before serving traffic.

## Languages and SEO

Default public language is **Azerbaijani**; **English** and **Russian** are supported via Django’s internationalization machinery and a custom locale middleware so admin UI language can differ from the public site. SEO defaults (titles, descriptions, keywords) are supplied per language through context processors and can be overridden per view where implemented.

## Security notes

- Never commit real **SECRET_KEY** or database passwords.  
- Keep **ADMIN_URL** non-guessable and out of public documentation if the repository is shared.  
- Review **CSRF_TRUSTED_ORIGINS** and **ALLOWED_HOSTS** when deploying to new domains.  

## Contributing and support

Use the project’s usual Git workflow (branches, pull requests, code review). For deployment-specific steps, follow your hosting provider’s Django checklist in addition to Django’s own deployment documentation.

---

*This README intentionally avoids embedded source or shell listings; use Django and PostgreSQL official docs for exact command syntax and flags.*
