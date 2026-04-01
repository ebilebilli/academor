
# ACADEMOR

**ACADEMOR** is the official website backend for an English Academy / course platform. The site presents courses, instructors, careers, about information, and contact options in three languages: **Azerbaijani**, **English**, and **Russian**.

**Live site:** `academor.az`  
**Repository:** `https://github.com/MusfiqEmirov/Academor`

---

## Technologies

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.11, Django 5.x |
| **Database** | PostgreSQL 15 |
| **WSGI server** | Gunicorn |
| **Web server** | Nginx (reverse proxy, static/media) |
| **Package manager** | uv (Python), pyproject.toml |
| **Containerization** | Docker, Docker Compose |
| **Environment** | python-dotenv, `.env` files |

**Key Python packages:** `django`, `gunicorn`, `psycopg2-binary`, `pillow`, `django-cleanup`, `unidecode`, `dotenv`.

---

## Environment variables

Configuration is driven by **environment variables**. Sensitive values and environment-specific settings are **not** committed; they live in `.env` (and optionally `.env.local` for local overrides).

### Hints for required variables

Create a `.env` file in the project root (or in `docker/` when using Docker Compose). Below are the variables used by the app and **hints** for what to set:

| Variable | Hint / Description |
|----------|--------------------|
| `SECRET_KEY` | Django secret key (e.g. from `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`) |
| `DEBUG` | `True` for development, `False` for production |
| `ALLOWED_HOSTS` | Comma-separated hosts, e.g. `localhost,127.0.0.1` or `academor.az,www.academor.az` |
| `ADMIN_URL` | Secret admin path (e.g. `my-secret-admin/`) ? **required** |
| `POSTGRES_DB` | PostgreSQL database name |
| `POSTGRES_USER` | PostgreSQL user |
| `POSTGRES_PASSWORD` | PostgreSQL password |
| `POSTGRES_HOST` | Database host (`db` in Docker, `localhost` when DB is on host) |
| `POSTGRES_PORT` | Database port (default `5432`) |

**Optional (e.g. for local email):**  
`EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`, `SERVER_EMAIL`.

**Important:** `.env` and `.env.local` are listed in `.gitignore`; never commit them. Use `.env.example` (without real secrets) in the repo if you want to document variable names for other developers.

---

## Running locally

### Option 1: Docker Compose (recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/MusfiqEmirov/Academor.git
   cd Academor
   ```

2. **Create `.env`**  
   In the project root or in `docker/`, create a `.env` file with the variables above (see hints). For local runs you can use:
   - `POSTGRES_HOST=db`
   - `POSTGRES_PORT=5432`
   - `DEBUG=True`
   - `ALLOWED_HOSTS=localhost,127.0.0.1`
   - Plus `SECRET_KEY`, `ADMIN_URL`, and DB credentials.

3. **Run with Docker Compose from the `docker` directory**
   ```bash
   cd docker
   docker compose up --build
   ```
   The app will be available at **http://localhost** (Nginx on port 80). The web container runs migrations and `collectstatic` on startup.

4. **Optional: run only DB and web (no Nginx)**  
   You can adapt `docker-compose.yaml` to expose the web service port (e.g. 8000) and access the app at `http://localhost:8000`.

### Option 2: Local Python (no Docker)

1. **Python 3.11** and **PostgreSQL 15** installed locally.

2. **Create a virtual environment and install dependencies**
   ```bash
   cd Academor
   uv venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   uv pip sync uv.lock
   # or: pip install -e .
   ```

3. **Create `.env`** in the project root with at least:
   - `POSTGRES_HOST=localhost`
   - `POSTGRES_PORT=5432`
   - `SECRET_KEY`, `ADMIN_URL`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, and optionally `DEBUG`, `ALLOWED_HOSTS`.

4. **Run migrations**
   ```bash
   cd conco
   python manage.py makemigrations
   python manage.py migrate

   ```

5. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```
   For local settings (e.g. `settings_local`), set:
   ```bash
   set DJANGO_SETTINGS_MODULE=academor.settings_local
   python manage.py runserver
   ```
   (Use `export` on Linux/macOS.)

---

## Deployment

1. **Server:** Provision a host with Docker and Docker Compose (or use a PaaS that supports Docker).

2. **Code and env**
  - Clone the repo: `git clone https://github.com/MusfiqEmirov/Academor.git`
   - Create a production `.env` (e.g. in `docker/` or where Compose is run) with:
     - `DEBUG=False`
    - `ALLOWED_HOSTS=academor.az,www.academor.az` (and any other domains)
     - Strong `SECRET_KEY` and `ADMIN_URL`
     - Production PostgreSQL credentials and `POSTGRES_HOST`/`POSTGRES_PORT` pointing to your DB.

3. **Run with Docker Compose**
   ```bash
   cd docker
   docker compose up -d --build
   ```
   This starts PostgreSQL, the Django app (Gunicorn), and Nginx. Nginx serves static/media and proxies to Gunicorn.

4. **SSL:** Place certificates under `nginx/ssl/` and configure `nginx/nginx.conf` for HTTPS. Adjust `CSRF_TRUSTED_ORIGINS` in Django settings to include your HTTPS origins.

5. **Static/media:** The Compose setup runs `collectstatic` in the entrypoint; static and media are served by Nginx from the mounted volumes.

6. **Updates:** Pull latest code, rebuild and restart:
   ```bash
   git pull
   docker compose up -d --build
   ```

---

## Project structure (overview)

- **`conco/`** ? Django project (settings, URLs, templates, static, locale, apps like `projects`).
- **`docker/`** ? `Dockerfile`, `docker-compose.yaml`, `entrypoint.sh` for DB wait, migrations, and `collectstatic`.
- **`nginx/`** ? Nginx config and `ssl/` (certs not committed).
- **`pyproject.toml`**, **`uv.lock`** ? Python dependencies (uv).
- **`.env`** ? Local/production env (not in repo); use the hints above to create it.

---

## Features (summary)

- **Home:** Hero carousel, about, featured projects, partners, latest vacancies, statistics.
- **Projects:** List and detail with categories, filters, and optional external links.
- **About:** Company info, partners, statistics.
- **Contact:** Details, map, contact form (messages in admin).
- **Vacancies:** List and detail; application form with CV upload; one application per email/phone per vacancy.
- **i18n:** Azerbaijani (default), English, Russian; language switcher and translated SEO metadata.
- **Admin:** Content managed via Django admin; custom admin path via `ADMIN_URL`.

=======

