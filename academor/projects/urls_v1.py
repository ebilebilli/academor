from django.urls import path

from projects.views.views_v1 import (
    HomePageView,
    CoursesPageView,
    CourseDetailPageView,
    AboutPageView,
    ServicesPageView,
    AbroadPageView,
    AbroadDetailPageView,
    ContactPageView,
    TeamPageView,
    TeamDetailPageView,
    ReviewsPageView,
)
from projects.views.test_views import TestListPageView, TestTakePageView
from projects.views.conversation_topics_views import (
    EnglishConversationTopicsListView,
    EnglishConversationTopicDetailView,
    LegacyTopicTwoRedirectView,
)


app_name = 'projects'

urlpatterns = [
    path(
        '', 
        HomePageView.as_view(),
        name='home-page'
    ),
    path(
        'courses/',
        CoursesPageView.as_view(),
        name='courses-page'
    ),
    path(
        'courses/<slug:slug>/',
        CourseDetailPageView.as_view(),
        name='course-detail'
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
        'abroad/',
        AbroadPageView.as_view(),
        name='abroad-page'
    ),
    path(
        'abroad/<int:pk>/',
        AbroadDetailPageView.as_view(),
        name='abroad-detail'
    ),
    path(
        'contact/', 
        ContactPageView.as_view(), 
        name='contact-page'
    ),
    path(
        'team/',
        TeamPageView.as_view(),
        name='team-page',
    ),
    path(
        'team/<int:pk>/',
        TeamDetailPageView.as_view(),
        name='team-detail',
    ),
    path(
        'reviews/',
        ReviewsPageView.as_view(),
        name='reviews-page',
    ),
    path(
        'tests/',
        TestListPageView.as_view(),
        name='tests-page',
    ),
    path(
        'tests/<int:test_id>/',
        TestTakePageView.as_view(),
        name='test-take',
    ),
    path(
        'learn/english-conversation-topics/',
        EnglishConversationTopicsListView.as_view(),
        name='english-conversation-topics',
    ),
    path(
        'learn/english-conversation-topics/two/',
        LegacyTopicTwoRedirectView.as_view(),
        name='english-conversation-topic-two-legacy',
    ),
    path(
        'learn/english-conversation-topics/<slug:slug>/',
        EnglishConversationTopicDetailView.as_view(),
        name='english-conversation-topic-detail',
    ),
]   
