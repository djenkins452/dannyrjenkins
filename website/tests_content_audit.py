"""Content audit, Nov 2026: titles, meta descriptions, Connect form, data fixes."""

import importlib
import json
import re
from html import unescape
from pathlib import Path

from django.apps import apps
from django.core import mail
from django.test import TestCase, override_settings

from .forms import ContactForm
from .models import (
    CaseStudy, ConnectPage, EnterpriseFunction, HomepagePillar, Page,
    Perspective, ResumeSection,
)

audit = importlib.import_module('website.migrations.0020_content_audit_2026_11')

ROOT = Path(__file__).resolve().parent.parent
BACKUP = ROOT / 'backups/content-audit-2026-11-08/pre_change_production_values.json'

DESCRIPTIONS = {
    '/': 'Healthcare HRIS leader connecting people, technology, and processes across the employee lifecycle. Founder of Beacon Innovation.',
    '/profile/': 'Danny R. Jenkins’s approach to people leadership, HR technology, systems thinking, and operational improvement.',
    '/enterprise-leadership/': 'Broad HR expertise, workforce technology leadership, data governance, and practical approaches to developing teams and improving operations.',
    '/case-studies/': 'Selected work in healthcare HR leadership, workforce technology, operational improvement, and independent software development.',
    '/innovation/': 'Independent software projects through Beacon Innovation exploring connected information, automation, AI, and practical decision support.',
    '/perspectives/': 'Practical perspectives on HR, people leadership, workforce technology, data governance, and organizational improvement.',
    '/connect/': 'Connect with Danny R. Jenkins about HR leadership, workforce technology, software development, automation, and applied AI.',
}

# Must not appear anywhere on the public site outside /contact/.
STALE_PUBLIC = [
    'UT Medical', '6,000', 'academic medical center', 'Level 1',
    'Director of HRIS, Compensation, and Payroll', 'Covenant',
    'Executive conversation', 'Role discussion', 'Advisory / speaking',
    'Resume request', 'tailored resume', 'SubmitSend',
    'zero errors', 'no operational disruption',
]


def _title(html):
    return unescape(re.search(r'<title>(.*?)</title>', html, re.S).group(1).strip())


def _description(html):
    return unescape(re.search(r'<meta name="description" content="([^"]*)"', html).group(1))


def _public_urls():
    urls = list(DESCRIPTIONS) + ['/resume/general/', '/resume/general/ats/']
    urls += [f'/case-studies/{s}/' for s in CaseStudy.objects.values_list('slug', flat=True)]
    urls += [f'/perspectives/{s}/' for s in Perspective.objects.values_list('slug', flat=True)]
    return urls


