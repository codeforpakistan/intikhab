"""
Class-based views for Election model operations
"""
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from collections import defaultdict

from app.models import Election, Vote
from app.forms import ElectionForm


class ElectionListView(LoginRequiredMixin, ListView):
    """List only active elections"""
    model = Election
    template_name = 'app/elections/list.html'
    context_object_name = 'elections'
    ordering = ['-created']
    
    def get_queryset(self):
        """Return only active elections"""
        return Election.objects.filter(active=True).order_by('-created')


class ElectionDetailView(LoginRequiredMixin, DetailView):
    """Display election details with voting options and results"""
    model = Election
    template_name = 'app/elections/detail.html'
    context_object_name = 'election'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        election = self.get_object()
        
        # Check if current user has voted
        user_votes = Vote.objects.filter(election=election, user=self.request.user)
        context['voted'] = user_votes.count()
        
        # Get vote results if election is closed
        context['vote_results'] = self._count_votes(election)
        
        # Check if user can edit this election
        context['can_edit'] = self._can_edit_election(election, self.request.user)
        
        return context
    
    def _can_edit_election(self, election, user):
        """Check if current user can edit this election"""
        # User can edit if they are:
        # 1. Superuser
        # 2. The creator of the election
        # 3. Member of Officials group (for backward compatibility with existing elections)
        return (user.is_superuser or 
                election.created_by == user or 
                user.groups.filter(name='Officials').exists())
    
    def _count_votes(self, election):
        """Count votes for each candidate in an election"""
        if election.active:
            return None  # Don't show results for active elections
        
        votes = Vote.objects.filter(election=election)
        vote_counts = defaultdict(int)
        
        # Parse ballot data to count votes
        for vote in votes:
            try:
                # Extract candidate_id from ballot format: "candidate_id:uuid"
                if isinstance(vote.ballot, list):
                    # Handle encrypted ballot list
                    continue
                candidate_id_str = vote.ballot.split(':')[0]
                candidate_id = int(candidate_id_str)
                vote_counts[candidate_id] += 1
            except (ValueError, IndexError, AttributeError):
                # Skip invalid ballot data
                continue
        
        # Create results with candidate details
        results = []
        candidates = election.candidates.all()
        total_votes = sum(vote_counts.values())
        
        for candidate in candidates:
            candidate_votes = vote_counts.get(candidate.id, 0)
            percentage = (candidate_votes / total_votes * 100) if total_votes > 0 else 0
            results.append({
                'candidate': candidate,
                'votes': candidate_votes,
                'percentage': round(percentage, 1)
            })
        
        # Sort by vote count (descending)
        results.sort(key=lambda x: x['votes'], reverse=True)
        
        return {
            'results': results,
            'total_votes': total_votes
        }


class ElectionCreateView(LoginRequiredMixin, CreateView):
    """Create a new election"""
    model = Election
    form_class = ElectionForm
    template_name = 'app/elections/create.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Check if user has permission to create elections"""
        if not self._is_official(request.user):
            messages.error(request, "You don't have permission to create elections.")
            return redirect('election_list')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Assign creator when election is created"""
        form.instance.created_by = self.request.user  # Set the creator
        response = super().form_valid(form)
        messages.success(
            self.request, 
            f"Election '{self.object.name}' has been created successfully! You can now add candidates to this election."
        )
        return response
    
    def get_success_url(self):
        return reverse_lazy('election_detail', kwargs={'pk': self.object.pk})
    
    def _is_official(self, user):
        """Check if user is an official who can create elections"""
        return user.is_superuser or user.groups.filter(name='Officials').exists()


class ElectionUpdateView(LoginRequiredMixin, UpdateView):
    """Edit an existing election"""
    model = Election
    form_class = ElectionForm
    template_name = 'app/elections/edit.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Check if user has permission to edit this specific election"""
        election = self.get_object()
        if not self._can_edit_election(election, request.user):
            messages.error(request, "You don't have permission to edit this election.")
            return redirect('election_detail', pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Handle successful form submission"""
        response = super().form_valid(form)
        messages.success(
            self.request, 
            f"Election '{self.object.name}' has been updated successfully!"
        )
        return response
    
    def get_success_url(self):
        return reverse_lazy('election_detail', kwargs={'pk': self.object.pk})
    
    def _can_edit_election(self, election, user):
        """Check if current user can edit this election"""
        # User can edit if they are:
        # 1. Superuser
        # 2. The creator of the election
        # 3. Member of Officials group (for backward compatibility with existing elections)
        return (user.is_superuser or 
                election.created_by == user or 
                user.groups.filter(name='Officials').exists())
    
    def _is_official(self, user):
        """Check if user is an official who can edit elections"""
        return user.is_superuser or user.groups.filter(name='Officials').exists()