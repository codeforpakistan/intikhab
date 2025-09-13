# Import all views to make them available at package level
from .election import ElectionListView, ElectionDetailView, ElectionCreateView, ElectionUpdateView
from .candidate import CandidateCreateView, CandidateUpdateView, CandidateDeleteView, CandidateDetailView
from .vote import VoteView, VerifyResultsView, CloseElectionView
from .base import index, profile, terms, privacy, accessibility, contact, faq

# For backwards compatibility, make views available at the package level
__all__ = [
    # Election views
    'ElectionListView', 'ElectionDetailView', 'ElectionCreateView', 'ElectionUpdateView',
    # Candidate views  
    'CandidateCreateView', 'CandidateUpdateView', 'CandidateDeleteView', 'CandidateDetailView',
    # Vote views
    'VoteView', 'VerifyResultsView', 'CloseElectionView',
    # Base views
    'index', 'profile',
    # Legal views
    'terms', 'privacy', 'accessibility', 'contact', 'faq'
]