class TitleAndDescriptionTests(TestCase):
    fixtures = ['initial_content']

    def test_primary_page_descriptions(self):
        for url, expected in DESCRIPTIONS.items():
            html = self.client.get(url).content.decode()
            self.assertEqual(_description(html), expected, url)

    def test_seo_title_with_owner_name_is_used_verbatim(self):
        html = self.client.get('/perspectives/system-fragmentation-is-inherited/').content.decode()
        self.assertEqual(_title(html), 'Operational Fragmentation Grows Over Time | Danny R. Jenkins')

    def test_every_title_names_the_owner_exactly_once(self):
        for url in _public_urls():
            title = _title(self.client.get(url).content.decode())
            self.assertEqual(title.count('Danny R. Jenkins'), 1, f'{url}: {title}')
            self.assertNotIn('— Perspectives', title, url)
            self.assertNotIn('— Case Study', title, url)

    def test_title_without_owner_name_gets_it_appended_once(self):
        Perspective.objects.filter(slug='hris-is-a-decision-engine').update(seo_title='')
        CaseStudy.objects.filter(slug='payroll-operations').update(seo_title='Payroll Work')
        p = self.client.get('/perspectives/hris-is-a-decision-engine/').content.decode()
        c = self.client.get('/case-studies/payroll-operations/').content.decode()
        self.assertEqual(_title(p), 'HRIS supports workforce operational alignment — Danny R. Jenkins')
        self.assertEqual(_title(c), 'Payroll Work — Danny R. Jenkins')
        self.assertEqual(_title(self.client.get('/profile/').content.decode()), 'Executive Profile — Danny R. Jenkins')

    def test_no_stale_wording_on_public_pages(self):
        for url in _public_urls():
            html = unescape(self.client.get(url).content.decode())
            for phrase in STALE_PUBLIC:
                self.assertNotIn(phrase, html, f'{phrase!r} on {url}')


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    EMAIL_HOST_USER='inbox@example.test',
)
class ConnectFormTests(TestCase):
    fixtures = ['initial_content']

    def _post(self, inquiry):
        return self.client.post('/connect/', {
            'name': 'Test Person', 'email': 'test@example.com',
            'inquiry_type': inquiry, 'message': 'Hello',
        })

    def test_button_label_and_options(self):
        html = self.client.get('/connect/').content.decode()
        self.assertEqual(
            re.findall(r'<button type="submit" class="btn-submit">(.*?)</button>', html),
            ['Send message'],
        )
        options = [unescape(o) for o in re.findall(r'<option value="[^"]*"[^>]*>(.*?)</option>', html)]
        self.assertEqual(options, [
            'Professional networking', 'HR and workforce technology',
            'Software, automation, and AI', 'Speaking or knowledge sharing', 'Other',
        ])

    def test_blank_stored_label_falls_back_to_send_message(self):
        ConnectPage.objects.update(submit_button_label='')
        self.assertContains(self.client.get('/connect/'), '>Send message</button>')

    def test_each_current_option_sends_one_notification(self):
        for value, label in ContactForm.INQUIRY_CHOICES:
            mail.outbox.clear()
            response = self._post(value)
            self.assertContains(response, 'role="status"')
            self.assertEqual(len(mail.outbox), 1, value)
            sent = mail.outbox[0]
            self.assertEqual(sent.subject, f'Website inquiry ({label}) from Test Person')
            self.assertIn(f'Inquiry type: {label}\n', sent.body)
            self.assertEqual(sent.reply_to, ['test@example.com'])
            self.assertEqual(sent.to, ['inbox@example.test'])
            self.assertNotIn('resume', sent.subject.lower())

    def test_legacy_value_from_stale_page_is_kept_not_reinterpreted(self):
        response = self._post('resume')
        self.assertContains(response, 'role="status"')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Inquiry type: Resume request (legacy option)\n', mail.outbox[0].body)
        # Retired options are never offered again.
        self.assertNotContains(self.client.get('/connect/'), 'value="resume"')

    def test_unknown_value_is_rejected(self):
        response = self._post('job_offer')
        self.assertEqual(len(mail.outbox), 0)
        self.assertNotContains(response, 'role="status"')
        self.assertContains(response, 'form-field__error')

    def test_direct_resume_access_is_unchanged(self):
        self.assertEqual(self.client.get('/resume/general/').status_code, 200)
        self.assertEqual(self.client.get('/resume/general/ats/').status_code, 200)


