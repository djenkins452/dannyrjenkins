from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import CaseStudy, HomepagePillar, NarrativeBlock, Page, SiteConfig


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
