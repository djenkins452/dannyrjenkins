import importlib
import json
from pathlib import Path

from django.apps import apps
from django.test import TestCase

from .models import CaseStudy, Perspective, ResumeSection

alignment = importlib.import_module('website.migrations.0018_align_professional_facts')

BACKUP = Path(__file__).resolve().parent.parent / (
    'backups/fact-alignment-2026-09-30/pre_change_production_values.json'
)

# Phrases that must never render as current fact after the alignment.
STALE_PHRASES = [
    'no operational disruption',
    'Live on schedule',
    'went live on schedule',
    'partnering with Segal to accelerate the work',
    'offer-stage loss',
    '$33M disbursed monthly',
    'Director of Compensation, HRIS, and Payroll',
]


class ProfessionalFactAlignmentTests(TestCase):
    """Migration 0018 against a copy of the production values it corrects."""

    fixtures = ['initial_content']

    def setUp(self):
        # Put the exact pre-change production values in place, so the test
        # exercises the same text the migration meets in production.
        self.snapshot = json.loads(BACKUP.read_text(encoding='utf-8'))['records']
        for rec in self.snapshot:
            Model = apps.get_model(rec['model'])
            Model.objects.filter(**rec['lookup']).update(**{rec['field']: rec['value']})

    def _values(self):
        out = []
        for rec in self.snapshot:
            Model = apps.get_model(rec['model'])
            out.append(getattr(Model.objects.get(**rec['lookup']), rec['field']))
        return out

    def test_forward_corrects_every_stale_claim(self):
        alignment.forwards(apps, None)
        text = '\n'.join(self._values())
        for phrase in STALE_PHRASES:
            self.assertNotIn(phrase, text)
        self.assertIn('active enterprise compensation redesign in partnership with Segal', text)
        self.assertIn('November 2025', text)
        self.assertIn('delayed go-live three times', text)
        self.assertIn('Director of HRIS, Compensation, and Payroll', text)
        self.assertIn('$500M+', text)

    def test_completed_compensation_work_is_preserved(self):
        alignment.forwards(apps, None)
        study = CaseStudy.objects.get(slug='compensation-transformation')
        self.assertIn('I led the rebuild end to end', study.role)
        self.assertIn('Managers could clearly explain pay decisions.', study.outcome)
        self.assertIn('Compensation moved from a reactive', study.outcome)

    def test_forward_is_idempotent(self):
        alignment.forwards(apps, None)
        once = self._values()
        alignment.forwards(apps, None)
        self.assertEqual(once, self._values())

    def test_reverse_restores_exact_prior_values(self):
        before = self._values()
        alignment.forwards(apps, None)
        self.assertNotEqual(before, self._values())
        alignment.backwards(apps, None)
        self.assertEqual(before, self._values())

    def test_admin_edited_field_is_left_untouched(self):
        section = ResumeSection.objects.get(version__slug='general', section_type='HIGHLIGHTS')
        section.content = '<p>Edited in admin.</p>'
        section.save()
        alignment.forwards(apps, None)
        section.refresh_from_db()
        self.assertEqual(section.content, '<p>Edited in admin.</p>')

    def test_corrected_pages_render(self):
        alignment.forwards(apps, None)
        pages = {
            '/case-studies/compensation-transformation/': ['partnership with Segal', 'ongoing'],
            '/resume/general/': ['Director of HRIS, Compensation, and Payroll', 'November 2025', 'Executive Summary'],
            '/resume/general/ats/': ['Director of HRIS, Compensation, and Payroll', 'November 2025'],
        }
        for url, expected in pages.items():
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200, url)
            body = resp.content.decode()
            for phrase in expected:
                self.assertIn(phrase, body, f'{phrase!r} missing on {url}')
            for phrase in STALE_PHRASES:
                self.assertNotIn(phrase, body, f'{phrase!r} still on {url}')


class FixtureFactTests(TestCase):
    """A fresh seed must not reintroduce the corrected claims."""

    def test_fixture_has_no_stale_claims(self):
        path = Path(__file__).resolve().parent / 'fixtures/initial_content.json'
        text = path.read_text(encoding='utf-8')
        for phrase in STALE_PHRASES:
            self.assertNotIn(phrase, text)


class PublicUrlRegressionTests(TestCase):
    fixtures = ['initial_content']

    def test_public_pages_render(self):
        urls = [
            '/', '/profile/', '/enterprise-leadership/', '/case-studies/',
            '/innovation/', '/perspectives/', '/connect/',
            '/resume/general/', '/resume/general/ats/',
        ]
        urls += [f'/case-studies/{s}/' for s in CaseStudy.objects.values_list('slug', flat=True)]
        urls += [f'/perspectives/{s}/' for s in Perspective.objects.values_list('slug', flat=True)]
        for url in urls:
            self.assertEqual(self.client.get(url).status_code, 200, url)
