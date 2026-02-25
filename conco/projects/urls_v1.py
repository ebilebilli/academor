from django.urls import path

from projects.views.views_v1 import (
    HomePageView,
    ProjectPageView,
    ProjectDetailPageView,
    AboutPageView,
    ServicesPageView,
    ContactPageView,
    VacancyPageView,
    VacancyDetailPageView,
)


app_name = 'projects'

urlpatterns = [
    path(
        '', 
        HomePageView.as_view(),
        name='home-page'
    ),
    path(
        'projects/', 
        ProjectPageView.as_view(), 
        name='project-page'
    ),
    path(
        'projects/<slug:slug>/', 
        ProjectDetailPageView.as_view(), 
        name='project-detail'
    ),
    path(
        'about/', 
        AboutPageView.as_view(), 
        name='about-page'
    ),
    path(
        'services/', 
        ServicesPageView.as_view(), 
        name='services-page'
    ),
    path(
        'contact/', 
        ContactPageView.as_view(), 
        name='contact-page'
    ),
    path(
        'vacancies/', 
        VacancyPageView.as_view(), 
        name='vacancy-page'
    ),
    path(
        'vacancies/<slug:slug>/', 
        VacancyDetailPageView.as_view(), 
        name='vacancy-detail'
    )
]   
