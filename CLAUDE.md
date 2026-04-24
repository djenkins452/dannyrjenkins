# dannyrjenkins — Claude Code Instructions

**Project:** Django 5.0 personal resume / CV site
**Repo:** GitHub: djenkins452/dannyrjenkins
**Local setup:** See [README_LOCAL.md](README_LOCAL.md)

---

## Behavior Rules

**Do NOT ask permission for:** reading files, searching, grepping, running migrations locally, starting the dev server.

**Ask permission for:** destructive operations (deleting files, resetting `db.sqlite3`), pushing to `main`, anything that affects the deployed site.

**Communication:** Be direct, skip "Would you like me to...", execute don't propose, summarize results not intentions.

**Auto-fix rule:** Fix obvious quality issues (typos, dead code, wrong module references) when you're already editing a nearby file.

---

## Tech Stack & Architecture

- Django 5.0.6 | SQLite (dev) | whitenoise for static files
- Gunicorn WSGI | Railway deployment (per `ALLOWED_HOSTS` and `procfile`)
- Python 3.12 locally (system 3.9 is too old); `runtime.txt` pins 3.14 for prod

**Layout:**
- `resume/` — Django project (`settings.py`, `urls.py`, `wsgi.py`). `DJANGO_SETTINGS_MODULE = 'resume.settings'`
- `website/` — the only app: 2 views (`home`, `about`), templates, no models
- `static/` — source static assets (CSS, images, resume PDFs)
- `staticfiles/` — `collectstatic` output (whitenoise serves this; `CompressedManifestStaticFilesStorage`)
- `db.sqlite3` — local DB (only holds Django built-ins: auth, sessions, admin)

The site has no custom models, no authentication flow beyond the admin, and no background jobs. Keep it that way unless the user explicitly wants to add something.

---

## Local Development

Full setup steps live in [README_LOCAL.md](README_LOCAL.md). Quick commands:

```bash
source venv/bin/activate
python manage.py runserver           # http://127.0.0.1:8000/
python manage.py check
python manage.py migrate
python manage.py collectstatic --noinput   # required when static/ changes (manifest storage)
```

**When adding/editing static files:** always re-run `collectstatic` before testing, or whitenoise will 500 with a missing-manifest-entry error.

---

## Responsive Design

This is a public-facing site — verify layouts on mobile before shipping.

- Mobile: `max-width: 480px` | Tablet: `max-width: 768px` | Desktop: `min-width: 769px`
- Touch targets ≥ 44x44px, `font-size: 16px` min on inputs (iOS zoom prevention)
- No fixed widths — use `max-width`, `%`, `vw`
- Verify at 375px width (iPhone SE)

---

## Deployment

Production deploys from `main` on GitHub. Before pushing:

1. `python manage.py check` — must pass
2. If static files changed: `python manage.py collectstatic --noinput` and commit `staticfiles/`
3. Confirm `DEBUG`, `SECRET_KEY`, and `ALLOWED_HOSTS` in `resume/settings.py` haven't been left in a broken state

**Do NOT push to `main` without the user's explicit go-ahead** — this is a live site.

---

## Known Issues / Things to Watch

1. **`procfile` references the wrong WSGI module** — `web: gunicorn website.wsgi ...` but the actual module is `resume.wsgi` (see `resume/settings.py` `WSGI_APPLICATION`). If prod boot is broken, this is the likely cause.
2. **`SECRET_KEY` is committed** in `resume/settings.py` and marked `django-insecure-...`. Fine for a public resume site with no user data, but rotate if the site ever collects anything sensitive.
3. **`DEBUG = True` is hardcoded.** Should be env-driven for production (`DEBUG = os.environ.get('DEBUG', 'False') == 'True'`) — fix if you touch settings.
4. **`runtime.txt` pins Python 3.14** — local dev uses 3.12 because 3.14 isn't installed. If Railway enforces 3.14 and a dep breaks, you'll only see it on deploy.
5. **`ALLOWED_HOSTS` contains `https://` prefixed entries** (e.g., `'https://dannyrjenkins.com'`) which Django doesn't need — harmless but redundant. Host header is just the hostname.
6. **No test suite.** There are no tests beyond Django's default `tests.py` stub. Don't invent a test harness unless the user asks.

---

## On Task Completion

After making changes:

1. Run `python manage.py check` — must pass
2. If you touched `static/`, run `collectstatic` and commit `staticfiles/`
3. Start the dev server and confirm the affected pages render (`/` and `/about`)
4. Commit with a descriptive message
5. **Stop.** Do not push to `main` unless the user says to deploy.

Summarize: what changed, what files, how you verified it.
