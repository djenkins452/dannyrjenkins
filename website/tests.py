import importlib
import json
import re
from pathlib import Path

from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import CaseStudy, ContactPage, Perspective, ResumeSection, SiteConfig
from .services.vcard import build_vcard

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
            '/innovation/', '/perspectives/', '/connect/', '/contact/',
            '/resume/general/', '/resume/general/ats/',
        ]
        urls += [f'/case-studies/{s}/' for s in CaseStudy.objects.values_list('slug', flat=True)]
        urls += [f'/perspectives/{s}/' for s in Perspective.objects.values_list('slug', flat=True)]
        for url in urls:
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_default_meta_description_is_employer_neutral(self):
        body = self.client.get('/').content.decode()
        self.assertIn('content="Healthcare HRIS leader connecting people, technology,', body)
        self.assertNotIn('Director of Compensation, HRIS, and Payroll', body)
        self.assertNotIn('Director of HRIS, Compensation, and Payroll', body)


class ContactPageTests(TestCase):
    """/contact/ and its .vcf are printed on business cards: they must stay put."""

    def _vcard(self):
        return self.client.get('/contact/contact.vcf')

    def test_permanent_urls(self):
        self.assertEqual(reverse('contact'), '/contact/')
        self.assertEqual(ContactPage.CANONICAL_URL, 'https://dannyrjenkins.com/contact/')

    def test_page_is_standalone_with_no_links_to_the_site(self):
        SiteConfig.objects.update_or_create(
            pk=1, defaults={'contact_email': 'footer@example.com'},
        )
        html = self.client.get('/contact/').content.decode()
        self.assertEqual(re.findall(r'<a\b[^>]*\bhref="([^"]*)"', html), [
            '/contact/contact.vcf',
            'mailto:djenki11@CovHlth.com',
            'tel:+14233094701',
        ])
        for removed in ('<header', '<nav', '<footer', 'footer@example.com'):
            self.assertNotIn(removed, html)
        self.assertIn('<meta name="robots" content="noindex" />', html)

    def test_other_pages_keep_header_and_footer(self):
        html = self.client.get('/connect/').content.decode()
        for kept in ('<header', '<nav', '<footer'):
            self.assertIn(kept, html)
        self.assertNotIn('noindex', html)

    def test_page_is_public_and_shows_every_detail(self):
        response = self.client.get('/contact/')
        self.assertEqual(response.status_code, 200)
        for text in (
            'Danny R. Jenkins', 'Director of HRIS', 'Covenant Health',
            'djenki11@CovHlth.com', '423-309-4701', 'Save Contact',
        ):
            self.assertContains(response, text)

    def test_page_action_links(self):
        response = self.client.get('/contact/')
        self.assertContains(response, 'href="mailto:djenki11@CovHlth.com"')
        self.assertContains(response, 'href="tel:+14233094701"')
        self.assertContains(response, 'href="/contact/contact.vcf"')

    def test_download_is_public_with_download_headers(self):
        response = self._vcard()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/vcard; charset=utf-8')
        self.assertEqual(
            response['Content-Disposition'],
            'attachment; filename="danny-r-jenkins.vcf"',
        )

    def test_vcard_contents(self):
        self.assertEqual(self._vcard().content.decode(), (
            'BEGIN:VCARD\r\n'
            'VERSION:3.0\r\n'
            'N:Jenkins;Danny;R.;;\r\n'
            'FN:Danny R. Jenkins\r\n'
            'ORG:Covenant Health\r\n'
            'TITLE:Director of HRIS\r\n'
            'EMAIL;TYPE=INTERNET;TYPE=WORK:djenki11@CovHlth.com\r\n'
            'TEL;TYPE=CELL;TYPE=VOICE:+14233094701\r\n'
            'URL:https://dannyrjenkins.com/contact/\r\n'
            'END:VCARD\r\n'
        ))

    def test_vcard_url_ignores_request_host(self):
        response = self.client.get('/contact/contact.vcf', HTTP_HOST='www.beacon-innovation.com')
        self.assertContains(response, 'URL:https://dannyrjenkins.com/contact/')

    def test_one_edit_updates_page_and_download(self):
        page = ContactPage.load()
        page.job_title = 'Vice President, HR; Systems'
        page.cell_phone = '+18655550100'
        page.save()
        html = self.client.get('/contact/').content.decode()
        card = self._vcard().content.decode()
        self.assertIn('Vice President, HR; Systems', html)
        self.assertIn('865-555-0100', html)
        self.assertIn('href="tel:+18655550100"', html)
        self.assertIn('TITLE:Vice President\\, HR\\; Systems\r\n', card)
        self.assertIn('TEL;TYPE=CELL;TYPE=VOICE:+18655550100\r\n', card)

    def test_long_lines_fold_at_75_octets_without_breaking_characters(self):
        page = ContactPage(job_title='Résumé ' * 30)
        raw = build_vcard(page).encode('utf-8')
        for line in raw.split(b'\r\n'):
            self.assertLessEqual(len(line), 75)
            line.decode('utf-8')  # Raises if a character was split.
        unfolded = raw.decode('utf-8').replace('\r\n ', '')
        self.assertIn(f'TITLE:{page.job_title}\r\n', unfolded)

    def test_phone_must_be_international(self):
        page = ContactPage.load()
        for bad in ('423-309-4701', '4233094701', '+14233094701\n'):
            page.cell_phone = bad
            with self.assertRaises(ValidationError):
                page.full_clean()
        page.cell_phone = '+14233094701'
        page.full_clean()

    def test_only_one_record_and_admin_opens_it(self):
        ContactPage(job_title='Second save').save()
        self.assertEqual(ContactPage.objects.count(), 1)
        admin_user = get_user_model().objects.create_superuser('staff', password='test-only')
        self.client.force_login(admin_user)
        response = self.client.get('/admin/website/contactpage/')
        self.assertRedirects(response, '/admin/website/contactpage/1/change/')
