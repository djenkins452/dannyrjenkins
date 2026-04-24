# Local Development Setup

Django resume site (`resume` project, `website` app). SQLite for local, Django 5.0.6 on Python 3.12.

## Prerequisites

- Python 3.12 (Django 5.0.6 needs 3.10+; macOS system Python 3.9 is too old)
  - macOS: `brew install python@3.12`
- Git

## First-time setup

```bash
cd /Users/dannyjenkins/Projects/dannyrjenkins

# 1. Virtual env
python3.12 -m venv venv
source venv/bin/activate

# 2. Dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 3. Database (SQLite, created at ./db.sqlite3)
python manage.py migrate

# 4. Superuser (local default: admin / admin)
DJANGO_SUPERUSER_PASSWORD=admin python manage.py createsuperuser \
    --noinput --username admin --email you@example.com

# 5. Static files (required because whitenoise uses CompressedManifestStaticFilesStorage)
python manage.py collectstatic --noinput
```

## Run the server

```bash
source venv/bin/activate
python manage.py runserver
```

- Home:  http://127.0.0.1:8000/  or  http://localhost:8000/
- Admin: http://127.0.0.1:8000/admin/  (login: `admin` / `admin`)

## Project layout

- `resume/` — Django project (settings, urls, wsgi)
- `website/` — the app (views, models, templates)
- `static/` — source static files
- `staticfiles/` — `collectstatic` output (whitenoise serves from here)
- `db.sqlite3` — local SQLite database

## Changes made during local setup

- Added `'127.0.0.1'` to `ALLOWED_HOSTS` in `resume/settings.py` so `http://127.0.0.1:8000/` works. No impact on production.

## Troubleshooting

- **`HTTP 400 Bad Request: DisallowedHost`** — host is not in `ALLOWED_HOSTS`. Use `localhost` or `127.0.0.1`.
- **`ModuleNotFoundError: django`** — venv not activated. Run `source venv/bin/activate`.
- **`ValueError: Missing staticfiles manifest entry`** — run `python manage.py collectstatic --noinput`.
- **Port 8000 already in use** — `python manage.py runserver 8001`, or kill the existing process: `lsof -ti:8000 | xargs kill`.
- **Wrong Python version** — ensure venv was created with 3.12: `./venv/bin/python --version`.

## Notes / things to watch

- `SECRET_KEY` is committed in `resume/settings.py` and marked insecure — fine for local, rotate for production.
- `DEBUG = True` is hardcoded — fine for local, but prod should override via env var.
- `procfile` references `website.wsgi` but `WSGI_APPLICATION = 'resume.wsgi.application'`. Production deploy may break — doesn't affect local dev.
- `runtime.txt` pins Python 3.14.0 (for Heroku/Railway). Locally we use 3.12 since 3.14 isn't installed; Django 5.0.6 supports both.
- No `website` models have migrations beyond Django defaults — only built-in migrations run.
