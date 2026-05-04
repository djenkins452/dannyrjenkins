from django.db import models
from tinymce.models import HTMLField


class SiteConfig(models.Model):
    """Singleton: global site strings editable from admin."""

    homepage_headline = models.CharField(
        max_length=200,
        default='Leading HR Transformation at Scale, Pioneering Personal AI Systems',
        help_text='Appears on the homepage hero as the large H1 headline.',
    )
    homepage_positioning_line = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='Homepage positioning line',
        help_text=(
            'Appears on the homepage hero, between the headline and the '
            'supporting paragraph. One sentence; plain text. Sized between '
            'headline and body so the eye reads it as a natural extension '
            'of the headline.'
        ),
    )
    homepage_subheadline = HTMLField(
        blank=True,
        verbose_name='Homepage positioning statement',
        help_text=(
            'Appears on the homepage hero, below the positioning line, as the '
            'supporting paragraph. Should define enterprise leadership scope '
            'and systems-thinking approach. 2–3 sentences max.'
        ),
    )
    homepage_vision = HTMLField(
        blank=True,
        verbose_name='Homepage vision section',
        help_text=(
            'Appears on the homepage between the hero and the enterprise/'
            'innovation split. The body of the Vision section. Use multiple '
            'paragraphs.'
        ),
    )
    vision_heading = models.CharField(
        max_length=200,
        default='How HR operations should work',
        blank=True,
        help_text='Appears on the homepage Vision section as the H2 heading (above the Vision paragraphs).',
    )
    enterprise_column_heading = models.CharField(
        max_length=200,
        default='Running HR operations that people can depend on',
        blank=True,
        help_text='Appears on the homepage as the H2 heading of the Enterprise Leadership column.',
    )
    enterprise_section_intro = HTMLField(
        blank=True,
        help_text='Appears on the homepage Enterprise Leadership column as the intro paragraph above the three pillars.',
    )
    enterprise_section_closing = HTMLField(
        blank=True,
        help_text='Appears on the homepage Enterprise Leadership column as the closing block below the three pillars.',
    )
    innovation_column_heading = models.CharField(
        max_length=200,
        default='Designing personal AI systems',
        blank=True,
        help_text='Appears on the homepage as the H2 heading of the Innovation column.',
    )
    innovation_section_intro = HTMLField(
        blank=True,
        help_text='Appears on the homepage Innovation column as the intro paragraph above the three highlights.',
    )
    read_profile_link_label = models.CharField(
        max_length=120,
        default='Read the executive profile →',
        blank=True,
        help_text='Appears at the bottom of the homepage as the link to the Executive Profile page.',
    )
    contact_email = models.EmailField(
        blank=True,
        help_text='Appears in the footer of every page as the contact email link.',
    )
    linkedin_url = models.URLField(
        blank=True,
        help_text='Appears in the footer as the LinkedIn link (opens in new tab).',
    )

    # ----- Global site chrome (every page) -----
    brand_wordmark = models.CharField(
        max_length=120,
        default='Danny R. Jenkins',
        blank=True,
        help_text='Wordmark in the top-left of every page header. Also used as the H1 on the resume page.',
    )
    nav_menu_toggle_label = models.CharField(
        max_length=40,
        default='Menu',
        blank=True,
        help_text='Visible text on the mobile nav toggle button.',
    )
    nav_home_label = models.CharField(max_length=40, default='Home', blank=True, help_text='Top-nav label for the Home page.')
    nav_profile_label = models.CharField(max_length=40, default='Profile', blank=True, help_text='Top-nav label for the Profile page.')
    nav_enterprise_label = models.CharField(max_length=60, default='Enterprise Leadership', blank=True, help_text='Top-nav label for the Enterprise Leadership page.')
    nav_case_studies_label = models.CharField(max_length=40, default='Case Studies', blank=True, help_text='Top-nav label for the Case Studies index.')
    nav_innovation_label = models.CharField(max_length=40, default='Innovation', blank=True, help_text='Top-nav label for the Innovation page.')
    nav_perspectives_label = models.CharField(max_length=40, default='Perspectives', blank=True, help_text='Top-nav label for the Perspectives index.')
    nav_connect_label = models.CharField(max_length=40, default='Connect', blank=True, help_text='Top-nav label for the Connect page.')
    footer_owner_name = models.CharField(
        max_length=120,
        default='Danny R. Jenkins',
        blank=True,
        help_text='Name shown after the © year in the footer of every page.',
    )
    footer_linkedin_label = models.CharField(
        max_length=40,
        default='LinkedIn',
        blank=True,
        help_text='Visible text of the LinkedIn link in the footer (the URL is set above).',
    )

    # ----- Homepage section eyebrows -----
    vision_eyebrow = models.CharField(
        max_length=80,
        default='Vision',
        blank=True,
        help_text='Small uppercase label above the Vision heading on the homepage.',
    )
    enterprise_column_eyebrow = models.CharField(
        max_length=80,
        default='Enterprise Leadership',
        blank=True,
        help_text='Small uppercase label above the left-column heading on the homepage.',
    )
    innovation_column_eyebrow = models.CharField(
        max_length=80,
        default='Innovation',
        blank=True,
        help_text='Small uppercase label above the right-column heading on the homepage.',
    )

    # ----- Case Study detail labels (apply to every case-study page) -----
    case_study_back_link_label = models.CharField(max_length=80, default='← All Case Studies', blank=True, help_text='Breadcrumb at the top of every case study detail page.')
    case_study_chip_suffix = models.CharField(max_length=40, default='Case Study', blank=True, help_text='Word(s) appended after the category in the chip on a case study detail page (e.g. "Enterprise Case Study").')
    case_study_problem_eyebrow = models.CharField(max_length=80, default='Problem', blank=True, help_text='Eyebrow above the Problem block on every case study.')
    case_study_problem_heading = models.CharField(max_length=120, default='The problem', blank=True, help_text='H2 of the Problem block on every case study.')
    case_study_role_eyebrow = models.CharField(max_length=80, default='Role', blank=True, help_text='Eyebrow above the Role block on every case study.')
    case_study_role_heading = models.CharField(max_length=120, default='My role', blank=True, help_text='H2 of the Role block on every case study.')
    case_study_approach_eyebrow = models.CharField(max_length=80, default='Approach', blank=True, help_text='Eyebrow above the Approach block on every case study.')
    case_study_approach_heading = models.CharField(max_length=120, default='Approach', blank=True, help_text='H2 of the Approach block on every case study.')
    case_study_outcome_eyebrow = models.CharField(max_length=80, default='Outcome', blank=True, help_text='Eyebrow above the Outcome block on every case study.')
    case_study_outcome_heading = models.CharField(max_length=120, default='Outcome', blank=True, help_text='H2 of the Outcome block on every case study.')
    case_study_back_to_all_label = models.CharField(max_length=80, default='← Back to all case studies', blank=True, help_text='Bottom-of-page back link on every case study.')

    # ----- Perspective detail labels (apply to every perspective page) -----
    perspective_back_link_label = models.CharField(max_length=80, default='← All Perspectives', blank=True, help_text='Breadcrumb at the top of every perspective detail page.')
    perspective_closing_eyebrow = models.CharField(max_length=80, default='Closing', blank=True, help_text='Eyebrow above the closing paragraph on a perspective detail page.')
    perspective_back_to_all_label = models.CharField(max_length=80, default='← Back to all Perspectives', blank=True, help_text='Bottom-of-page back link on every perspective detail page.')

    # ----- Resume page chrome -----
    resume_eyebrow_prefix = models.CharField(max_length=40, default='Resume', blank=True, help_text='Word that prefixes the eyebrow on a resume page (renders as "Resume · <type>").')
    resume_print_button_label = models.CharField(max_length=80, default='Print / Save as PDF', blank=True, help_text='Button text on the resume page that triggers print / save-as-PDF.')

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

    class Meta:
        verbose_name = 'Profile page'
        verbose_name_plural = 'Profile pages'

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
        verbose_name = 'Case study entry'
        verbose_name_plural = 'Case Studies — Entries'

    def __str__(self):
        return self.title


