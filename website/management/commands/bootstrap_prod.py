"""Idempotent production bootstrap.

Runs on every deploy (from Procfile) and performs two actions safely:

1. Seeds initial_content.json if the database has no Page records yet.
2. Creates a Django superuser from DJANGO_SUPERUSER_{USERNAME,EMAIL,PASSWORD}
   env vars if a user with that username does not already exist.

Both steps are idempotent — running the command repeatedly is safe.
"""

import os

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = 'Idempotent production bootstrap: seed content and create superuser from env.'

    def handle(self, *args, **options):
        self._maybe_seed_content()
        self._maybe_create_superuser()

    def _maybe_seed_content(self):
        """Load initial_content fixture only if the DB has no Page records."""
        from website.models import Page

        try:
            if Page.objects.exists():
                self.stdout.write('Content already present — skipping loaddata.')
                return
        except OperationalError:
            self.stderr.write('Page table missing — did migrations run? Skipping seed.')
            return

        self.stdout.write('Seeding initial_content.json ...')
        call_command('loaddata', 'initial_content', verbosity=1)
        self.stdout.write(self.style.SUCCESS('Content seeded.'))

    def _maybe_create_superuser(self):
        """Create a superuser from env vars if one with that username is missing."""
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
