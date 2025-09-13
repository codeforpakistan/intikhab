# Import all views to make them available at package level
from .election import ElectionListView, ElectionDetailView, ElectionCreateView, ElectionUpdateView
from .candidate import CandidateCreateView, CandidateUpdateView, CandidateDeleteView
from .vote import VoteView, VerifyResultsView, CloseElectionView
from .base import index, profile

# For backwards compatibility, make views available at the package level
__all__ = [
    # Election views
    'ElectionListView', 'ElectionDetailView', 'ElectionCreateView', 'ElectionUpdateView',
    # Candidate views  
    'CandidateCreateView', 'CandidateUpdateView', 'CandidateDeleteView',
    # Vote views
    'VoteView', 'VerifyResultsView', 'CloseElectionView',
    # Base views
    'index', 'profile'
]