from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import (
    CaseStudy,
    EnterpriseFunction,
    EnterpriseOverview,
    HomepagePillar,
    InnovationOverview,
    NarrativeBlock,
    Page,
    Perspective,
    PerspectiveSection,
    ResumePage,
    SiteConfig,
)


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
        (None, {'fields': ('title', 'slug', 'eyebrow', 'intro')}),
        ('SEO', {
            'classes': ('collapse',),
            'fields': ('seo_title', 'seo_description'),
        }),
    )
    inlines = [NarrativeBlockInline]


@admin.register(CaseStudy)
class CaseStudyAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'order', 'published', 'published_at')
    list_filter = ('category', 'published')
    list_editable = ('order', 'published')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'category', 'summary'),
        }),
        ('Case study body', {
            'fields': ('problem', 'role', 'approach', 'outcome'),
            'description': (
                'Structure is fixed: every case study renders Problem, Role, '
                'Approach, Outcome in order. Write each as 1–3 paragraphs.'
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


@admin.register(HomepagePillar)
class HomepagePillarAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'order')
    list_filter = ('category',)
    list_editable = ('order',)
    ordering = ('category', 'order')


@admin.register(EnterpriseOverview)
class EnterpriseOverviewAdmin(admin.ModelAdmin):
    """Singleton: redirect changelist to the sole instance."""

    fields = ('scope', 'impact', 'system_integration')

    def has_add_permission(self, request):
        return not EnterpriseOverview.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = EnterpriseOverview.load()
        return HttpResponseRedirect(
            reverse('admin:website_enterpriseoverview_change', args=[obj.pk])
        )


@admin.register(InnovationOverview)
class InnovationOverviewAdmin(admin.ModelAdmin):
    """Singleton: redirect changelist to the sole instance."""

    fieldsets = (
        (None, {'fields': ('intro',)}),
        ('Beacon Innovation', {'fields': ('beacon_positioning',)}),
        ('Whole Life Journey', {'fields': ('wlj_positioning', 'wlj_overview')}),
        ('Architecture', {'fields': ('architecture_caption', 'practical_example')}),
        ('AI Chief of Staff', {'fields': ('chief_of_staff',)}),
        ('What This Demonstrates', {'fields': ('what_this_demonstrates',)}),
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
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'eyebrow', 'deck')}),
        ('Body', {
            'fields': ('lead', 'closing'),
            'description': (
                'Lead is the opening paragraph (the argument in one paragraph). '
                'Closing is the final paragraph. Use the Sections inline below '
                'for the middle sections.'
            ),
        }),
        ('Publication', {'fields': ('published', 'published_at', 'order')}),
        ('SEO', {
            'classes': ('collapse',),
            'fields': ('seo_title', 'seo_description'),
        }),
    )
    inlines = [PerspectiveSectionInline]


@admin.register(EnterpriseFunction)
class EnterpriseFunctionAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'order')
    list_editable = ('order',)
    prepopulated_fields = {'slug': ('title',)}
    fields = (
        'title',
        'slug',
        'summary',
        'responsibilities',
        'systems_led',
        'organizational_role',
        'order',
    )


@admin.register(ResumePage)
class ResumePageAdmin(admin.ModelAdmin):
    """Singleton: redirect changelist to the sole instance."""

    fieldsets = (
        ('Header', {'fields': ('positioning_line',)}),
        ('Executive Summary', {'fields': ('executive_summary',)}),
        ('Current Role', {
            'fields': (
                'current_role_title',
                'current_role_org',
                'current_role_dates',
                'current_role_bullets',
            ),
        }),
        ('Prior Roles', {'fields': ('prior_roles',)}),
        ('Education & Certifications', {'fields': ('education',)}),
        ('Key Impact Highlights', {'fields': ('key_impact',)}),
    )

    def has_add_permission(self, request):
        return not ResumePage.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = ResumePage.load()
        return HttpResponseRedirect(
            reverse('admin:website_resumepage_change', args=[obj.pk])
        )


@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    """Singleton: redirect changelist to the sole instance's edit view."""

    fieldsets = (
        ('Homepage', {
            'fields': (
                'homepage_headline',
                'homepage_subheadline',
                'enterprise_section_intro',
                'innovation_section_intro',
            ),
        }),
        ('Contact', {'fields': ('contact_email', 'linkedin_url')}),
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
