"""ResumeAssemblyService — internal narrative composition for /resume/.

Reads canonical site content (SiteConfig, EnterpriseOverview, InnovationOverview,
Profile narrative blocks, CaseStudy records) and composes a render-ready context
for the resume templates (executive HTML, ATS HTML, print-to-PDF). The service
does not duplicate content — it orchestrates existing governed fields.

Architecture rules this module obeys:

- Single source of truth (Architecture Law #1): every string the service emits
  comes from a model field; no string is hardcoded except the empty-body
  placeholder used when a section has neither a canonical source nor an admin-
  provided override.
- Override-wins: if a `ResumeSection.content` body is set, the assembly skips
  source composition for that section and uses the override verbatim.
- Side-effect free: the service reads only; it never writes back to the DB.
- One service, two templates: the same context dict feeds both the executive
  HTML view and the ATS HTML view. They differ only in presentation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from django.utils.html import format_html, format_html_join, mark_safe

from website.models import (
    CaseStudy,
    ConnectPage,  # imported for type-completeness; not currently read
    EnterpriseOverview,
    InnovationOverview,
    Page,
    ResumeSection,
    ResumeVersion,
    SiteConfig,
)


EMPTY_BODY_PLACEHOLDER = mark_safe(
    '<p class="muted">'
    '[Set this section\'s body in admin — no canonical source available.]'
    '</p>'
)


@dataclass
class AssembledIdentity:
    """The seven fields the resume header renders.

    name / email / linkedin come from SiteConfig (already canonical site-wide).
    headline is per-version (ResumeVersion.headline).
    phone / location / website are resume-specific SiteConfig fields.
    """

    name: str
    headline: str
    location: str
    email: str
    phone: str
    linkedin_url: str
    website_url: str

    @property
    def has_contact_line(self) -> bool:
        """True if any of email/phone/location is set — used by templates
        to decide whether to render the contact line at all."""
        return bool(self.email or self.phone or self.location)


@dataclass
class AssembledSection:
    """One section of the assembled resume, ordered.

    `body_html` is HTML-safe and ready for `|safe` in a template.
    `source_label` is admin-facing diagnostic text (shown only to staff in the
    ATS view's HTML comments) — useful to confirm assembly chose the right
    canonical source.
    """

    section_type: str
    heading: str
    body_html: str
    source_label: str


class ResumeAssemblyService:
    """Compose a render-ready context for one ResumeVersion."""

    def __init__(self, version: ResumeVersion):
        self.version = version
        self.config = SiteConfig.load()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def assemble(self) -> dict:
        """Return the context dict consumed by resume.html and resume_ats.html."""
        return {
            'version': self.version,
            'identity': self._identity(),
            'sections': self._sections(),
            'site_config': self.config,
        }

    # ------------------------------------------------------------------
    # Identity (resume header)
    # ------------------------------------------------------------------
    def _identity(self) -> AssembledIdentity:
        return AssembledIdentity(
            name=self.config.brand_wordmark or 'Danny R. Jenkins',
            headline=self.version.headline or '',
            location=self.config.resume_location or '',
            email=self.config.contact_email or '',
            phone=self.config.resume_phone or '',
            linkedin_url=self.config.linkedin_url or '',
            website_url=self.config.site_url or 'https://dannyrjenkins.com',
        )

    # ------------------------------------------------------------------
    # Sections
    # ------------------------------------------------------------------
    def _sections(self) -> List[AssembledSection]:
        out: List[AssembledSection] = []
        for s in self.version.sections.all().order_by('order'):
            out.append(self._assemble_section(s))
        return out

    def _assemble_section(self, section: ResumeSection) -> AssembledSection:
        # Override-wins: an authored body takes precedence over assembly.
        if section.content:
            return AssembledSection(
                section_type=section.section_type,
                heading=section.get_display_heading(),
                body_html=section.content,
                source_label='admin override (ResumeSection.content)',
            )

        # No override → compose from canonical source per section_type.
        body_html, source_label = self._compose_from_canonical(section)
        return AssembledSection(
            section_type=section.section_type,
            heading=section.get_display_heading(),
            body_html=body_html,
            source_label=source_label,
        )

    def _compose_from_canonical(self, section: ResumeSection):
        """Return (body_html, source_label) composed from canonical site
        content for the given section type. Returns the empty-body placeholder
        when no canonical source exists for the section type."""

        if section.section_type == ResumeSection.SUMMARY:
            return self._compose_summary()

        if section.section_type == ResumeSection.CURRENT_ROLE:
            return self._compose_current_role()

        if section.section_type == ResumeSection.HIGHLIGHTS:
            return self._compose_highlights()

        # PRIOR_ROLES / EDUCATION / CUSTOM have no canonical site source.
        return (
            EMPTY_BODY_PLACEHOLDER,
            f'no canonical source for {section.section_type}; awaiting admin body',
        )

    # ------------------------------------------------------------------
    # Per-section canonical composers
    # ------------------------------------------------------------------
    def _compose_summary(self):
        """Pull the executive summary from the source the version selects."""
        source = self.version.summary_source

        if source == ResumeVersion.SUMMARY_HOMEPAGE_SUBHEADLINE:
            body = self.config.homepage_subheadline
            label = 'SiteConfig.homepage_subheadline'
        elif source == ResumeVersion.SUMMARY_ENTERPRISE_HERO_LEAD:
            body = EnterpriseOverview.load().hero_lead
            label = 'EnterpriseOverview.hero_lead'
        elif source == ResumeVersion.SUMMARY_PROFILE_INTRO:
            try:
                page = Page.objects.get(slug='profile')
                body = page.intro
                label = 'Page(slug=profile).intro'
            except Page.DoesNotExist:
                body = ''
                label = 'Profile page not found'
        else:
            # MANUAL — section.content was blank, so render the placeholder.
            return (EMPTY_BODY_PLACEHOLDER, 'summary_source=MANUAL with blank Content')

        if not body:
            return (EMPTY_BODY_PLACEHOLDER, f'{label} (empty)')
        return (mark_safe(body), label)

    def _compose_current_role(self):
        """Compose CURRENT_ROLE from EnterpriseOverview scope + impact.

        Concatenates the two HTMLField bodies. Both are TinyMCE-restricted so
        the combined HTML is safe.
        """
        overview = EnterpriseOverview.load()
        parts = []
        labels = []
        if overview.scope:
            parts.append(overview.scope)
            labels.append('scope')
        if overview.impact:
            parts.append(overview.impact)
            labels.append('impact')

        # Optional: include a one-line Innovation pointer when the version
        # asks for it. Keeps the resume narrative coherent for audiences
        # where the AI/Innovation work is on-message.
        if self.version.include_innovation:
            innov = InnovationOverview.load()
            if innov.intro:
                parts.append(innov.intro)
                labels.append('InnovationOverview.intro')

        if not parts:
            return (
                EMPTY_BODY_PLACEHOLDER,
                'EnterpriseOverview.scope/impact both empty',
            )

        body = mark_safe(''.join(parts))
        return (body, f'EnterpriseOverview ({" + ".join(labels)})')

    def _compose_highlights(self):
        """Render the version's featured CaseStudy records as a list.

        We only surface published case studies. Each entry renders the
        title (linked back to the live case-study URL) and the summary —
        consistent with how the public site lists them.
        """
        studies = (
            self.version.featured_case_studies
            .filter(published=True)
            .order_by('order', '-published_at')
        )

        if not studies.exists():
            return (
                EMPTY_BODY_PLACEHOLDER,
                'featured_case_studies empty (no highlights selected)',
            )

        items = format_html_join(
            '\n',
            '<li><strong>{}</strong> — {} '
            '<span class="muted">(see {}/case-studies/{}/)</span></li>',
            (
                (s.title, s.summary, self.config.site_url.rstrip('/'), s.slug)
                for s in studies
            ),
        )
        body = format_html('<ul>{}</ul>', items)
        return (body, f'featured_case_studies ({studies.count()})')
