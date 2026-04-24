from django.http import Http404
from django.shortcuts import get_object_or_404, render

from .models import CaseStudy, HomepagePillar, Page


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


def case_study_index(request):
    studies = CaseStudy.objects.filter(published=True)
    return render(request, 'case_studies/index.html', {'studies': studies})


def case_study_detail(request, slug):
    study = get_object_or_404(CaseStudy, slug=slug, published=True)
    return render(request, 'case_studies/detail.html', {'study': study})


def placeholder(request, title):
    """Phase 1 placeholder for sections built in later phases."""
    return render(request, 'placeholder.html', {'section_title': title})