class AuditMigrationTests(TestCase):
    """Migration 0020 against the exact values production held."""

    fixtures = ['initial_content']

    def setUp(self):
        self.records = json.loads(BACKUP.read_text(encoding='utf-8'))['records']
        for rec in self.records:
            apps.get_model(rec['model']).objects.filter(**rec['lookup']).update(
                **{rec['field']: rec['value']},
            )

    def _values(self):
        return [
            getattr(apps.get_model(r['model']).objects.get(**r['lookup']), r['field'])
            for r in self.records
        ]

    def test_forward_applies_approved_text(self):
        audit.forwards(apps, None)
        wlj = HomepagePillar.objects.get(category='INNOVATION', title='Whole Life Journey')
        cos = HomepagePillar.objects.get(category='INNOVATION', title='AI Chief of Staff')
        self.assertIn('A personal platform connecting faith, health, journaling, tasks, and goals.', wlj.body)
        self.assertIn('keep the user in control.', cos.body)
        kairos = HomepagePillar.objects.get(category='INNOVATION', title='Kairos Core HQ')
        self.assertIn('Its aim is to help leaders evaluate competing demands', kairos.body)
        self.assertIn('coordinate daily work with longer-term goals.', kairos.body)
        self.assertNotIn('drive disciplined execution', kairos.body)
        self.assertEqual(
            Page.objects.get(slug='profile').seo_description,
            DESCRIPTIONS['/profile/'],
        )
        highlights = ResumeSection.objects.get(version__slug='general', section_type='HIGHLIGHTS')
        self.assertEqual(highlights.content.count('<li>'), 7)
        self.assertNotIn('<p>', highlights.content)
        self.assertEqual(ConnectPage.load().submit_button_label, 'Send message')

    def test_pillar_category_and_order_are_preserved(self):
        before = list(HomepagePillar.objects.values_list('category', 'title', 'order'))
        audit.forwards(apps, None)
        self.assertEqual(before, list(HomepagePillar.objects.values_list('category', 'title', 'order')))

    def test_forward_is_idempotent(self):
        audit.forwards(apps, None)
        once = self._values()
        audit.forwards(apps, None)
        self.assertEqual(once, self._values())

    def test_admin_edits_are_left_untouched(self):
        HomepagePillar.objects.filter(title='Whole Life Journey').update(body='<p>Edited.</p>')
        ConnectPage.objects.update(submit_button_label='Get in touch')
        audit.forwards(apps, None)
        self.assertEqual(HomepagePillar.objects.get(title='Whole Life Journey').body, '<p>Edited.</p>')
        self.assertEqual(ConnectPage.load().submit_button_label, 'Get in touch')

    def test_broken_label_is_repaired(self):
        ConnectPage.objects.update(submit_button_label='SubmitSend message')
        audit.forwards(apps, None)
        self.assertEqual(ConnectPage.load().submit_button_label, 'Send message')

    def test_reverse_restores_prior_text_except_submit_label(self):
        before = self._values()
        audit.forwards(apps, None)
        audit.backwards(apps, None)
        self.assertEqual(before[:-1], self._values()[:-1])
        self.assertEqual(ConnectPage.load().submit_button_label, 'Send message')

    def test_highlights_render_as_seven_bullets(self):
        audit.forwards(apps, None)
        for url in ('/resume/general/', '/resume/general/ats/'):
            html = self.client.get(url).content.decode()
            self.assertEqual(html.count('<li>Led multidisciplinary teams'), 1, url)
            self.assertEqual(html.count('<li>Created independent software projects'), 1, url)


class EnterpriseFunctionTests(TestCase):
    fixtures = ['initial_content']

    def test_functions_render_in_order_with_new_titles(self):
        self.assertEqual(
            list(EnterpriseFunction.objects.values_list('slug', flat=True)),
            ['hr-strategy-employee-lifecycle', 'hr-technology-data-governance',
             'people-leadership-operational-improvement'],
        )
        html = unescape(self.client.get('/enterprise-leadership/').content.decode())
        titles = re.findall(r'<h3 class="function-block__title">(.*?)</h3>', html)
        self.assertEqual(titles, [
            'HR Strategy & Employee Lifecycle',
            'HR Technology & Data Governance',
            'People Leadership & Operational Improvement',
        ])

    def test_fixture_has_no_retired_function_slugs(self):
        data = json.loads((Path(__file__).resolve().parent / 'fixtures/initial_content.json').read_text())
        slugs = {o['fields']['slug'] for o in data if o['model'] == 'website.enterprisefunction'}
        self.assertFalse(slugs & {'compensation', 'hris', 'payroll'})


class PreservedContentTests(TestCase):
    fixtures = ['initial_content']

    def test_payroll_scale_wording_is_unchanged(self):
        self.assertContains(
            self.client.get('/case-studies/payroll-operations/'),
            'more than $30 million in monthly payroll',
        )

    def test_innovation_pillars_keep_order(self):
        self.assertEqual(
            list(HomepagePillar.objects.filter(category='INNOVATION').values_list('title', 'order')),
            [('Beacon Innovation, LLC', 1), ('Whole Life Journey', 2),
             ('Kairos Core HQ', 3), ('AI Chief of Staff', 4)],
        )
        html = self.client.get('/').content.decode()
        self.assertIn('coordinate daily work with longer-term goals.', html)
        self.assertLess(html.index('<h3>Kairos Core HQ</h3>'), html.index('<h3>AI Chief of Staff</h3>'))
