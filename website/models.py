from django.db import models
from tinymce.models import HTMLField


class SiteConfig(models.Model):
    """Singleton: global site strings editable from admin."""

    homepage_headline = models.CharField(
        max_length=200,
        default='Leading HR Transformation at Scale, Pioneering Personal AI Systems',
    )
    homepage_subheadline = HTMLField(
        blank=True,
        verbose_name='Homepage positioning statement',
        help_text=(
            'Short positioning statement under the headline. Should define '
            'enterprise leadership scope and systems-thinking approach. '
            '2–3 sentences max.'
        ),
    )
    enterprise_section_intro = HTMLField(
        blank=True,
        help_text='Intro paragraph above the three enterprise pillars.',
    )
    innovation_section_intro = HTMLField(
        blank=True,
        help_text='Intro paragraph above the three innovation highlights.',
    )
    contact_email = models.EmailField(blank=True)
    linkedin_url = models.URLField(blank=True)

    class Meta:
        verbose_name = 'Site Configuration'
        verbose_name_plural = 'Site Configuration'

    def __str__(self):
        return 'Site Configuration'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Page(models.Model):
    """A narrative page composed of ordered NarrativeBlocks.

    Used for /profile/ and future narrative pages. The homepage is composed
    from SiteConfig + HomepagePillar, not from a Page record — the homepage
    has a fixed, pillar-driven structure and does not need arbitrary blocks.
    """

    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=200)
    eyebrow = models.CharField(
        max_length=80,
        blank=True,
        help_text='Small uppercase label above the page title, e.g. "EXECUTIVE PROFILE".',
    )
    intro = HTMLField(
        blank=True,
        help_text='Optional lead paragraph under the title.',
    )
    seo_title = models.CharField(max_length=120, blank=True)
    seo_description = models.CharField(max_length=300, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class NarrativeBlock(models.Model):
    """Ordered content block belonging to a Page.

    `heading` is a structured field (plain text, design-controlled typography).
    `body` is TinyMCE-restricted rich text: paragraphs, bold/italic, lists,
    links. No headings or style attributes reach the output.
    """

    page = models.ForeignKey(
        Page,
        related_name='blocks',
        on_delete=models.CASCADE,
    )
    order = models.PositiveIntegerField(default=0)
    eyebrow = models.CharField(
        max_length=80,
        blank=True,
        help_text='Optional small label above heading.',
    )
    heading = models.CharField(max_length=200, blank=True)
    body = HTMLField(blank=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.page.slug} · {self.heading or f"block #{self.order}"}'


class CaseStudy(models.Model):
    """A case study rendered with a fixed four-section structure.

    Problem / Role / Approach / Outcome are stored as separate fields
    (not one TinyMCE body) so the detail template can style each section
    consistently and the structure cannot drift between studies.
    """

    ENTERPRISE = 'ENTERPRISE'
    INNOVATION = 'INNOVATION'
    CATEGORY_CHOICES = [
        (ENTERPRISE, 'Enterprise'),
        (INNOVATION, 'Innovation'),
    ]

    slug = models.SlugField(unique=True, max_length=120)
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    summary = models.CharField(
        max_length=400,
        help_text='Shown on the case studies index. One or two sentences.',
    )

    problem = HTMLField(
        help_text='The strategic or operational problem. Written for an executive reader.',
    )
    role = HTMLField(
        help_text='Your role, remit, and reporting context.',
    )
    approach = HTMLField(
        help_text='How you approached the problem. Sequencing, decisions, tradeoffs.',
    )
    outcome = HTMLField(
        help_text='The measured result. Quantify where possible.',
    )

    order = models.PositiveIntegerField(
        default=0,
        help_text='Lower numbers sort first on the index page.',
    )
    published = models.BooleanField(default=True)
    published_at = models.DateField(null=True, blank=True)

    seo_title = models.CharField(max_length=120, blank=True)
    seo_description = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ['order', '-published_at', 'id']
        verbose_name_plural = 'Case studies'

    def __str__(self):
        return self.title


class EnterpriseOverview(models.Model):
    """Singleton: top-of-page overview for /enterprise-leadership/.

    Kept minimal (scope + impact) on purpose. The deeper structure lives
    in EnterpriseFunction records below.
    """

    scope = HTMLField(
        blank=True,
        help_text='Scale of responsibility — employees, systems, divisions.',
    )
    impact = HTMLField(
        blank=True,
        help_text='What the function is measured on; transformation outcomes.',
    )
    system_integration = HTMLField(
        blank=True,
        verbose_name='How the system works together',
        help_text=(
            'Closing paragraph at the bottom of the Enterprise Leadership page. '
            'Explain how Compensation, HRIS, and Payroll operate as one system — '
            'not three parallel jobs.'
        ),
    )

    class Meta:
        verbose_name = 'Enterprise Overview'
        verbose_name_plural = 'Enterprise Overview'

    def __str__(self):
        return 'Enterprise Overview'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class EnterpriseFunction(models.Model):
    """One function under the director remit: Compensation, HRIS, Payroll.

    Three fixed sub-sections per function — responsibilities, systems led,
    role in the organization — all as TinyMCE-restricted HTML. Structure is
    enforced by schema so the Enterprise Leadership page reads uniformly
    no matter which function you look at.
    """

    slug = models.SlugField(unique=True, max_length=60)
    title = models.CharField(max_length=80)
    summary = models.CharField(
        max_length=300,
        blank=True,
        help_text='One-line framing shown under the function title.',
    )
    responsibilities = HTMLField(help_text='What this function leads.')
    systems_led = HTMLField(help_text='Systems, tools, and programs owned.')
    organizational_role = HTMLField(
        help_text='How this function fits into the organization.',
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


class InnovationOverview(models.Model):
    """Singleton for /innovation/.

    Structured sections — Beacon positioning, WLJ overview, architecture
    caption, AI Chief of Staff. The Data → Signals → Decisions diagram is
    design, not content, and lives in the template as inline SVG.
    """

    intro = HTMLField(
        blank=True,
        help_text='Page lead paragraph. Keep brief.',
    )
    beacon_positioning = HTMLField(
        blank=True,
        verbose_name='Beacon Innovation positioning',
        help_text='What Beacon Innovation, LLC is and why it exists separately from any enterprise role.',
    )
    wlj_positioning = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='WLJ positioning line',
        help_text=(
            'One-line framing statement rendered as a pull-quote above the '
            'WLJ overview. Keep to a single sentence or two short sentences.'
        ),
    )
    wlj_overview = HTMLField(
        blank=True,
        verbose_name='Whole Life Journey overview',
        help_text='What WLJ is, why it was built, who it is for.',
    )
    architecture_caption = HTMLField(
        blank=True,
        help_text=(
            'Paragraph accompanying the Data → Signals → Decisions diagram. '
            'Explain the three stages in plain language.'
        ),
    )
    practical_example = HTMLField(
        blank=True,
        verbose_name='Architecture — in-practice example',
        help_text=(
            'A concrete scenario showing the pipeline producing one decision '
            '(e.g. prioritizing a quick task before a meeting). Grounds the '
            'abstract architecture in real use.'
        ),
    )
    chief_of_staff = HTMLField(
        blank=True,
        verbose_name='AI Chief of Staff concept',
        help_text='The AI layer as an executive Chief of Staff — not a chatbot metaphor.',
    )
    what_this_demonstrates = HTMLField(
        blank=True,
        verbose_name='What this demonstrates',
        help_text=(
            'Closing section. What the WLJ work demonstrates about the '
            'author: systems thinking, AI application, cross-domain '
            'integration, focus on decision-making.'
        ),
    )

    class Meta:
        verbose_name = 'Innovation Overview'
        verbose_name_plural = 'Innovation Overview'

    def __str__(self):
        return 'Innovation Overview'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Perspective(models.Model):
    """A Perspective — an argument presented as an operator would write it.

    Sections are separate (PerspectiveSection records) so the H2 headings
    stay structured and consistent across pieces. The editor never writes
    headings inside TinyMCE.
    """

    slug = models.SlugField(unique=True, max_length=120)
    title = models.CharField(max_length=200)
    deck = models.CharField(
        max_length=300,
        blank=True,
        help_text='Short subtitle / summary — shown under the title and on index cards.',
    )
    eyebrow = models.CharField(
        max_length=40,
        blank=True,
        help_text='Category label (e.g. "COMPENSATION", "HRIS", "SYSTEMS").',
    )
    lead = HTMLField(
        blank=True,
        help_text='Opening paragraph — the argument in one paragraph. Serif lead styling.',
    )
    closing = HTMLField(
        blank=True,
        help_text='Final closing paragraph. Rendered below the sections.',
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text='Lower numbers sort first on the index page.',
    )
    published = models.BooleanField(default=True)
    published_at = models.DateField(null=True, blank=True)

    seo_title = models.CharField(max_length=120, blank=True)
    seo_description = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ['order', '-published_at', 'id']

    def __str__(self):
        return self.title


class PerspectiveSection(models.Model):
    """Ordered section within a Perspective.

    heading is a structured CharField (design controls typography).
    body is TinyMCE-restricted HTML.
    """

    perspective = models.ForeignKey(
        Perspective,
        related_name='sections',
        on_delete=models.CASCADE,
    )
    order = models.PositiveIntegerField(default=0)
    heading = models.CharField(max_length=200)
    body = HTMLField()

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.perspective.slug} · {self.heading}'


