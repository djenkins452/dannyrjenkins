from django.http import Http404
from django.shortcuts import get_object_or_404, render

from .models import (
    CaseStudy,
    EnterpriseFunction,
    EnterpriseOverview,
    HomepagePillar,
    InnovationOverview,
    Page,
    Perspective,
    ResumePage,
)


def home(request):
    context = {
        'enterprise_pillars': HomepagePillar.objects.filter(
            category=HomepagePillar.ENTERPRISE,
        ),
        'innovation_pillars': HomepagePillar.objects.filter(
            category=HomepagePillar.INNOVATION,
        ),
    }
    return render(request, 'home.html', context)


def profile(request):
    try:
        page = Page.objects.prefetch_related('blocks').get(slug='profile')
    except Page.DoesNotExist:
        raise Http404('Profile page has not been created yet.')
    return render(request, 'profile.html', {'page': page})


def enterprise_leadership(request):
    context = {
        'overview': EnterpriseOverview.load(),
        'functions': EnterpriseFunction.objects.all(),
    }
    return render(request, 'enterprise_leadership.html', context)


def innovation(request):
    return render(request, 'innovation.html', {'overview': InnovationOverview.load()})


def resume(request):
    return render(request, 'resume.html', {'page': ResumePage.load()})


def case_study_index(request):
    studies = CaseStudy.objects.filter(published=True)
    return render(request, 'case_studies/index.html', {'studies': studies})


def case_study_detail(request, slug):
    study = get_object_or_404(CaseStudy, slug=slug, published=True)
    return render(request, 'case_studies/detail.html', {'study': study})


def perspective_index(request):
    perspectives = Perspective.objects.filter(published=True)
    return render(request, 'perspectives/index.html', {'perspectives': perspectives})


def perspective_detail(request, slug):
    perspective = get_object_or_404(
        Perspective.objects.prefetch_related('sections'),
        slug=slug,
        published=True,
    )
    return render(request, 'perspectives/detail.html', {'perspective': perspective})


def placeholder(request, title):
    """Phase 1 placeholder for sections built in later phases."""
    return render(request, 'placeholder.html', {'section_title': title})
