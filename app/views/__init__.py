# Import all views to make them available at package level
from .election import ElectionListView, ElectionDetailView, ElectionCreateView, ElectionUpdateView
from .candidate import CandidateCreateView, CandidateUpdateView, CandidateDeleteView, CandidateDetailView
from .vote import VoteView, VerifyResultsView, CloseElectionView
from .invitation import (
    send_invitations, manage_invitations, invitation_accept, 
    resend_invitation, cancel_invitation, process_pending_invitation
)
from .base import index, profile, terms, privacy, accessibility, contact, faq
from .auth import CustomLoginView

# For backwards compatibility, make views available at the package level
__all__ = [
    # Election views
    'ElectionListView', 'ElectionDetailView', 'ElectionCreateView', 'ElectionUpdateView',
    # Candidate views  
    'CandidateCreateView', 'CandidateUpdateView', 'CandidateDeleteView', 'CandidateDetailView',
    # Vote views
    'VoteView', 'VerifyResultsView', 'CloseElectionView',
    # Invitation views
    'send_invitations', 'manage_invitations', 'invitation_accept', 
    'resend_invitation', 'cancel_invitation', 'process_pending_invitation',
    # Base views
    'index', 'profile',
    # Legal views
    'terms', 'privacy', 'accessibility', 'contact', 'faq',
    # Auth views
    'CustomLoginView'
]