class EnterpriseOverview(models.Model):
    """Singleton: top-of-page overview for /enterprise-leadership/.

    Kept minimal (scope + impact) on purpose. The deeper structure lives
    in EnterpriseFunction records below.
    """

    page_eyebrow = models.CharField(
        max_length=80,
        default='Enterprise Leadership',
        blank=True,
        help_text='Small uppercase label above the H1 at the top of the Enterprise Leadership page.',
    )
    hero_heading = models.CharField(
        max_length=200,
        default='Running HR operations at scale',
        blank=True,
        help_text='Appears on the Enterprise Leadership page hero as the H1 headline.',
    )
    hero_lead = HTMLField(
        blank=True,
        verbose_name='Hero lead paragraph',
        help_text='Appears on the Enterprise Leadership page hero, below the headline, as the supporting paragraph.',
    )
    scope_label = models.CharField(
        max_length=80,
        default='Scope',
        blank=True,
        help_text='Drives both the eyebrow and the H2 of the Scope section on the Enterprise Leadership page.',
    )
    scope = HTMLField(
        blank=True,
        help_text='Appears on the Enterprise Leadership page as the body of the Scope section.',
    )
    impact_label = models.CharField(
        max_length=80,
        default='Impact',
        blank=True,
        help_text='Drives both the eyebrow and the H2 of the Impact section on the Enterprise Leadership page.',
    )
    impact = HTMLField(
        blank=True,
        help_text='Appears on the Enterprise Leadership page as the body of the Impact section.',
    )
    function_section_eyebrow = models.CharField(
        max_length=80,
        default='The Function',
        blank=True,
        help_text='Eyebrow above the "What I lead" heading (the section that holds the three function blocks).',
    )
    function_section_heading = models.CharField(
        max_length=200,
        default='What I lead',
        blank=True,
        help_text='Appears on the Enterprise Leadership page as the H2 heading above the three function blocks (Compensation, HRIS, Payroll).',
    )
    system_integration_eyebrow = models.CharField(
        max_length=80,
        default='System Integration',
        blank=True,
        help_text='Eyebrow above the closing-section heading at the bottom of the Enterprise Leadership page.',
    )
    system_integration_heading = models.CharField(
        max_length=200,
        default='How the system works together',
        blank=True,
        help_text='Appears on the Enterprise Leadership page as the H2 heading of the closing section.',
    )
    system_integration = HTMLField(
        blank=True,
        verbose_name='Closing section body',
        help_text=(
            'Appears on the Enterprise Leadership page as the body of the closing '
            'section. Explain how Compensation, HRIS, and Payroll operate as one '
            'system — not three parallel jobs.'
        ),
    )

    class Meta:
        verbose_name = 'Enterprise Leadership'
        verbose_name_plural = 'Enterprise Leadership'

    def __str__(self):
        return 'Enterprise Leadership'

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
    responsibilities_label = models.CharField(
        max_length=80,
        default='RESPONSIBILITIES',
        blank=True,
        verbose_name='"Responsibilities" section label',
        help_text=(
            'Small uppercase label above the "Responsibilities" block on '
            'the Enterprise Leadership page. Edit per function. Leave blank '
            'to fall back to "RESPONSIBILITIES".'
        ),
    )
    responsibilities = HTMLField(help_text='What this function leads.')
    systems_led = HTMLField(help_text='Systems, tools, and programs owned.')
    platforms_and_tools_label = models.CharField(
        max_length=80,
        default='PLATFORMS AND TOOLS',
        blank=True,
        verbose_name='"Systems Led" section label',
        help_text=(
            'The small uppercase label rendered above the "Systems Led" '
            'block on the Enterprise Leadership page. Edit per function. '
            'Leave blank to fall back to "PLATFORMS AND TOOLS".'
        ),
    )
    organizational_role = HTMLField(
        help_text='How this function fits into the organization.',
    )
    role_and_accountability_label = models.CharField(
        max_length=80,
        default='ROLE AND ACCOUNTABILITY',
        blank=True,
        verbose_name='"Role in the Organization" section label',
        help_text=(
            'The small uppercase label rendered above the "Role in the '
            'Organization" block on the Enterprise Leadership page. Edit '
            'per function. Leave blank to fall back to '
            '"ROLE AND ACCOUNTABILITY".'
        ),
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Enterprise Leadership function'
        verbose_name_plural = 'Enterprise Leadership — Functions'

    def __str__(self):
        return self.title


class InnovationOverview(models.Model):
    """Singleton for /innovation/.

    Structured sections — Beacon positioning, WLJ overview, architecture
    caption, AI Chief of Staff. The Data → Signals → Decisions diagram is
    design, not content, and lives in the template as inline SVG.
    """

    page_eyebrow = models.CharField(
        max_length=80,
        default='Innovation',
        blank=True,
        help_text='Small uppercase label above the H1 at the top of the Innovation page.',
    )
    hero_heading = models.CharField(
        max_length=200,
        default='Innovation & Systems Design',
        blank=True,
        help_text='Appears on the Innovation page hero as the H1 headline.',
    )
    intro = HTMLField(
        blank=True,
        help_text='Appears on the Innovation page hero, below the headline, as the lead paragraph.',
    )
    beacon_eyebrow = models.CharField(
        max_length=80,
        default='Beacon Innovation',
        blank=True,
        help_text='Eyebrow above the Beacon Innovation block on the Innovation page.',
    )
    beacon_heading = models.CharField(
        max_length=200,
        default='Beacon Innovation, LLC',
        blank=True,
        help_text='H2 of the Beacon Innovation block on the Innovation page.',
    )
    beacon_positioning = HTMLField(
        blank=True,
        verbose_name='Beacon Innovation positioning',
        help_text='Appears on the Innovation page as the body of the Beacon Innovation, LLC section.',
    )
    wlj_case_study_link_label = models.CharField(
        max_length=200,
        default='See how this operates in practice → WLJ Case Study',
        blank=True,
        help_text='Appears at the bottom of the Innovation page as the link to the WLJ case study.',
    )
    wlj_eyebrow = models.CharField(
        max_length=80,
        default='Whole Life Journey',
        blank=True,
        help_text='Eyebrow above the Whole Life Journey block on the Innovation page.',
    )
    wlj_heading = models.CharField(
        max_length=200,
        default='Whole Life Journey',
        blank=True,
        help_text='H2 of the Whole Life Journey block on the Innovation page.',
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
    architecture_eyebrow = models.CharField(
        max_length=80,
        default='Architecture',
        blank=True,
        help_text='Eyebrow above the Data → Signals → Decisions block on the Innovation page.',
    )
    architecture_heading = models.CharField(
        max_length=200,
        default='Data → Signals → Decisions',
        blank=True,
        help_text='H2 above the Data → Signals → Decisions diagram on the Innovation page.',
    )
    diagram_box_1_label = models.CharField(max_length=40, default='Data', blank=True, help_text='Label inside the FIRST box of the architecture diagram.')
    diagram_box_2_label = models.CharField(max_length=40, default='Signals', blank=True, help_text='Label inside the SECOND box of the architecture diagram.')
    diagram_box_3_label = models.CharField(max_length=40, default='Decisions', blank=True, help_text='Label inside the THIRD box of the architecture diagram.')
    diagram_caption_1 = models.CharField(max_length=80, default='WHAT SYSTEMS EMIT', blank=True, help_text='Small uppercase caption under the FIRST diagram box.')
    diagram_caption_2 = models.CharField(max_length=80, default='PATTERNS WORTH WATCHING', blank=True, help_text='Small uppercase caption under the SECOND diagram box.')
    diagram_caption_3 = models.CharField(max_length=80, default='ACTION TO TAKE NEXT', blank=True, help_text='Small uppercase caption under the THIRD diagram box.')
    architecture_caption = HTMLField(
        blank=True,
        help_text=(
            'Paragraph accompanying the Data → Signals → Decisions diagram. '
            'Explain the three stages in plain language.'
        ),
    )
    in_practice_eyebrow = models.CharField(
        max_length=80,
        default='In Practice',
        blank=True,
        help_text='Eyebrow above the in-practice example beneath the architecture diagram.',
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
    chief_of_staff_eyebrow = models.CharField(
        max_length=80,
        default='AI Chief of Staff',
        blank=True,
        help_text='Eyebrow above the AI Chief of Staff block on the Innovation page.',
    )
    chief_of_staff_heading = models.CharField(
        max_length=200,
        default='AI Chief of Staff',
        blank=True,
        help_text='H2 of the AI Chief of Staff block on the Innovation page.',
    )
    chief_of_staff = HTMLField(
        blank=True,
        verbose_name='AI Chief of Staff concept',
        help_text='The AI layer as an executive Chief of Staff — not a chatbot metaphor.',
    )
    what_this_demonstrates_eyebrow = models.CharField(
        max_length=80,
        default='What This Demonstrates',
        blank=True,
        help_text='Eyebrow above the closing block on the Innovation page.',
    )
    what_this_demonstrates_heading = models.CharField(
        max_length=200,
        default='What this demonstrates',
        blank=True,
        help_text='H2 of the closing block on the Innovation page.',
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
        verbose_name = 'Innovation'
        verbose_name_plural = 'Innovation'

    def __str__(self):
        return 'Innovation'

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
        verbose_name = 'Perspective entry'
        verbose_name_plural = 'Perspectives — Entries'

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


class ResumeVersion(models.Model):
    """A tailored resume version (HR Ops, Total Rewards, General, etc.).

    URL: /resume/<slug>/ — only accessible if is_active=True. Not linked
    from the public nav; the URL is shared by the owner on request.
    """

    HR_OPS = 'HR_OPS'
    TOTAL_REWARDS = 'TOTAL_REWARDS'
    GENERAL = 'GENERAL'
    TYPE_CHOICES = [
        (HR_OPS, 'HR Operations'),
        (TOTAL_REWARDS, 'Total Rewards'),
        (GENERAL, 'General'),
    ]

    slug = models.SlugField(
        unique=True,
        max_length=80,
        help_text='URL identifier, e.g. "general", "hr-ops", "total-rewards".',
    )
    name = models.CharField(
        max_length=200,
        help_text='Short label shown as the deck under the name (e.g. "HR Operations").',
    )
    type = models.CharField(max_length=30, choices=TYPE_CHOICES, default=GENERAL)
    is_active = models.BooleanField(
        default=True,
        help_text='Uncheck to take the URL offline without deleting the content.',
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['type', 'name']
        verbose_name = 'Resume version'
        verbose_name_plural = 'Resume — Versions'

    def __str__(self):
        return f'{self.name} ({self.get_type_display()})'


class ResumeSection(models.Model):
    """Ordered section within a ResumeVersion.

    content is TinyMCE-restricted HTML. The editor is responsible for
    laying out the section body (titles, orgs, dates, bullets) — the
    template renders {{ content|safe }} inside the section heading.
    """

    SUMMARY = 'SUMMARY'
    CURRENT_ROLE = 'CURRENT_ROLE'
    PRIOR_ROLES = 'PRIOR_ROLES'
    EDUCATION = 'EDUCATION'
    HIGHLIGHTS = 'HIGHLIGHTS'
    CUSTOM = 'CUSTOM'
    SECTION_CHOICES = [
        (SUMMARY, 'Executive Summary'),
        (CURRENT_ROLE, 'Current Role'),
        (PRIOR_ROLES, 'Prior Roles'),
        (EDUCATION, 'Education & Certifications'),
        (HIGHLIGHTS, 'Key Impact Highlights'),
        (CUSTOM, 'Custom Section'),
    ]

    version = models.ForeignKey(
        ResumeVersion,
        related_name='sections',
        on_delete=models.CASCADE,
    )
    section_type = models.CharField(max_length=30, choices=SECTION_CHOICES)
    heading = models.CharField(
        max_length=200,
        blank=True,
        help_text='Override the default heading for this section type. Required if type=CUSTOM.',
    )
    content = HTMLField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.version.slug} · {self.get_section_type_display()}'

    def get_display_heading(self):
        if self.heading:
            return self.heading
        return dict(self.SECTION_CHOICES).get(self.section_type, self.section_type)


class ConnectPage(models.Model):
    """Singleton for /connect/ — two CTAs (conversation + resume request)."""

    page_eyebrow = models.CharField(
        max_length=80,
        default='Connect',
        blank=True,
        help_text='Small uppercase label above the H1 at the top of the Connect page.',
    )
    page_title = models.CharField(
        max_length=120,
        default='Connect',
        blank=True,
        help_text='H1 (page title) at the top of the Connect page.',
    )
    intro = HTMLField(
        blank=True,
        help_text='Appears on the Connect page hero, below the headline, as the lead paragraph.',
    )
    form_prelude = models.CharField(
        max_length=300,
        default='If you’d like to connect, share a few details below.',
        blank=True,
        help_text='Appears on the Connect page as the bridge sentence above the contact form.',
    )
    name_label = models.CharField(max_length=40, default='Name', blank=True, help_text='Label above the Name input on the contact form.')
    email_label = models.CharField(max_length=40, default='Email', blank=True, help_text='Label above the Email input on the contact form.')
    inquiry_label = models.CharField(max_length=80, default='Reason for reaching out', blank=True, help_text='Label above the inquiry-type dropdown on the contact form.')
    message_label = models.CharField(max_length=40, default='Message', blank=True, help_text='Label above the Message textarea on the contact form.')
    message_optional_label = models.CharField(max_length=20, default='(optional)', blank=True, help_text='Small parenthetical note next to the Message label.')
    submit_button_label = models.CharField(max_length=80, default='Submit', blank=True, help_text='Visible text on the contact-form submit button. The form covers multiple inquiry types (resume request, conversation, etc.), so a neutral verb like "Submit" is the safe default.')
    success_heading = models.CharField(
        max_length=200,
        default='Thank you — I’ve received your message.',
        blank=True,
        help_text='Appears on the Connect page after a successful form submission, as the H2 of the confirmation block.',
    )
    success_body = HTMLField(
        blank=True,
        help_text='Appears on the Connect page after a successful form submission, as the paragraph below the confirmation heading.',
    )
    # Legacy mailto-CTA fields — retained for schema compatibility but no longer
    # rendered on the Connect page (the contact form replaced them). Will be
    # removed in a follow-up cleanup migration.
    conversation_label = models.CharField(max_length=100, default='Request a conversation', blank=True)
    conversation_blurb = models.CharField(max_length=300, blank=True)
    conversation_href = models.CharField(max_length=500, default='mailto:', blank=True)
    resume_label = models.CharField(max_length=100, default='Request a resume', blank=True)
    resume_blurb = models.CharField(max_length=300, blank=True)
    resume_href = models.CharField(max_length=500, default='mailto:', blank=True)

    class Meta:
        verbose_name = 'Connect'
        verbose_name_plural = 'Connect'

    def __str__(self):
        return 'Connect'

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
        verbose_name = 'Homepage pillar'
        verbose_name_plural = 'Home — Pillars'

    def __str__(self):
        return f'[{self.get_category_display()}] {self.title}'


class CaseStudiesIndexPage(models.Model):
    """Singleton: copy for the /case-studies/ index page (the list page)."""

    page_eyebrow = models.CharField(
        max_length=80,
        default='Case Studies',
        blank=True,
        help_text='Small uppercase label above the H1 on the Case Studies index.',
    )
    page_title = models.CharField(
        max_length=200,
        default='Selected work',
        blank=True,
        help_text='H1 at the top of the Case Studies index.',
    )
    page_lead = HTMLField(
        blank=True,
        help_text=(
            'Lead paragraph below the H1 on the Case Studies index. '
            'Leave blank to fall back to the design-time default.'
        ),
    )
    read_more_label = models.CharField(
        max_length=60,
        default='Read case study →',
        blank=True,
        help_text='Per-card link text on the Case Studies index ("Read case study →").',
    )
    empty_state_label = models.CharField(
        max_length=120,
        default='No published case studies yet.',
        blank=True,
        help_text='Message shown when there are zero published case studies.',
    )

    class Meta:
        verbose_name = 'Case Studies'
        verbose_name_plural = 'Case Studies'

    def __str__(self):
        return 'Case Studies'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class PerspectivesIndexPage(models.Model):
    """Singleton: copy for the /perspectives/ index page (the list page)."""

    page_eyebrow = models.CharField(
        max_length=80,
        default='Perspectives',
        blank=True,
        help_text='Small uppercase label above the H1 on the Perspectives index.',
    )
    page_title = models.CharField(
        max_length=200,
        default='Perspectives',
        blank=True,
        help_text='H1 at the top of the Perspectives index.',
    )
    page_lead = HTMLField(
        blank=True,
        help_text=(
            'Lead paragraph below the H1 on the Perspectives index. '
            'Leave blank to fall back to the design-time default.'
        ),
    )
    read_more_label = models.CharField(
        max_length=60,
        default='Read →',
        blank=True,
        help_text='Per-card link text on the Perspectives index.',
    )
    empty_state_label = models.CharField(
        max_length=120,
        default='No perspectives published yet.',
        blank=True,
        help_text='Message shown when there are zero published perspectives.',
    )

    class Meta:
        verbose_name = 'Perspectives'
        verbose_name_plural = 'Perspectives'

    def __str__(self):
        return 'Perspectives'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
