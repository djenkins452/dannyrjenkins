"""Admin registration for the website app.

The admin is structured so a non-developer site owner can find every
public-facing piece of content. Each fieldset name mirrors the
language used on the site; every field has help_text saying where it
appears. Use the in-page help panel on the public site (the "?" icon
visible to staff users) for a quick map.
"""

from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import (
    CaseStudy,
    ConnectPage,
    EnterpriseFunction,
    EnterpriseOverview,
    HomepagePillar,
    InnovationOverview,
    NarrativeBlock,
    Page,
    Perspective,
    PerspectiveSection,
    ResumeSection,
    ResumeVersion,
    SiteConfig,
)


# ---------------------------------------------------------------------------
# Profile page (uses Page + NarrativeBlock)
# ---------------------------------------------------------------------------

class NarrativeBlockInline(admin.StackedInline):
    model = NarrativeBlock
    extra = 1
    fields = ('order', 'eyebrow', 'heading', 'body')
    ordering = ('order',)


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'updated_at')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        ('Page header', {
            'fields': ('title', 'slug', 'eyebrow', 'intro'),
            'description': (
                'These render as the page hero. The Profile page uses this '
                'model — slug must remain "profile" for the URL to resolve.'
            ),
        }),
        ('SEO', {
            'classes': ('collapse',),
            'fields': ('seo_title', 'seo_description'),
        }),
    )
    inlines = [NarrativeBlockInline]


# ---------------------------------------------------------------------------
# Case studies (4-field structured)
# ---------------------------------------------------------------------------

@admin.register(CaseStudy)
class CaseStudyAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'order', 'published', 'published_at')
    list_filter = ('category', 'published')
    list_editable = ('order', 'published')
    search_fields = ('title', 'summary')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        ('Case study identity', {
            'fields': ('title', 'slug', 'category', 'summary'),
            'description': (
                'Title appears as the H1 on the case study page and as the '
                'card title on /case-studies/. Summary appears under the '
                'card title and as the lead paragraph on the detail page.'
            ),
        }),
        ('Case study body — fixed structure', {
            'fields': ('problem', 'role', 'approach', 'outcome'),
            'description': (
                'Every case study renders Problem → Role → Approach → Outcome '
                'in that fixed order. Write each section as 1–3 paragraphs. '
                'The section headings ("The problem," "My role," etc.) are '
                'rendered by the template and don\'t need to be set here.'
            ),
        }),
        ('Publication', {
            'fields': ('published', 'published_at', 'order'),
            'description': (
                'Order controls position on the /case-studies/ index. '
                'Uncheck Published to take a study offline without deleting.'
            ),
        }),
        ('SEO', {
            'classes': ('collapse',),
            'fields': ('seo_title', 'seo_description'),
        }),
    )


# ---------------------------------------------------------------------------
# Homepage pillars
# ---------------------------------------------------------------------------

@admin.register(HomepagePillar)
class HomepagePillarAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'order')
    list_filter = ('category',)
    list_editable = ('order',)
    ordering = ('category', 'order')

    fieldsets = (
        (None, {
            'fields': ('category', 'title', 'body', 'order'),
            'description': (
                'Pillars appear on the homepage in two columns. ENTERPRISE '
                'pillars render in the Enterprise Leadership column; '
                'INNOVATION pillars render in the Innovation column. Order '
                'controls position within the column.'
            ),
        }),
    )


# ---------------------------------------------------------------------------
# Enterprise Leadership page
# ---------------------------------------------------------------------------

@admin.register(EnterpriseOverview)
class EnterpriseOverviewAdmin(admin.ModelAdmin):
    """Singleton: redirect changelist to the sole instance."""

    fieldsets = (
        ('Page hero', {
            'fields': ('hero_heading', 'hero_lead'),
        }),
        ('Scope section', {
            'fields': ('scope',),
        }),
        ('Impact section', {
            'fields': ('impact',),
        }),
        ('Function section heading', {
            'fields': ('function_section_heading',),
            'description': 'The H2 above the three function blocks (Compensation, HRIS, Payroll).',
        }),
        ('Closing section', {
            'fields': ('system_integration_heading', 'system_integration'),
            'description': 'The "How the system works together" closing.',
        }),
    )

    def has_add_permission(self, request):
        return not EnterpriseOverview.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = EnterpriseOverview.load()
        return HttpResponseRedirect(
            reverse('admin:website_enterpriseoverview_change', args=[obj.pk])
        )


