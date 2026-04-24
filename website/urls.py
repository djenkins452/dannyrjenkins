from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path(
        'enterprise-leadership/',
        views.enterprise_leadership,
        name='enterprise',
    ),
    path('case-studies/', views.case_study_index, name='case_studies'),
    path(
        'case-studies/<slug:slug>/',
        views.case_study_detail,
        name='case_study_detail',
    ),
    path('innovation/', views.innovation, name='innovation'),
    path('perspectives/', views.perspective_index, name='perspectives'),
    path(
        'perspectives/<slug:slug>/',
        views.perspective_detail,
        name='perspective_detail',
    ),
    path('resume/', views.resume, name='resume'),
]
