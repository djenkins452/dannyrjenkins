import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.http import Http404
from django.shortcuts import get_object_or_404, render

from .forms import ContactForm

logger = logging.getLogger(__name__)

from .models import (
    CaseStudiesIndexPage,
    CaseStudy,
    ConnectPage,
    EnterpriseFunction,
    EnterpriseOverview,
    HomepagePillar,
    InnovationOverview,
    Page,
    Perspective,
    PerspectivesIndexPage,
    ResumeVersion,
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


def resume_version(request, slug):
    version = get_object_or_404(
        ResumeVersion.objects.prefetch_related('sections'),
        slug=slug,
        is_active=True,
    )
    return render(request, 'resume.html', {'version': version})


def connect(request):
    page = ConnectPage.load()
    success = False

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            inquiry_display = form.inquiry_display()
            message_text = form.cleaned_data.get('message', '') or '(no message)'

            body = (
                f'Name: {name}\n'
                f'Email: {email}\n'
                f'Inquiry type: {inquiry_display}\n'
                f'\n'
                f'Message:\n{message_text}\n'
            )

            mail = EmailMessage(
                subject=f'New {inquiry_display} request from {name}',
                body=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.EMAIL_HOST_USER] if settings.EMAIL_HOST_USER else [],
                reply_to=[email],
            )

            try:
                mail.send(fail_silently=False)
            except Exception:
                logger.exception('Contact form email send failed for %s', email)
                form.add_error(
                    None,
                    'Could not send your message right now. Please try again in a few minutes.',
                )
            else:
                logger.info(
                    'Contact form sent: inquiry=%s from=%s', inquiry_display, email,
                )
                success = True
                form = ContactForm()  # fresh form for the (hidden) state
    else:
        form = ContactForm()

    return render(request, 'connect.html', {
        'page': page,
        'form': form,
        'success': success,
    })


def case_study_index(request):
    studies = CaseStudy.objects.filter(published=True)
    return render(request, 'case_studies/index.html', {
        'studies': studies,
        'page': CaseStudiesIndexPage.load(),
    })


def case_study_detail(request, slug):
    study = get_object_or_404(CaseStudy, slug=slug, published=True)
    return render(request, 'case_studies/detail.html', {'study': study})


def perspective_index(request):
    perspectives = Perspective.objects.filter(published=True)
    return render(request, 'perspectives/index.html', {
        'perspectives': perspectives,
        'page': PerspectivesIndexPage.load(),
    })


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
