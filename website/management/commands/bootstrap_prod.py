"""Idempotent production bootstrap.

Runs on every deploy (from Procfile) and performs two actions safely:

1. Content sync — default behavior is **seed-if-empty**:
   load initial_content.json only when the Page table is empty.
   Existing content is never touched, so admin edits always survive
   a deploy or dyno restart. The fixture is a one-time bootstrap, not
   a source of truth.

   To force a fixture-driven rebuild (e.g. after editing the fixture
   file during a content rebuild phase), pass the explicit CLI flag:

       python manage.py bootstrap_prod --rebuild-from-fixture

   This upserts every record from initial_content.json by natural key
   (slug or singleton pk) and **will overwrite admin edits** for any
   record that exists in the fixture. Records in the DB but not in the
   fixture are left untouched. The flag is intentionally not exposed
   via an environment variable, so no Railway env var can accidentally
   trigger an overwrite from the Procfile chain.

2. Create a Django superuser from DJANGO_SUPERUSER_{USERNAME,EMAIL,
   PASSWORD} env vars if a user with that username does not already
   exist. Always runs.

Both steps are idempotent — running the command repeatedly is safe.

Deprecated: CONTENT_SYNC_MODE env var. Previously, setting it to "build"
would trigger a fixture rebuild on every Procfile boot, which silently
clobbered admin edits when the dyno restarted. The env var is now
ignored (a deprecation notice is printed if it's set). Use the
--rebuild-from-fixture CLI flag instead.
"""

import json
import os
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core import serializers
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.utils import OperationalError


# Only these models are touched by content sync.
# Value is the natural-key lookup field used to find an existing record.
#   'pk'   — use the fixture pk directly (singletons force pk=1 via save()).
#   'slug' — match on the unique slug field (stable across content changes).
CONTENT_KEY = {
    'website.siteconfig':          'pk',     # singleton (pk=1)
    'website.homepagepillar':      'pk',
    'website.page':                'slug',
    'website.narrativeblock':      'pk',
    'website.casestudy':           'slug',
    'website.enterpriseoverview':  'pk',     # singleton (pk=1)
    'website.enterprisefunction':  'slug',
    'website.innovationoverview':  'pk',     # singleton (pk=1)
    'website.perspective':         'slug',
    'website.perspectivesection':  'pk',
    'website.resumeversion':       'slug',
    'website.resumesection':       'pk',
    'website.connectpage':         'pk',     # singleton (pk=1)
}

FIXTURE_PATH = Path('website/fixtures/initial_content.json')


class Command(BaseCommand):
    help = (
        'Idempotent production bootstrap: seed content if DB empty + create '
        'superuser from env. Use --rebuild-from-fixture to force an upsert.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--rebuild-from-fixture',
            action='store_true',
            help=(
                'Force-upsert every record from initial_content.json into '
                'the DB by natural key. WILL OVERWRITE ADMIN EDITS for '
                'records in the fixture. Manual one-shot only — never '
                'wired into the Procfile.'
            ),
        )

    def handle(self, *args, **options):
        # Deprecation notice for the old env-var-driven mode. Any value is
        # now ignored — the only way to trigger a rebuild is the CLI flag,
        # which prevents a Railway env var from silently clobbering admin
        # edits on every dyno restart.
        legacy_mode = os.environ.get('CONTENT_SYNC_MODE')
        if legacy_mode:
            self.stdout.write(
                f'NOTE: CONTENT_SYNC_MODE={legacy_mode!r} is set but is '
                'now IGNORED. Admin edits are the source of truth. To '
                'force a fixture rebuild, run: '
                'python manage.py bootstrap_prod --rebuild-from-fixture'
            )

        if options.get('rebuild_from_fixture'):
            self.stdout.write(
                'Rebuild requested via --rebuild-from-fixture. Admin edits '
                'for fixture-listed records will be overwritten.'
            )
            self._sync_content()
        else:
            self._seed_if_empty()

        self._maybe_create_superuser()

    # ------------------------------------------------------------------
    # Run mode — seed only if DB is empty. Preserves all admin edits.
    # ------------------------------------------------------------------
    def _seed_if_empty(self):
        from website.models import Page

        try:
            if Page.objects.exists():
                self.stdout.write('Content already present — skipping seed (run mode).')
                return
        except OperationalError:
            self.stderr.write('Page table missing — did migrations run? Skipping seed.')
            return

        self.stdout.write('Seeding initial_content.json (run mode, empty DB) ...')
        call_command('loaddata', 'initial_content', verbosity=1)
        self.stdout.write(self.style.SUCCESS('Content seeded.'))

    # ------------------------------------------------------------------
    # Build mode — upsert every fixture record by natural key. No deletes,
    # no full-table wipes. Records not in the fixture are untouched.
    # ------------------------------------------------------------------
    def _sync_content(self):
        if not FIXTURE_PATH.exists():
            self.stderr.write(f'Fixture not found at {FIXTURE_PATH}; skipping sync.')
            return

        try:
            raw = FIXTURE_PATH.read_text(encoding='utf-8')
            # Validate JSON early so we fail fast.
            json.loads(raw)
        except json.JSONDecodeError as exc:
            self.stderr.write(f'Fixture JSON invalid: {exc}')
            return

        created = 0
        updated = 0
        skipped_non_content = 0

        self.stdout.write('Syncing initial_content.json into DB (build mode) ...')

        with transaction.atomic():
            for deserialized in serializers.deserialize('json', raw):
                obj = deserialized.object
                meta = obj._meta
                label = f'{meta.app_label}.{meta.model_name}'

                if label not in CONTENT_KEY:
                    skipped_non_content += 1
                    continue

                Model = type(obj)
                key_field = CONTENT_KEY[label]

                if key_field == 'pk':
                    lookup = {'pk': obj.pk}
                else:
                    lookup = {key_field: getattr(obj, key_field)}

                existing = Model.objects.filter(**lookup).first()

                if existing is not None:
                    # Copy every concrete field from the deserialized obj onto
                    # the existing instance, then save. This leaves the
                    # existing pk intact (so FK children stay linked) and lets
                    # auto_now fields update naturally.
                    for field in meta.fields:
                        setattr(existing, field.attname, getattr(obj, field.attname))
                    existing.save()
                    updated += 1
                else:
                    # Brand-new record: deserialized obj carries its own pk.
                    # Save as-is. For singletons, the model's save() forces
                    # pk=1 regardless.
                    obj.save()
                    created += 1

        self.stdout.write(self.style.SUCCESS(
            f'Build sync complete: {created} created, {updated} updated, '
            f'{skipped_non_content} non-content records skipped.'
        ))

    # ------------------------------------------------------------------
    # Superuser (independent of CONTENT_SYNC_MODE)
    # ------------------------------------------------------------------
    def _maybe_create_superuser(self):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')

        if not username or not password:
            self.stdout.write(
                'DJANGO_SUPERUSER_USERNAME / _PASSWORD not set — skipping superuser creation.'
            )
            return

        User = get_user_model()
        if User.objects.filter(username=username).exists():
            self.stdout.write(f'Superuser "{username}" already exists — skipping.')
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        self.stdout.write(
            self.style.SUCCESS(f'Created superuser "{username}".')
        )
