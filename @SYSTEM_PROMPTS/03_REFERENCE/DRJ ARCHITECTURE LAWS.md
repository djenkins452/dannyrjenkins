# DRJ Architecture Laws

Project: `dannyrjenkins` — personal executive resume / portfolio site for Danny R. Jenkins, presenting HR operations leadership and personal AI systems work to hiring contacts and industry peers.

These are non-negotiable rules. Each one has a one-paragraph rationale and, where applicable, a forbidden-pattern / required-pattern pair. Every law has evidence in the codebase as it stands today; if a future change would violate one, push back before writing it.

---

## 1. Admin DB is the source of truth for all visible content

The deployed Postgres row, edited through `/admin/`, is the canonical value for every piece of text and configuration a visitor reads. The model defaults, the fixture (`website/fixtures/initial_content.json`), and the template `|default:"…"` strings are bootstrap and fallback only. They never override what an admin has set, and a deploy can never overwrite admin edits except via an explicit, hand-typed CLI flag.

This was learned the hard way: an earlier version of `bootstrap_prod` read `CONTENT_SYNC_MODE=build` from the env var and re-applied the fixture on every dyno restart, silently reverting admin edits. Commit `c49bbf9` moved that trigger from env var to a CLI flag (`--rebuild-from-fixture`), so any value of any environment variable on Railway is now harmless.

**Forbidden:** any code path that writes to a content model without an admin or an explicit one-shot CLI invocation behind it.
**Required:** read content via `Model.load()` (singletons) or `Model.objects.get(...)` (records); never auto-derive content from the fixture in a request handler or a Procfile boot.

---

## 2. Headings live in CharFields, never in HTMLField / TinyMCE

Every H1 and H2 you see on the public site comes from a structured `CharField` on a model. Body text — paragraphs, bold, italic, bullets, links — comes from `HTMLField` (django-tinymce). The TinyMCE config is hard-locked: `valid_elements: 'p,br,strong,em,b,i,ul,ol,li,a[href|title|target|rel]'` (see `resume/settings.py` `TINYMCE_DEFAULT_CONFIG`). No `h1`–`h6` are allowed through, even if a paste tries to smuggle them in.

This means design controls heading typography. An editor cannot accidentally promote an inline phrase into an H2 and break the visual hierarchy.

**Forbidden:** adding `h1..h6` to TinyMCE's `valid_elements`, or rendering `{{ field|safe }}` for a field that is supposed to be a heading.
**Required:** for any new "section" with a title, give it both a `CharField` (e.g. `*_heading`) for the title and an `HTMLField` for the body.

---

## 3. Singletons enforce `pk = 1` in `save()`

Every page that has exactly one record on the public site uses the singleton pattern: `SiteConfig`, `Page` (used for /profile/), `EnterpriseOverview`, `InnovationOverview`, `ConnectPage`, `CaseStudiesIndexPage`, `PerspectivesIndexPage`. Each forces `self.pk = 1` in `save()` and exposes a classmethod `load()` that returns `get_or_create(pk=1)[0]`. The corresponding `ModelAdmin` overrides `changelist_view` to redirect straight to `/change/1/`, hides the "Add" button when one already exists, and disables delete.

**Forbidden:** instantiating a second copy of a singleton, or removing the `pk = 1` line from `save()`.
**Required:** when adding a new "page settings" model, copy the existing singleton scaffolding intact (model `save()` + `load()` + admin redirect + `has_add_permission` + `has_delete_permission`).

---

## 4. Structured fields beat freeform body HTML for any multi-section block

A `CaseStudy` always renders Problem → Role → Approach → Outcome, in that order, on every detail page. Each of those four lives in its own `HTMLField`, not collapsed into one body. The same applies to `EnterpriseFunction` (Responsibilities → Systems Led → Role in the Organization), `Perspective` (lead + ordered sections + closing), `ResumeVersion` (ordered `ResumeSection` rows by section_type), and `Page` (ordered `NarrativeBlock` children).

The reason: structure can't drift between records when the schema enforces it. Someone editing a third case study can't accidentally invent a new section ordering or skip a beat.

**Forbidden:** replacing a structured set of fields with a single freeform body. Forbidden: adding a new "section" by overloading an existing field's body with extra paragraphs.
**Required:** if a record needs a new repeating section, model it explicitly (new `CharField`/`HTMLField` pair, or a new related model with `order` and a foreign key).

---

## 5. Every visible string must be configurable through admin

If a user can see it on a public page, an admin must be able to edit it without a code change. This includes page H1s, H2s, eyebrow labels (e.g. "PLATFORMS AND TOOLS"), nav labels, footer text, form labels, button text, the words inside the SVG architecture diagram on `/innovation/`. The system-wide audit is captured in commit `40ff900` ("Make every visible string on the site editable in admin"). Strings that remain in code today are limited to admin-only chrome (the staff help panel is exempt per the same commit).

**Forbidden:** introducing a new public-facing string as a hardcoded literal in a template or view. Forbidden: re-introducing a string we already moved to admin.
**Required:** a new field on the relevant model with a sensible default, plus a `{{ field|default:"…" }}` template binding so blanking the field still renders.

---

## 6. Templates must use `|default:"…"` fallback for every model-bound string

`{{ site_config.nav_home_label|default:"Home" }}` — never `{{ site_config.nav_home_label }}` alone. Two reasons: (a) the design-time default in the template is a backstop if the admin field is ever cleared, so the page never goes blank; (b) the fallback string is documentation — a developer reading the template sees what the rendered text should look like.

**Forbidden:** `{{ field }}` for a CharField that's meant to render a label, headline, or button text.
**Required:** every binding pairs with a `|default:"…"` whose argument matches the model's `default=` value.

---

## 7. No silent failures on side-effecting operations

