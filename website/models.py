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
