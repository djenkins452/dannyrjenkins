# Executive Brand v1.0 — Baseline Snapshot & Restore Guide

**Created:** 2026-08-02
**Git tag:** `executive-brand-v1`
**GitHub release:** "Executive Brand v1.0"
**Purpose:** Complete, restorable snapshot of dannyrjenkins.com **before** the Executive Brand Transformation project. This is Version 1.0 of the executive brand — the original "HR Operations" positioning. It preserves both **code** and **configured website content** so the site can be returned to this exact state at any time.

---

## What is in this folder

| File | What it is | Use in restore |
|---|---|---|
| `content_export_all_models_20260802-144849.json` | **Django `dumpdata` of every model in the `website` app** (42 records). The authoritative, portable content backup. Loadable with `loaddata`. | Restore all site content into any DB (SQLite or Postgres). |
| `fixture_initial_content.snapshot.json` | **Exact copy of `website/fixtures/initial_content.json` as it existed today**, unmodified. Preserved verbatim per the task requirement — *not* regenerated. | Reference / restore the original bootstrap fixture. |
| `db.sqlite3.snapshot` | **Raw copy of the local dev database** (`db.sqlite3`, 304 KB) at snapshot time. Named `.snapshot` so it is not caught by the `db.sqlite3` gitignore rule and is therefore committed to git. | Fastest full local restore — drop-in replace `db.sqlite3`. |
| `RESTORE.md` | This document. | — |

### Why the content export has MORE than the fixture
The live content export contains **42 records**; the shipped fixture (`initial_content.json`) contains **40**. Two singleton models — `CaseStudiesIndexPage` and `PerspectivesIndexPage` — exist in the database but are **absent from the fixture** (they are also not listed in `bootstrap_prod.CONTENT_KEY`). Additionally, the fixture's `ResumeVersion` row predates migration `0017` and is missing the resume-assembly fields. **The `content_export_all_models_*.json` file is the complete, current source of truth** and captures everything the fixture does not. Restore from it, not from the fixture, if you want the exact live state.

---

## The two things being preserved

1. **Code** — every file tracked by git at commit `0b78091` (the tagged commit). Restored via the git tag / GitHub release.
2. **Configured content** — every string that drives the public site, which lives in the database (Architecture Law #1: the admin DB is the source of truth). Restored via the JSON exports or the raw SQLite snapshot in this folder.

> Note on environments: **Local dev** uses `db.sqlite3` (in this snapshot). **Production** (Railway) uses **Postgres**, edited through `/admin/`. `db.sqlite3` is gitignored, so the git tag alone does **not** carry database content — that is exactly why the JSON/SQLite exports in this folder exist.

---

## RESTORE INSTRUCTIONS

### 1. Restore the CODE

Restore the entire codebase to the v1 baseline.

Inspect without moving your branch:
```bash
git fetch --tags
git checkout executive-brand-v1        # detached HEAD at the baseline
```

Make `main` point back at the baseline (destructive to later commits — be sure):
```bash
git checkout main
git reset --hard executive-brand-v1
```

Or restore just one or a few files from the baseline without touching everything else:
```bash
git checkout executive-brand-v1 -- <path/to/file>
```

You can also download the source archive from the GitHub release page ("Executive Brand v1.0").

### 2. Restore the FIXTURE

The original bootstrap fixture is preserved verbatim in this folder. To put it back in place:
```bash
cp backups/executive-brand-v1/fixture_initial_content.snapshot.json website/fixtures/initial_content.json
```
(The git tag also contains the original `website/fixtures/initial_content.json`, so `git checkout executive-brand-v1 -- website/fixtures/initial_content.json` does the same thing.)

### 3. Restore DATABASE CONTENT (local dev — SQLite)

**Option A — load the content export (recommended, DB-agnostic).** This upserts every `website` record by primary key. It replaces the content models' rows with the v1 values:
```bash
source venv/bin/activate
python manage.py loaddata backups/executive-brand-v1/content_export_all_models_20260802-144849.json
```

**Option B — drop-in the raw SQLite snapshot (fastest, local only).** Replaces the whole local database file:
```bash
cp backups/executive-brand-v1/db.sqlite3.snapshot db.sqlite3
```

After either option:
```bash
python manage.py migrate          # ensure schema is current
python manage.py runserver        # verify / and /profile/ render the v1 content
```

### 4. Restore PRODUCTION (Railway / Postgres)

Production content lives in Postgres and is normally edited via `/admin/`. To restore the v1 content to prod, choose one:

**Option A — loaddata against production (targeted).** With production database credentials available to Django (e.g. `DATABASE_URL` pointed at prod), run:
```bash
python manage.py loaddata backups/executive-brand-v1/content_export_all_models_20260802-144849.json
```
This upserts the `website` content rows to their v1 values and leaves auth/sessions untouched.

**Option B — fixture-driven rebuild via the deploy path.** Restore the original fixture (step 2), then run the project's documented one-shot rebuild, which upserts every fixture record by natural key:
```bash
python manage.py bootstrap_prod --rebuild-from-fixture
```
⚠️ This overwrites admin edits for records present in the fixture. Because the shipped fixture is missing the two index singletons and the newer resume fields (see above), **Option A is the more complete production restore.**

**Option C — redeploy the code, restore content separately.** Point Railway at the `executive-brand-v1` tag (or reset `main` to it and push) to restore code, then use Option A to restore content. Code and content are independent restores.

---

## HOW THIS SNAPSHOT WAS PUBLISHED (for auditability)

- Backups written to `backups/executive-brand-v1/` and committed to `main`.
- Annotated git tag `executive-brand-v1` created on that commit.
- **Only the tag was pushed** to GitHub (`git push origin executive-brand-v1`). `main` was **not** pushed, so **no Railway production deploy was triggered** by this task.
- A GitHub Release ("Executive Brand v1.0") was created from the tag.

To fully mirror `main` on GitHub later (this **will** trigger a production deploy), an explicit `git push origin main` is required — left for Danny's approval.

---

## RISKS & NOTES

- **`loaddata` upserts by primary key; it does not delete.** If, at restore time, the database contains *new* content records created after this snapshot (e.g. a 5th case study), `loaddata` will not remove them — it only overwrites the 42 records captured here. For an exact match, delete stray records first or use the raw SQLite snapshot (local) / a fresh DB.
- **The SQLite snapshot also contains Django auth/session/admin-log rows** (it is a whole-DB file copy), including the local superuser's hashed password. It is committed to this private repo. If that is undesirable, restore from the JSON content export instead (content-only) and recreate the superuser from `DJANGO_SUPERUSER_*` env vars.
- **Stale fixture:** the shipped `initial_content.json` is not a faithful mirror of the live DB (missing 2 singletons + newer resume fields). This is a pre-existing condition, preserved as-is here. The Executive Brand Transformation project will regenerate the fixture **once at the end** to make it canonical again.
- **Production is Postgres, not this SQLite file.** The SQLite snapshot restores local dev only; production restore uses the JSON export (Options A/B/C above).
- This snapshot reflects content as of the export timestamp `20260802-144849`.
