# Academor

Public website and CMS for **Academor**, an English-language and test-prep education centre in Baku, Azerbaijan. The site promotes courses (IELTS, GMAT, GRE, SAT, YÖS, ALES, and more), study-abroad programmes, team profiles, level tests, English conversation topics, blog posts, reviews, and contact flows. Content is managed in Django admin; rich text fields use CKEditor where configured.

**Production:** [academor.az](https://academor.az)

## Stack

| Layer | Choice |
| --- | --- |
| Runtime | Python 3.11+ |
| Framework | Django 5.2 |
| Database | PostgreSQL 15 |
| Templates | Server-rendered HTML (`academor/templates/`) |
| WSGI (prod) | Gunicorn behind Nginx |
| Dependency install | [uv](https://github.com/astral-sh/uv) + `pyproject.toml` / `uv.lock` |
| Images | Pillow, django-imagekit |
| Static assets | django-compressor (offline bundles in production) |
| i18n | Azerbaijani (default), English, Russian |
| Cache | In-process LocMem with versioned invalidation via ORM signals |
| Bot protection | Cloudflare Turnstile (contact / review forms) |
| Payments | United Payment Azerbaijan API (`payments` app) |

## Django apps

### `projects` — public site + CMS

Handles almost all business logic: models, views, admin, sitemaps, middleware helpers, static assets under `projects/static/`, and query/cache layers in `projects/utils/`.

**Main content models**

- **Service** — course/category pages (slug URLs, instructors, price packages, card icons)
- **CoursePricePackage** — tiered pricing per course
- **Sale** — promotions: homepage banners, optional `%` badge, optional discount on linked course prices, optional `end_date`
- **Team**, **Review**, **BlogPost**, **About**, **Contact**
- **AbroadModel**, **University**, **StudyAbroadSection**, **StudyAbroadAdvantage**
- **Test**, **Question**, **Option**, **UserResult** — level-test flow
- **Media** — shared uploads (hero backgrounds, sale card images, etc.)
- **ContactInquiry** — form submissions

**Public routes** (`projects/urls_v1.py`)

| Path | Page |
| --- | --- |
| `/` | Home |
| `/courses/` | Course listing |
| `/courses/<slug>/` | Course detail + checkout entry |
| `/about/`, `/services/`, `/contact/` | Institutional pages |
| `/abroad/`, `/abroad/<slug>/`, `/abroad/universities/<slug>/` | Study abroad |
| `/team/`, `/team/<slug>/` | Team listing and profiles |
| `/blog/`, `/blog/<slug>/` | Blog |
| `/tests/`, `/tests/<id>/` | Level tests |
| `/topics/`, `/topics/<slug>/` | English conversation topics |

Legacy URL patterns redirect to the slug-based routes where applicable.

### `payments` — online course checkout

Integrates with **United Payment Azerbaijan**:

- Start checkout from course detail (`/payment/course/<slug>/` or `/payment/checkout/course/<slug>/`)
- Callback handling: success, cancel, decline
- **Payment** records + **CourseEnrollment** created after successful payment
- Sale discounts from admin are applied to payable amounts when `Sale.apply_to_service_prices` is enabled

Root URLconf also exposes `/sitemap.xml`, `/robots.txt`, `/i18n/setlang/`, and a secret **ADMIN_URL** prefix.

## Repository layout

```
Academor/
├── academor/                    # Django project root (manage.py lives here)
│   ├── academor/                # settings, urls, wsgi, middleware, env_load
│   ├── projects/                # main app: models, views, admin, signals, static, migrations
│   ├── payments/                # payment gateway + enrollment
│   ├── templates/               # site HTML + includes
│   ├── locale/                  # az / en / ru translations
│   ├── media/                   # uploads (gitignored)
│   └── staticfiles/             # collectstatic output (gitignored)
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yaml      # db + web (gunicorn) + nginx
│   └── entrypoint.sh            # migrate, compress, collectstatic
├── nginx/
│   └── nginx.conf               # TLS, static/media, proxy to gunicorn
├── pyproject.toml
├── uv.lock
└── README.md
```

Environment files are loaded from `docker/.env` first, then `academor/.env` (local overrides). Never commit real secrets.

## Environment variables

### Required

| Variable | Purpose |
| --- | --- |
| `SECRET_KEY` | Django secret key |
| `ADMIN_URL` | Secret admin path prefix (must end with `/` after normalization) |
| `POSTGRES_DB` | Database name |
| `POSTGRES_USER` | Database user |
| `POSTGRES_PASSWORD` | Database password |
| `POSTGRES_HOST` | Database host (`db` in Docker, `localhost` locally) |
| `POSTGRES_PORT` | Database port (usually `5432`) |

### Common optional

| Variable | Purpose |
| --- | --- |
| `DEBUG` | `true` locally, `false` in production |
| `ALLOWED_HOSTS` | Comma-separated extra hosts merged with `academor.az` / `www.academor.az` |
| `SITE_CANONICAL_DOMAIN` | Canonical domain for sitemap and absolute URLs (default `academor.az`) |
| `SITEMAP_STATIC_LASTMOD` | ISO date for static sitemap `lastmod` hints |

### Cloudflare Turnstile (forms)

| Variable | Purpose |
| --- | --- |
| `TURNSTILE_SITE_KEY` | Widget site key (empty = Turnstile disabled) |
| `TURNSTILE_SECRET_KEY` | Server-side verification key |

### United Payment (course checkout)

| Variable | Purpose |
| --- | --- |
| `UNITED_PAYMENT_AUTH_URL` | Auth endpoint |
| `UNITED_PAYMENT_USERNAME` | API username |
| `UNITED_PAYMENT_PASSWORD` | API password |
| `UNITED_PAYMENT_BASE_URL` | API base URL |
| `UNITED_PAYMENT_SUCCESS_URL` | Return URL after success |
| `UNITED_PAYMENT_CANCEL_URL` | Return URL after cancel |
| `UNITED_PAYMENT_DECLINE_URL` | Return URL after decline |
| `PAYMENT_FRONTEND_RETURN_URL` | Optional post-callback redirect (empty = render payment result templates) |

### Email (local `settings_local` only, optional)

`EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`, `SERVER_EMAIL`

Production uses `academor.settings`; local development typically uses `academor.settings_local` (see below).

## Local development

### 1. Install dependencies

From the repository root:

```bash
pip install uv
uv sync
```

Or install from the exported requirements in your preferred workflow.

### 2. Configure environment

Create `academor/.env` (or `docker/.env`) with at least the required variables above. For local `runserver`, set `DEBUG=true` and point `POSTGRES_*` at a local PostgreSQL instance.

`ADMIN_URL` is required even locally (e.g. `secret-admin/`).

### 3. Migrate and run

```bash
cd academor
set DJANGO_SETTINGS_MODULE=academor.settings_local   # Windows
# export DJANGO_SETTINGS_MODULE=academor.settings_local  # Linux/macOS

python manage.py migrate
python manage.py createsuperuser   # optional
python manage.py runserver
```

Open `http://127.0.0.1:8000/` and admin at `http://127.0.0.1:8000/<ADMIN_URL>`.

### 4. Translations (after editing `.po` files)

```bash
cd academor
python manage.py compilemessages
```

## Docker (production-style stack)

From the `docker/` directory, with `docker/.env` configured:

```bash
cd docker
docker compose up --build
```

Services:

- **db** — PostgreSQL 15 with persistent volume
- **web** — Gunicorn (`academor.settings`), runs migrations, `compress`, and `collectstatic` on start
- **nginx** — TLS termination (Let’s Encrypt paths in config), serves `/static/` and `/media/`, proxies to Gunicorn

Static and media directories are bind-mounted from `academor/staticfiles` and `academor/media`.

After pulling schema changes, containers re-run migrations on startup; for manual runs:

```bash
docker compose exec web python academor/manage.py migrate
```

## Caching and content updates

Heavy read paths use `@cached_query` / `@cached_page_data` with a global `cache_version` key. **ORM signals** in `projects/signals.py` bump that version (or call `invalidate_sale_cache()`) when admin content changes — courses, team, blog, media, sales, price packages, etc.

**Sales** invalidate on Sale save/delete, Sale↔Service M2M changes, promo **Media** linked to a Sale, and Sale admin list-editable saves.

**Note:** When a sale `end_date` passes at midnight, cache is not bumped automatically until the next admin edit or cache timeout (~2 hours). Plan a cron or manual cache bump if you need midnight-sharp expiry without edits.

LocMem cache is **per Gunicorn worker**; each worker holds its own copy until invalidated.

## Sales and pricing (admin)

In **Sales**:

- **Active** promotions appear on the homepage sales section (horizontal banner with optional background image, optional `%` column, optional deadline).
- Link **Services** and enable **Apply discount to service prices** to show sale badges on course cards and reduce displayed/checkout prices by the configured percent.
- **End date** hides expired promotions from queries; null percent allows event-style banners without a numeric discount.

## Security notes

- Do not commit `SECRET_KEY`, database passwords, payment credentials, or Turnstile secrets.
- Keep `ADMIN_URL` non-guessable.
- Production sets secure cookies and trusts `X-Forwarded-Proto` behind Nginx/Cloudflare.
- Review `CSRF_TRUSTED_ORIGINS` and `ALLOWED_HOSTS` when adding staging domains.

## Contributing

Use the usual Git workflow (feature branches, pull requests, review). After model changes, add migrations under `projects/migrations` or `payments/migrations` and run `migrate` before deploy.

For Django deployment checklists, see the [official Django deployment docs](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/) in addition to this project’s Docker/Nginx setup.