class ResumePage(models.Model):
    """Singleton for /resume/ — the executive-level validation layer.

    Structured fields per resume section. Admin edits each labelled field;
    the template renders the section only if the field is populated.
    """

    positioning_line = models.CharField(
        max_length=300,
        blank=True,
        help_text='One line below the name at the top. Positioning, not title.',
    )
    executive_summary = HTMLField(
        blank=True,
        help_text='2–3 lines. Do not duplicate the Enterprise Leadership page.',
    )
    current_role_title = models.CharField(max_length=200, blank=True)
    current_role_org = models.CharField(max_length=200, blank=True)
    current_role_dates = models.CharField(
        max_length=100,
        blank=True,
        help_text='e.g. "2023 — Present"',
    )
    current_role_bullets = HTMLField(
        blank=True,
        help_text='4–6 bullets. Use the list button in the editor. Declarative verbs, no "responsible for".',
    )
    prior_roles = HTMLField(
        blank=True,
        help_text='Condensed — one or two lines each. No bullet list for prior roles.',
    )
    education = HTMLField(blank=True)
    key_impact = HTMLField(
        blank=True,
        verbose_name='Key impact highlights',
        help_text='Optional. Bulleted.',
    )

    class Meta:
        verbose_name = 'Resume Page'
        verbose_name_plural = 'Resume Page'

    def __str__(self):
        return 'Resume Page'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class HomepagePillar(models.Model):
    """A pillar on the homepage. Category routes it to one of the two columns."""

    ENTERPRISE = 'ENTERPRISE'
    INNOVATION = 'INNOVATION'
    CATEGORY_CHOICES = [
        (ENTERPRISE, 'Enterprise Leadership'),
        (INNOVATION, 'Innovation'),
    ]

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=120)
    body = HTMLField(
        blank=True,
        help_text='Short description (2–3 sentences).',
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['category', 'order', 'id']

    def __str__(self):
        return f'[{self.get_category_display()}] {self.title}'