@admin.register(EnterpriseFunction)
class EnterpriseFunctionAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'order')
    list_editable = ('order',)
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        ('Function identity', {
            'fields': ('title', 'slug', 'summary', 'order'),
        }),
        ('Function body — fixed structure', {
            'fields': ('responsibilities', 'systems_led', 'organizational_role'),
            'description': (
                'Every function renders Responsibilities → Systems Led → '
                'Role in the Organization in that fixed order on the '
                'Enterprise Leadership page.'
            ),
        }),
    )


# ---------------------------------------------------------------------------
# Innovation page
# ---------------------------------------------------------------------------

@admin.register(InnovationOverview)
class InnovationOverviewAdmin(admin.ModelAdmin):
    """Singleton: redirect changelist to the sole instance."""

    fieldsets = (
        ('Page hero', {
            'fields': ('hero_heading', 'intro'),
        }),
        ('Beacon Innovation section', {
            'fields': ('beacon_positioning',),
        }),
        ('Whole Life Journey section', {
            'fields': ('wlj_positioning', 'wlj_overview'),
        }),
        ('Architecture section', {
            'fields': ('architecture_caption', 'practical_example'),
        }),
        ('AI Chief of Staff section', {
            'fields': ('chief_of_staff',),
        }),
        ('What This Demonstrates section', {
            'fields': ('what_this_demonstrates',),
        }),
        ('Footer link', {
            'fields': ('wlj_case_study_link_label',),
        }),
    )

    def has_add_permission(self, request):
        return not InnovationOverview.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = InnovationOverview.load()
        return HttpResponseRedirect(
            reverse('admin:website_innovationoverview_change', args=[obj.pk])
        )


# ---------------------------------------------------------------------------
# Perspectives
# ---------------------------------------------------------------------------

class PerspectiveSectionInline(admin.StackedInline):
    model = PerspectiveSection
    extra = 1
    fields = ('order', 'heading', 'body')
    ordering = ('order',)


@admin.register(Perspective)
class PerspectiveAdmin(admin.ModelAdmin):
    list_display = ('title', 'eyebrow', 'order', 'published', 'published_at')
    list_filter = ('published',)
    list_editable = ('order', 'published')
    search_fields = ('title', 'deck')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        ('Perspective identity', {
            'fields': ('title', 'slug', 'eyebrow', 'deck'),
            'description': (
                'Title is the H1. Eyebrow is the small uppercase category '
                'label above the title. Deck is the subtitle below the title.'
            ),
        }),
        ('Body', {
            'fields': ('lead', 'closing'),
            'description': (
                'Lead is the opening paragraph (the argument in one paragraph). '
                'Closing is the final paragraph. Use the Sections inline below '
                'for the middle sections.'
            ),
        }),
        ('Publication', {
            'fields': ('published', 'published_at', 'order'),
        }),
        ('SEO', {
            'classes': ('collapse',),
            'fields': ('seo_title', 'seo_description'),
        }),
    )
    inlines = [PerspectiveSectionInline]


# ---------------------------------------------------------------------------
# Resume versions
# ---------------------------------------------------------------------------

class ResumeSectionInline(admin.StackedInline):
    model = ResumeSection
    extra = 1
    fields = ('order', 'section_type', 'heading', 'content')
    ordering = ('order',)


@admin.register(ResumeVersion)
class ResumeVersionAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'type', 'is_active', 'updated_at')
    list_filter = ('type', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ('Resume version', {
            'fields': ('name', 'slug', 'type', 'is_active'),
            'description': (
                'Each resume version is reachable at /resume/&lt;slug&gt;/ when '
                'is_active is checked. The URL is not linked from the public '
                'nav; share it directly with recipients.'
            ),
        }),
    )


# ---------------------------------------------------------------------------
# Connect page
# ---------------------------------------------------------------------------

