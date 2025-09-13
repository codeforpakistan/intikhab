"""
Class-based views for Candidate model operations
"""
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy

from app.models import Candidate, Election
from app.forms import CandidateForm


class CandidateCreateView(LoginRequiredMixin, CreateView):
    """Add a candidate to an election"""
    model = Candidate
    form_class = CandidateForm
    template_name = 'app/candidates/create.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Check permissions and get election"""
        if not self._is_official(request.user):
            messages.error(request, "You don't have permission to add candidates.")
            return redirect('election_list')
        
        # Get the election for this candidate
        self.election = get_object_or_404(Election, pk=kwargs['election_pk'])
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Associate candidate with the election and create profile if needed"""
        form.instance.election = self.election
        response = super().form_valid(form)
        
        # Create user profile if it doesn't exist (since they're now a candidate)
        from app.models import Profile
        Profile.objects.get_or_create(user=self.object.user)
        
        messages.success(
            self.request, 
            f"Candidate '{self.object.user.get_full_name()}' has been added to the election!"
        )
        return response
    
    def get_success_url(self):
        return reverse_lazy('election_detail', kwargs={'pk': self.election.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['election'] = self.election
        
        # Check if there are any available candidates
        from django.contrib.auth.models import User
        from app.models import Candidate
        
        existing_candidate_users = Candidate.objects.filter(
            election=self.election
        ).values_list('user_id', flat=True)
        
        available_users = User.objects.filter(
            is_active=True,
            groups__name='Candidates'
        ).exclude(id__in=existing_candidate_users).distinct()
        
        context['no_candidates_available'] = available_users.count() == 0
        
        return context
    
    def get_form_kwargs(self):
        """Add election to the form kwargs for validation"""
        kwargs = super().get_form_kwargs()
        kwargs['election'] = self.election
        return kwargs
    
    def _is_official(self, user):
        """Check if user is an official who can manage candidates"""
        return user.is_superuser or user.groups.filter(name='Officials').exists()


class CandidateUpdateView(LoginRequiredMixin, UpdateView):
    """Edit an existing candidate"""
    model = Candidate
    form_class = CandidateForm
    template_name = 'app/candidates/edit.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Check permissions and get election"""
        self.election = get_object_or_404(Election, pk=kwargs['election_pk'])
        if not self._is_official(request.user):
            messages.error(request, "You don't have permission to edit candidates.")
            return redirect('election_detail', pk=self.election.pk)
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Handle successful form submission"""
        response = super().form_valid(form)
        messages.success(
            self.request, 
            f"Candidate '{self.object.user.get_full_name()}' has been updated successfully!"
        )
        return response
    
    def get_success_url(self):
        return reverse_lazy('election_detail', kwargs={'pk': self.election.pk})
    
    def get_context_data(self, **kwargs):
        """Add election to context"""
        context = super().get_context_data(**kwargs)
        context['election'] = self.election
        return context
    
    def _is_official(self, user):
        """Check if user is an official who can manage candidates"""
        return user.is_superuser or user.groups.filter(name='Officials').exists()


class CandidateDeleteView(LoginRequiredMixin, DeleteView):
    """Remove a candidate from an election"""
    model = Candidate
    template_name = 'app/candidates/delete.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Check permissions and election status"""
        self.election = get_object_or_404(Election, pk=kwargs['election_pk'])
        
        # Check if user can remove candidates from this election
        if not self._can_remove_candidate(request.user, self.election):
            messages.error(request, "You don't have permission to remove candidates from this election.")
            return redirect('election_detail', pk=self.election.pk)
        
        # Check if election has started (cannot remove candidates after voting starts)
        if not self.election.is_editable():
            messages.error(request, "Cannot remove candidates after the election has started.")
            candidate = self.get_object()
            return redirect('candidate_detail', election_pk=self.election.pk, pk=candidate.pk)
        
        return super().dispatch(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        """Handle candidate deletion"""
        candidate = self.get_object()
        candidate_name = str(candidate)  # Uses the __str__ method which calls get_full_name()
        
        response = super().delete(request, *args, **kwargs)
        messages.success(
            request, 
            f"Candidate '{candidate_name}' has been removed from the election."
        )
        return response
    
    def get_success_url(self):
        return reverse_lazy('election_detail', kwargs={'pk': self.election.pk})
    
    def get_context_data(self, **kwargs):
        """Add election to context"""
        context = super().get_context_data(**kwargs)
        context['election'] = self.election
        return context
    
    def _can_remove_candidate(self, user, election):
        """Check if user can remove candidates from this election"""
        # User can remove candidates if they are:
        # 1. The election creator/owner
        # 2. Superuser 
        # 3. Election manager (using new user extension)
        return (user == election.created_by or 
                user.is_superuser or 
                user.is_election_manager())
    
    def _is_official(self, user):
        """Check if user is an official who can manage candidates"""
        return user.is_superuser or user.groups.filter(name='Officials').exists()


class CandidateDetailView(LoginRequiredMixin, DetailView):
    """View a candidate's profile"""
    model = Candidate
    template_name = 'app/candidates/detail.html'
    context_object_name = 'candidate'
    
    def dispatch(self, request, *args, **kwargs):
        """Get election and verify candidate belongs to it"""
        self.election = get_object_or_404(Election, pk=kwargs['election_pk'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['election'] = self.election
        
        # Check if current user has voted in this election
        from app.models import Vote
        user_votes = Vote.objects.filter(election=self.election, user=self.request.user)
        context['voted'] = user_votes.count()
        
        # Check if current user can remove this candidate
        context['can_remove_candidate'] = self._can_remove_candidate(
            self.request.user, 
            self.election
        )
        
        return context
    
    def _can_remove_candidate(self, user, election):
        """Check if user can remove candidates from this election"""
        # User can remove candidates if they are:
        # 1. The election creator/owner
        # 2. Superuser 
        # 3. Election manager (using new user extension)
        return (user == election.created_by or 
                user.is_superuser or 
                user.is_election_manager())