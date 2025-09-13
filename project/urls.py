"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.decorators import login_required
from django.conf.urls.static import static
from django.conf import settings

# Import views from the new organized structure
from app.views import (
    # Base views
    index, profile,
    # Election views
    ElectionListView, ElectionDetailView, ElectionCreateView, ElectionUpdateView,
    # Candidate views
    CandidateCreateView, CandidateUpdateView, CandidateDeleteView,
    # Vote views
    VoteView, CloseElectionView, VerifyResultsView
)

admin.site.site_header = 'Election Management System'
admin.site.site_title = 'Intikhab'

urlpatterns = [
    # Base views
    path('', index, name='index'),
    path('profile', profile, name='profile'),
    
    # Election management
    path('elections', login_required(ElectionListView.as_view()), name='election_list'),
    path('elections/create', ElectionCreateView.as_view(), name='create_election'),
    path('elections/<int:pk>', login_required(ElectionDetailView.as_view()), name='election_detail'),
    path('elections/<int:pk>/edit', ElectionUpdateView.as_view(), name='edit_election'),
    path('elections/<int:pk>/close', CloseElectionView.as_view(), name='close_election'),
    
    # Candidate management
    path('elections/<int:election_pk>/candidates/add', CandidateCreateView.as_view(), name='add_candidate'),
    path('candidates/<int:pk>/edit', CandidateUpdateView.as_view(), name='edit_candidate'),
    path('candidates/<int:pk>/delete', CandidateDeleteView.as_view(), name='delete_candidate'),
    
    # Voting and results
    path('elections/<int:election_id>/vote/<int:candidate_id>', VoteView.as_view(), name='vote'),
    path('elections/<int:election_id>/verify-results', login_required(VerifyResultsView.as_view()), name='verify_results'),
    
    # Authentication
    path("accounts/", include("django.contrib.auth.urls")),
    path('accounts/', include('allauth.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
