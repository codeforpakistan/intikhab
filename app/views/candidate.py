"""
Class-based views for Candidate model operations
"""
from django.views.generic import CreateView, UpdateView, DeleteView
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
        """Associate candidate with the election"""
        form.instance.election = self.election
        response = super().form_valid(form)
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
        return context
    
    def _is_official(self, user):
        """Check if user is an official who can manage candidates"""
        return user.is_superuser or user.groups.filter(name='Officials').exists()


class CandidateUpdateView(LoginRequiredMixin, UpdateView):
    """Edit an existing candidate"""
    model = Candidate
    form_class = CandidateForm
    template_name = 'app/candidates/edit.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Check permissions"""
        if not self._is_official(request.user):
            messages.error(request, "You don't have permission to edit candidates.")
            candidate = self.get_object()
            return redirect('election_detail', pk=candidate.election.pk)
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
        return reverse_lazy('election_detail', kwargs={'pk': self.object.election.pk})
    
    def _is_official(self, user):
        """Check if user is an official who can manage candidates"""
        return user.is_superuser or user.groups.filter(name='Officials').exists()


class CandidateDeleteView(LoginRequiredMixin, DeleteView):
    """Remove a candidate from an election"""
    model = Candidate
    template_name = 'app/candidates/delete.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Check permissions"""
        if not self._is_official(request.user):
            messages.error(request, "You don't have permission to remove candidates.")
            candidate = self.get_object()
            return redirect('election_detail', pk=candidate.election.pk)
        return super().dispatch(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        """Handle candidate deletion"""
        candidate = self.get_object()
        candidate_name = candidate.user.get_full_name()
        election_pk = candidate.election.pk
        
        response = super().delete(request, *args, **kwargs)
        messages.success(
            request, 
            f"Candidate '{candidate_name}' has been removed from the election."
        )
        return response
    
    def get_success_url(self):
        return reverse_lazy('election_detail', kwargs={'pk': self.object.election.pk})
    
    def _is_official(self, user):
        """Check if user is an official who can manage candidates"""
        return user.is_superuser or user.groups.filter(name='Officials').exists()