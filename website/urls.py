from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path(
        'enterprise-leadership/',
        views.placeholder,
        {'title': 'Enterprise Leadership'},
        name='enterprise',
    ),
    path('case-studies/', views.case_study_index, name='case_studies'),
    path(
        'case-studies/<slug:slug>/',
        views.case_study_detail,
        name='case_study_detail',
    ),
    path(
        'innovation/',
        views.placeholder,
        {'title': 'Innovation'},
        name='innovation',
    ),
    path(
        'perspectives/',
        views.placeholder,
        {'title': 'Perspectives'},
        name='perspectives',
    ),
    path(
        'resume/',
        views.placeholder,
        {'title': 'Resume'},
        name='resume',
    ),
]