@admin.register(ConnectPage)
class ConnectPageAdmin(admin.ModelAdmin):
    """Singleton: redirect changelist to the sole instance."""

    fieldsets = (
        ('Hero & form', {
            'fields': ('intro', 'form_prelude'),
        }),
        ('Confirmation message (after form submit)', {
            'fields': ('success_heading', 'success_body'),
        }),
        ('Legacy CTA fields (no longer rendered)', {
            'classes': ('collapse',),
            'fields': (
                'conversation_label', 'conversation_blurb', 'conversation_href',
                'resume_label', 'resume_blurb', 'resume_href',
            ),
            'description': (
                'These fields backed the old mailto CTAs that the contact '
                'form replaced. They are not rendered anywhere on the public '
                'site. Safe to ignore.'
            ),
        }),
    )

    def has_add_permission(self, request):
        return not ConnectPage.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = ConnectPage.load()
        return HttpResponseRedirect(
            reverse('admin:website_connectpage_change', args=[obj.pk])
        )


# ---------------------------------------------------------------------------
# Site Configuration (homepage hero, homepage sections, footer)
# ---------------------------------------------------------------------------

@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    """Singleton: redirect changelist to the sole instance's edit view.

    The fieldset names and field-level help_text mirror the language used
    in the public-site help panel exactly, so an editor reading the
    panel and then opening the admin sees the same words for the same
    things. Help_text is overridden at the form level (see get_form)
    rather than on the model, to keep this an admin-only change with
    no migrations.
    """

    # Plain-language help text for the three Homepage hero fields.
    # Matches the public-site help panel exactly. Overridden at form
    # level in get_form() so we don't generate an AlterField migration.
    HERO_FIELD_HELP = {
        'homepage_headline': (
            'The large serif text at the top of the homepage, beside '
            'your photo. The first thing a visitor reads.'
        ),
        'homepage_positioning_line': (
            'Appears directly below the headline as a single sentence, '
            'slightly smaller than the headline. Plain text, no formatting.'
        ),
        'homepage_subheadline': (
            'Appears below the positioning line as the supporting '
            'paragraph. Two to three sentences that introduce who you '
            'are and what you do.'
        ),
    }

    fieldsets = (
        ('Homepage hero', {
            'fields': (
                'homepage_headline',
                'homepage_positioning_line',
                'homepage_subheadline',
            ),
            'description': (
                'The first thing visitors see — the navy band at the top '
                'of the homepage with your headshot, name, and positioning '
                'copy. The three fields below render in this exact order: '
                'Headline → Positioning line → Supporting paragraph.'
            ),
        }),
        ('Homepage Vision section', {
            'fields': ('vision_heading', 'homepage_vision'),
            'description': (
                'A separate dark band that appears below the hero. Holds '
                'the leadership-philosophy copy. Clear the body to hide '
                'this section entirely.'
            ),
        }),
        ('Homepage Enterprise Leadership column', {
            'fields': (
                'enterprise_column_heading',
                'enterprise_section_intro',
                'enterprise_section_closing',
            ),
            'description': (
                'Left column of the homepage domain split. Pillars (Compensation, '
                'HRIS, Payroll) are managed under "Homepage Pillars" — filter by '
                'Enterprise category.'
            ),
        }),
        ('Homepage Innovation column', {
            'fields': (
                'innovation_column_heading',
                'innovation_section_intro',
            ),
            'description': (
                'Right column of the homepage domain split. Pillars (Beacon '
                'Innovation, Whole Life Journey, AI Chief of Staff) are managed '
                'under "Homepage Pillars" — filter by Innovation category.'
            ),
        }),
        ('Homepage closing link', {
            'fields': ('read_profile_link_label',),
            'description': 'The "Read the executive profile →" link below the domain split.',
        }),
        ('Footer & contact', {
            'fields': ('contact_email', 'linkedin_url'),
            'description': 'Rendered in the footer of every page.',
        }),
    )

    def has_add_permission(self, request):
        return not SiteConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = SiteConfig.load()
        return HttpResponseRedirect(
            reverse('admin:website_siteconfig_change', args=[obj.pk])
        )

    def get_form(self, request, obj=None, **kwargs):
        """Apply plain-language help_text to the Homepage hero fields.

        Overridden at the form level rather than on the model so this
        change does not require a migration. Each hero field's help_text
        matches its description in the public-site help panel.
        """
        form = super().get_form(request, obj, **kwargs)
        for name, text in self.HERO_FIELD_HELP.items():
            if name in form.base_fields:
                form.base_fields[name].help_text = text
        return form


# ---------------------------------------------------------------------------
# Admin site headers
# ---------------------------------------------------------------------------
admin.site.site_header = 'Danny R. Jenkins — Site Admin'
admin.site.site_title = 'Site Admin'
admin.site.index_title = 'Site Content'
