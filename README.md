# Academor

Public website and CMS for **Academor**, an English-language and test-prep education centre in Baku, Azerbaijan. The site promotes courses (IELTS, GMAT, GRE, SAT, YÖS, ALES, and more), study-abroad programmes, team profiles, level tests, English conversation topics, blog posts, reviews, and contact flows. Content is managed in Django admin; rich text fields use CKEditor where configured.

A separate **student portal** (`/portal/`) gives teachers, students, and parents access to schedules, lessons, attendance, scores, quizzes, classrooms, and notifications — with auth isolated from the Django admin session.

**Production:** [academor.az](https://academor.az)

## Architecture

Django **monolith** with server-rendered HTML templates. There is no separate frontend app (no React/Vue, no `package.json`). Public pages are class-based views; the admin panel is a custom CMS built on Django admin.

| Area | Location |
| --- | --- |
| Public views | `academor/projects/views/` |
| Portal views | `academor/portals/views/` |
| Query + cache layer | `academor/projects/utils/queries.py` |
| Cache invalidation | `academor/projects/signals.py` |
| CMS admin | `academor/projects/admin/admin_v1.py`, `academor/portals/admin/admin_v1.py` |
| Site templates | `academor/templates/` (public + `portals/` subtree) |
| Static assets | `academor/projects/static/`, `academor/portals/static/` (Bootstrap 5, custom CSS/JS) |
| Translations | `academor/locale/{az,en,ru}/` |

## Stack

| Layer | Choice |
| --- | --- |
| Runtime | Python 3.11+ |
| Framework | Django 5.2+ |
| Database | PostgreSQL 15 |
| Templates | Server-rendered HTML (`academor/templates/`) |
| Frontend | Bootstrap 5.3, vanilla JS, Swiper, Font Awesome (no bundler) |
| WSGI (prod) | Gunicorn (2 workers) behind Nginx |
| Dependency install | [uv](https://github.com/astral-sh/uv) + `pyproject.toml` / `uv.lock` |
| Images | Pillow, django-imagekit |
| Rich text | django-ckeditor |
| Static assets | django-compressor (offline bundles in production) |
| i18n | Azerbaijani (default), English, Russian |
| Cache | In-process LocMem with versioned invalidation via ORM signals |
| Bot protection | Cloudflare Turnstile (contact / review forms) |
| Payments | United Payment Azerbaijan API (`payments` app) |
| Time zone | `Asia/Baku` |

## Django apps

### `projects` — public site + CMS

Handles almost all business logic: models, views, admin, sitemaps, middleware helpers, static assets under `projects/static/`, and query/cache layers in `projects/utils/`.

**Main content models**

| Model | Purpose |
| --- | --- |
| **Service** | Course/category pages (slug URLs, instructors, price packages, card icons) |
| **CoursePricePackage** | Tiered pricing per course; optional homepage carousel and package tabs |
| **Sale** | Promotions: homepage banners, optional `%` badge, optional discount on linked course prices, optional `end_date` |
| **Team**, **Review** | Staff profiles and testimonials |
| **BlogPost**, **BlogPostImage**, **ContentTag** | Blog posts, gallery images, tag filtering |
| **About**, **AboutWhyItem** | About page content and “why us” items |
| **Contact**, **ContactInquiry** | Contact page settings and form submissions |
| **AbroadModel**, **University**, **StudyAbroadSection**, **StudyAbroadAdvantage** | Study-abroad programmes |
| **Test**, **Question**, **Option**, **UserResult** | Level-test flow |
| **Media** | Shared uploads (hero backgrounds, sale card images, etc.) |
| **Tagline** | Per-page banner taglines (home, courses, blog, etc.) |
| **SiteFaqEntry** | FAQ entries for the services page |

**English conversation topics** are static Python data in `projects/conversation_topics_data.py` (not CMS-managed).

**Public routes** (`projects/urls_v1.py`)

| Path | Page |
| --- | --- |
| `/` | Home |
| `/courses/` | Course listing |
| `/courses/<slug>/` | Course detail + checkout entry |
| `/about/`, `/services/`, `/contact/` | Institutional pages |
| `/abroad/`, `/abroad/<slug>/`, `/abroad/universities/<slug>/` | Study abroad |
| `/team/`, `/team/<slug>/` | Team listing and profiles |
| `/blog/`, `/blog/<slug>/`, `/blog/tag/<slug>/` | Blog listing, detail, tag filter |
| `/blog/posts/` | AJAX partial for filtered blog listing |
| `/tests/`, `/tests/<id>/` | Level tests |
| `/topics/`, `/topics/<slug>/` | English conversation topics |

Legacy URL patterns (PK-based blog/team/abroad URLs, old `/learn/english-conversation-topics/` paths) redirect to slug-based routes where applicable.

### `payments` — online course checkout

Integrates with **United Payment Azerbaijan**:

| Path | Purpose |
| --- | --- |
| `/payment/course/<slug>/` | Start checkout for a course |
| `/payment/checkout/course/<slug>/` | Same flow (alternate entry) |
| `/payment/start/<amount>/` | Generic amount checkout |
| `/payment/success/`, `/cancel/`, `/decline/` | Gateway callbacks |

After successful payment:

- **Payment** record is updated with buyer info and transaction details
- **CourseEnrollment** is created with a generated training agreement (contract HTML)
- Sale discounts from admin are applied when `Sale.apply_to_service_prices` is enabled
- Admin can view enrollment contracts and export PDF from the payments admin

Root URLconf also exposes `/sitemap.xml`, `/robots.txt`, `/i18n/setlang/`, and a secret **ADMIN_URL** prefix.

### `portals` — student / teacher / parent portal

Role-based portal at **`/portal/`** for day-to-day learning workflows. Portal users log in via `/portal/login/` or the login modal on the public site navbar; authenticated users see a **Portal** button that routes to their role dashboard.

**Auth isolation:** Portal uses its own `portal_sessionid` cookie (scoped to `/portal/` paths) and middleware (`PortalAuthenticationMiddleware`, `PortalSessionMiddleware`), separate from Django admin's `sessionid`. A staff member can stay logged into admin and portal at the same time without session clashes.

**Roles**

| Role | Main capabilities |
| --- | --- |
| **Teacher** | Study groups, weekly schedule, lessons (with attachments and video links), attendance (per session or per student), scores and weekly score entry, quiz management, manual grading review, IELTS mock result review, classrooms/textbooks |
| **Student** | Schedule, lessons, scores, quiz categories and timed attempts (multiple formats), IELTS full mock test, classrooms, notifications |
| **Parent** | Read-only child views: schedule, lessons, scores, quiz results, attendance, classrooms (child selector when multiple children are linked) |

**Main models** (`portals/models/`)

| Model | Purpose |
| --- | --- |
| **StudentProfile**, **TeacherProfile**, **ParentProfile** | Portal user profiles linked to Django `User` |
| **StudentCourseSpecialization**, **TeacherCourseSpecialization** | Which course types (IELTS, GMAT, etc.) a user is enrolled in or teaches |
| **StudyGroup** | Teacher-led group with students and linked course types |
| **Schedule**, **Attendance** | Recurring slots and attendance marks |
| **Lesson**, **LessonCategory**, **LessonAttachment**, **VideoRecord** | Lesson content, PDF/image/video attachments, and recordings |
| **Classroom** | Group- or teacher-scoped textbook/material spaces (PDF, description) |
| **Score**, **WeeklyStudentScore** | Teacher-entered assessment scores and weekly rollups |
| **Quiz**, **QuizCategory**, **QuizQuestion**, **QuizResult** | Quiz builder, MCQ question bank, attempts, and results |
| **ListeningAudio**, **ListeningQuestion** | IELTS-style listening sections (audio clips + questions) |
| **ReadingPassage**, **ReadingQuestionGroup**, **ReadingQuestion** | IELTS-style reading passages with grouped auto-scored questions |
| **SpeakingPart**, **SpeakingQuestion**, **SpeakingRecording** | IELTS-style speaking tasks with student audio uploads |
| **IeltsMockTestAttempt** | Full mock session chaining Listening → Reading → Writing → Speaking |
| **PortalNotification**, **QuizResultReview** | In-app notifications and teacher review of manual quiz answers |

**Quiz formats**

Each `Quiz` has exactly one format flag (`is_listening`, `is_essay`, `is_speaking`, or `is_reading`); standard MCQ quizzes have all flags off.

| Format | Grading | Student route | Notes |
| --- | --- | --- | --- |
| **Standard MCQ** | Auto | `/portal/student/quizzes/<id>/take/` | Random question selection from `QuizQuestion` bank; optional time limit |
| **Reading** | Auto (IELTS band) | `/portal/student/quizzes/<id>/reading/` | Passages, question groups, 14+ IELTS question types (TFNG, matching, completion, etc.) |
| **Listening** | Manual (teacher) | Same take flow with listening UI | Audio clips (`ListeningAudio`) and linked questions; teacher reviews submission |
| **Writing** (`is_essay`) | Manual (teacher) | `/portal/student/quizzes/<id>/manual/` | Free-text essay; teacher scores and writes corrections |
| **Speaking** (`is_speaking`) | Manual (teacher) | `/portal/student/quizzes/<id>/speaking/` | Part 1/2/3 prompts; student records audio; teacher reviews |

Quizzes are scoped by **course type** (`QuizCategory.service`) and **study group** membership — a student only sees quizzes for services they are enrolled in and groups they belong to. Teachers see quizzes for their specializations and groups.

**IELTS full mock test**

Students with IELTS course access can start a chained mock at `/portal/student/ielts-mock/`:

1. **Listening** — auto-scored quiz picked from available listening quizzes
2. **Reading** — auto-scored reading quiz
3. **Writing** — manual essay quiz
4. **Speaking** — manual speaking quiz

Progress is tracked in `IeltsMockTestAttempt`; Listening and Reading bands are computed automatically, Writing and Speaking await teacher review. Teachers view completed mocks at `/portal/teacher/ielts-mock/<id>/`. Quiz-taking routes are excluded from AJAX fragment navigation so timers and recordings are not interrupted.

**Portal routes** (`portals/urls_v1.py`, prefix `/portal/`)

| Path | Page |
| --- | --- |
| `/portal/login/`, `/portal/logout/` | Portal auth |
| `/portal/`, `/portal/profile/` | Role-aware dashboard redirect; profile edit (avatar, bio, contact links) |
| `/portal/teacher/…` | Dashboard, groups, schedule CRUD, lessons CRUD, attendance, scores, weekly scores, quizzes, quiz result review, classrooms, IELTS mock detail, notifications |
| `/portal/student/…` | Dashboard, schedule, lessons, scores, quizzes (start/take/submit per format), IELTS mock, classrooms, notifications |
| `/portal/parent/…` | Dashboard and child-linked schedule, lessons, scores, attendance, quiz categories/results, classrooms, notifications |

**AJAX fragment navigation:** Most portal pages support in-app navigation without full page reloads. `portal-nav-ajax.js` intercepts internal links, fetches HTML with `X-Portal-Fragment: 1`, and swaps content via `PortalFragmentMiddleware`. Quiz take pages, IELTS mock flows, login/logout, and some heavy list views are excluded.

**Portal admin** (`portals/admin/admin_v1.py`): user creation with role assignment, study groups, schedule, lessons, quiz builder (including reading/listening/speaking inlines), question bank, attendance, scores, classrooms — with branded templates under `templates/admin/portals/` and custom JS for reading passage and quiz question editing.

**Portal templates & static**

| Location | Contents |
| --- | --- |
| `templates/portals/` | Role dashboards, quiz play UI (reading tabs, speaking recorder, manual essay), lesson forms, shared includes |
| `portals/static/portals/css/` | Portal shell, redesign tokens, quiz-reading/speaking styles, lesson video lightbox |
| `portals/static/portals/js/` | `portal-nav-ajax.js`, `portal-init.js`, `quiz-take-reading.js`, `quiz-take-speaking.js`, `quiz-take-manual.js`, `quiz-start-gate.js`, `quiz-leave-guard.js`, lesson and score helpers |

**JSON resource banks** (loaded via management commands)

| Directory | Purpose |
| --- | --- |
| `portals/resources/quiz_questions/` | Standard MCQ quizzes by level (A1–C1) |
| `portals/resources/reading_questions/` | IELTS reading tests (`ielts_reading_test_*.json`, 40 questions each) |
| `portals/resources/speaking_questions/` | IELTS speaking tests (parts and prompts) |

**Portal management commands**

| Command | Purpose |
| --- | --- |
| `python manage.py seed_sample_quizzes` | Create sample quiz categories and questions for local demo |
| `python manage.py load_quiz_category_questions` | Import MCQ quizzes from `portals/resources/quiz_questions/` |
| `python manage.py load_reading_quiz_resources` | Import reading quizzes from `portals/resources/reading_questions/` (`--file`, `--keep-old`) |
| `python manage.py load_speaking_quiz_resources` | Import speaking quizzes from `portals/resources/speaking_questions/` (`--file`, `--keep-old`) |
| `python manage.py generate_ielts_reading_bank` | Regenerate reading JSON from built-in topic bank (tests 2–51; `--dry-run` to validate only) |

**Portal tests:** `python manage.py test portals` — auth isolation, quiz submit/visibility/manual grading, reading and speaking flows, IELTS mock test, notifications, classrooms, attendance, schedule, weekly scores, teacher lessons, admin forms, AJAX fragments, resource loaders.

## Repository layout

```
Academor/
├── academor/                    # Django project root (manage.py lives here)
│   ├── academor/                # settings, urls, wsgi, middleware, env_load
│   ├── projects/                # main app: models, views, admin, signals, static, migrations
│   ├── portals/                 # student/teacher/parent portal: auth, quizzes, schedule, admin
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
│   └── nginx.conf               # TLS, static/media, proxy to gunicorn, Cloudflare real-IP
├── entrypoint-local.sh          # local Docker helper (settings_local, no compress)
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

### Starter `.env` (local)

Create `academor/.env` with at least:

```env
SECRET_KEY=change-me-to-a-long-random-string
ADMIN_URL=secret-admin/
DEBUG=true

POSTGRES_DB=academor
POSTGRES_USER=academor
POSTGRES_PASSWORD=academor
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Optional — leave empty to disable
TURNSTILE_SITE_KEY=
TURNSTILE_SECRET_KEY=

# Optional — required only for live checkout
UNITED_PAYMENT_AUTH_URL=
UNITED_PAYMENT_USERNAME=
UNITED_PAYMENT_PASSWORD=
UNITED_PAYMENT_BASE_URL=
UNITED_PAYMENT_SUCCESS_URL=
UNITED_PAYMENT_CANCEL_URL=
UNITED_PAYMENT_DECLINE_URL=
```

## Local development

### 1. Install dependencies

From the repository root:

```bash
pip install uv
uv sync
```

### 2. Configure environment

Create `academor/.env` (or `docker/.env`) with at least the required variables above. For local `runserver`, set `DEBUG=true` and point `POSTGRES_*` at a local PostgreSQL instance.

`ADMIN_URL` is required even locally (e.g. `secret-admin/`).

### 3. Migrate and run

```bash
cd academor

# Windows (PowerShell)
$env:DJANGO_SETTINGS_MODULE="academor.settings_local"

# Linux/macOS
export DJANGO_SETTINGS_MODULE=academor.settings_local

python manage.py migrate
python manage.py createsuperuser   # optional
python manage.py runserver
```

Open `http://127.0.0.1:8000/` and admin at `http://127.0.0.1:8000/<ADMIN_URL>`. Portal login is at `http://127.0.0.1:8000/portal/login/`.

Admin UI is always **English** regardless of the public site language (`CustomLocaleMiddleware`).

### 4. Translations (after editing `.po` files)

```bash
cd academor
python manage.py compilemessages
```

Content is translated on three levels:

1. Django UI strings — `{% trans %}` in templates + `.po` files under `locale/`
2. CMS model fields — `_az`, `_en`, `_ru` suffixes on admin-managed content
3. SEO defaults — `projects/seo_page_defaults.py` and context processors

## Docker (production-style stack)

From the `docker/` directory, with `docker/.env` configured:

```bash
cd docker
docker compose up --build
```

Services:

| Service | Role |
| --- | --- |
| **db** | PostgreSQL 15 with persistent volume and healthcheck |
| **web** | Gunicorn (`academor.settings`), runs migrations, `compress`, and `collectstatic` on start |
| **nginx** | TLS termination (Let's Encrypt paths in config), serves `/static/` and `/media/`, proxies to Gunicorn |

Static and media directories are bind-mounted from `academor/staticfiles` and `academor/media`.

After pulling schema changes, containers re-run migrations on startup. For manual runs:

```bash
docker compose exec web python academor/manage.py migrate
```

For local Docker with `settings_local` (no offline compress), use `entrypoint-local.sh` in a custom compose override.

## Caching and content updates

Heavy read paths use `@cached_query` / `@cached_page_data` with a global `cache_version` key. **ORM signals** in `projects/signals.py` bump that version (or call targeted invalidators) when admin content changes — courses, team, blog, media, sales, price packages, taglines, etc.

Some homepage sections merge **fresh** data on every request (sales banners, team cards, blog preview, featured prices) so time-sensitive content stays current without waiting for cache expiry.

**Sales** invalidate on Sale save/delete, Sale↔Service M2M changes, promo **Media** linked to a Sale, and Sale admin list-editable saves.

**Note:** When a sale `end_date` passes at midnight, cache is not bumped automatically until the next admin edit or cache timeout (~2 hours). Plan a cron or manual cache bump if you need midnight-sharp expiry without edits.

LocMem cache is **per Gunicorn worker**; each worker holds its own copy until invalidated. Sessions are stored in **PostgreSQL** (not cached sessions) to keep language consistent across workers.

## Sales and pricing (admin)

In **Sales**:

- **Active** promotions appear on the homepage sales section (horizontal banner with optional background image, optional `%` column, optional deadline).
- Link **Services** and enable **Apply discount to service prices** to show sale badges on course cards and reduce displayed/checkout prices by the configured percent.
- **End date** hides expired promotions from queries; null percent allows event-style banners without a numeric discount.

## SEO

- Dynamic sitemaps (`/sitemap.xml`) for static pages, courses, blog, team, abroad, universities, tests, and conversation topics
- Canonical URLs, Open Graph tags, and JSON-LD structured data via `projects/utils/seo_meta.py`
- Per-page SEO defaults in `projects/seo_page_defaults.py`
- `robots.txt` served from Django

## Admin CMS

The custom admin includes:

- **Public site CMS** (`projects/admin/admin_v1.py`): branded templates under `templates/admin/`, inline help panels, CKEditor, payment/enrollment management
- **Portal CMS** (`portals/admin/admin_v1.py`): portal user roles, study groups, schedule, lessons, quizzes, question bank, attendance, scores, classrooms — with portal-specific templates under `templates/admin/portals/`

Shared patterns across both:

- Image compression on upload (`AdminImageCompressMixin`)
- List-editable fields and custom filters for common workflows
- Contract PDF export for course enrollments (payments admin)

## Management commands

| Command | Purpose |
| --- | --- |
| `python manage.py resize_university_flags` | Batch-resize university flag images |
| Portal quiz/resource loaders | See **Portal management commands** under the `portals` app section above |

### Running tests

Portal app tests live under `portals/tests/` (see portal section above for coverage areas):

```bash
cd academor
python manage.py test portals
```

## Security notes

- Do not commit `SECRET_KEY`, database passwords, payment credentials, or Turnstile secrets.
- Keep `ADMIN_URL` non-guessable.
- Production sets secure cookies and trusts `X-Forwarded-Proto` behind Nginx/Cloudflare.
- Nginx blocks common scan paths (`.env`, `.git`, `wp-admin`, etc.) before requests reach Django.
- Review `CSRF_TRUSTED_ORIGINS` and `ALLOWED_HOSTS` when adding staging domains.

## Known limitations

- **Limited automated tests** — portal app has test coverage (`portals/tests/`); public site and payments flows are still mostly manual.
- **No CI/CD** — deploy is manual via Docker Compose.
- **Conversation topics** are code-managed, not editable in admin.
- **LocMem cache** does not share state across Gunicorn workers (by design; invalidated via signals).

## Contributing

Use the usual Git workflow (feature branches, pull requests, review). After model changes, add migrations under `projects/migrations`, `portals/migrations`, or `payments/migrations` and run `migrate` before deploy.

For Django deployment checklists, see the [official Django deployment docs](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/) in addition to this project's Docker/Nginx setup.