The contact form view (`website/views.connect`) is the canonical example. `EmailMessage.send(fail_silently=False)` is wrapped in `try/except`, on exception the failure is logged with `logger.exception(...)` AND a non-field form error surfaces to the user, on success the failure path is skipped and an `INFO`-level "Contact form sent" line goes to the `website` logger. The `LOGGING` config in `resume/settings.py` routes that logger to console so Railway captures it.

**Forbidden:** `except Exception: pass` on any path that does I/O (email, DB write, external HTTP).
**Required:** catch narrowly, log at `exception` level (so traceback ships), and surface a user-visible signal (form error, 5xx, or admin notification — never silent).

---

## 8. The fixture is bootstrap-only, never the live source of truth

`website/fixtures/initial_content.json` exists so a fresh deploy onto an empty Postgres has something to render on the first page load. It is loaded automatically only when `Page.objects.exists()` is False (`bootstrap_prod._seed_if_empty`). After that, every change happens in admin. Editing the fixture is appropriate when adding a brand-new model that doesn't yet exist on prod; editing it to "update copy" is wrong — that copy goes through admin.

**Forbidden:** updating `initial_content.json` to change live wording on a model that already exists in prod.
**Required:** add new fields' default values to the fixture so a from-scratch seed renders correctly. Existing rows are not touched on deploy unless the operator runs `python manage.py bootstrap_prod --rebuild-from-fixture` by hand.

---

## 9. `DEBUG` is environment-driven and defaults to `False`

`DEBUG = os.environ.get('DJANGO_DEBUG', 'False').lower() in ('1', 'true', 'yes')`. The default-False matters because `STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'`: when `DEBUG` is True, Django's `staticfiles_storage.url()` short-circuits the manifest and returns un-hashed URLs, which defeats cache-busting on every CSS / JS change. Production must run with `DEBUG=False`. Local dev sets `DJANGO_DEBUG=true` to opt back in.

**Forbidden:** `DEBUG = True` hardcoded in `resume/settings.py`.
**Required:** if a setting needs different values in dev vs prod, derive it from `os.environ` with a safe default for production.

---

## 10. Modify before adding — no parallel pipelines

The recent commit history (`90f29fd`, `c49bbf9`, `40ff900`, `04239d3`) shows the operating pattern: when a feature needs to evolve, update the existing model / admin / template, don't add a parallel one and leave the old one drifting. The `placeholder` view in `website/views.py` is a known violation — it's defined but unrouted dead code from Phase 1. New work should not create more of those.

**Forbidden:** adding a "v2" model, view, or template alongside the existing one with a TODO to delete the old one later.
**Required:** edit the existing path in place. If the change is large, break it into reviewable commits — but never leave two paths live at once.

---

## 11. Admin matches site nav

Model verbose names, fieldset order, and the admin-index ordering all mirror what a visitor sees on the public site (commit `04239d3`). Page singletons get the page's nav name (`EnterpriseOverview` → "Enterprise Leadership"). Per-record models get the page name plus `— X` (`CaseStudy` → "Case Studies — Entries"). Within an admin form, fieldsets read top-to-bottom in the same order the visitor reads the page.

This is enforced by the override of `admin.site.get_app_list` at the bottom of `website/admin.py`. The `_ADMIN_MODEL_ORDER` list is the authoritative ordering.

**Forbidden:** introducing a new admin entry whose `verbose_name_plural` doesn't read like something on the site nav.
**Required:** when adding a model, also add it to `_ADMIN_MODEL_ORDER` in the right slot, and write its `Meta.verbose_name`/`verbose_name_plural` in site-language.

---

## 12. No background workers, no cache layer, no async

The `Procfile` is one line: `web: python manage.py migrate && python manage.py bootstrap_prod && gunicorn …`. There is no Celery, no Redis, no RQ, no cache backend, no scheduled jobs. Every request is request-response, synchronous. The site is small and that's deliberate. If a feature seems to need async (a long-running request, a queued job), the right answer is almost always to make the request faster or to do the work offline before deploy, not to add infrastructure.

**Forbidden:** adding `celery`, `redis`, or any broker dependency without an explicit, written justification approved by the operator.
**Required:** if a request takes more than ~1 second, profile it first and look for an N+1 query or a missing `prefetch_related` (`enterprise_leadership` view already uses `prefetch_related('blocks')` for `Page`).

---

## 13. Admin-only changes must not generate schema migrations

When the work is purely admin presentation — verbose names, fieldset reorder, help-text rewording — the migration produced should contain only `AlterModelOptions` (or no migration at all if changes are made via `ModelAdmin.get_form` overrides). Changing per-field `help_text` on a model generates an `AlterField` migration, which is harmless but noisy. The established pattern (commit `40b48b7`) is to override help_text in the admin form via `get_form` when the underlying field doesn't otherwise need to change.

**Forbidden:** generating an `AlterField` migration for a help_text-only tweak when you could have done it via `ModelAdmin.get_form`.
**Required:** before running `makemigrations`, decide whether the change is structural (add field, change default) or presentational (reword help_text, rename verbose). Presentational goes through admin, structural goes through a migration.

---

## 14. Push to `main` deploys to production — treat it that way

The Railway app deploys directly from `main`. There is no staging environment. Pre-flight before pushing: `python manage.py check` must be clean; if `static/` changed, `collectstatic` must be re-run and `staticfiles/` committed (manifest storage will 500 on a missing entry); `DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS` in `resume/settings.py` must be in a working state.

**Forbidden:** pushing without running `manage.py check` first.
**Required:** the operator's explicit "yes, push" before `git push` runs (per `CLAUDE.md` behavior rules; the standing instruction in this session is "after all development, automatically push").

---

Last updated: 2026-05-04.
