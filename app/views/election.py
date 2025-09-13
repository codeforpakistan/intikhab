"""
Class-based views for Election model operations
"""
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from collections import defaultdict

from app.models import Election, Vote
from app.forms import ElectionForm, ElectionUpdateForm


class ElectionListView(LoginRequiredMixin, ListView):
    """List elections organized by status: ongoing, upcoming, and recently closed"""
    model = Election
    template_name = 'app/elections/list.html'
    context_object_name = 'elections'
    
    def get_context_data(self, **kwargs):
        """Organize elections by status with filtering"""
        context = super().get_context_data(**kwargs)
        from django.utils import timezone
        from datetime import timedelta
        now = timezone.now()
        
        # Get filter parameters
        status_filter = self.request.GET.get('status', 'all')
        search_term = self.request.GET.get('search', '').strip()
        date_range = self.request.GET.get('date_range', 'all')
        
        # Convert single status to list for backward compatibility
        if status_filter == 'all':
            selected_statuses = ['ongoing', 'upcoming', 'closed']
        else:
            selected_statuses = [status_filter]
        
        # Get all elections and apply search filter
        all_elections = Election.objects.all().select_related('created_by')
        
        if search_term:
            all_elections = all_elections.filter(name__icontains=search_term)
        
        # Apply date range filter
        if date_range != 'all':
            if date_range == 'this-week':
                start_date = now - timedelta(days=7)
                end_date = now + timedelta(days=7)
            elif date_range == 'this-month':
                start_date = now.replace(day=1)
                end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            elif date_range == 'next-month':
                next_month = now.replace(day=1) + timedelta(days=32)
                start_date = next_month.replace(day=1)
                end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            elif date_range == 'last-month':
                end_date = now.replace(day=1) - timedelta(days=1)
                start_date = end_date.replace(day=1)
            else:
                start_date = end_date = None
            
            if start_date and end_date:
                all_elections = all_elections.filter(
                    start_date__gte=start_date,
                    end_date__lte=end_date
                )
        
        # Organize by status and apply status filter
        ongoing_elections = []
        upcoming_elections = []
        recently_closed_elections = []
        
        for election in all_elections:
            status = election.get_status()
            if status == 'open' and 'ongoing' in selected_statuses:
                ongoing_elections.append(election)
            elif status in ['scheduled', 'inactive'] and 'upcoming' in selected_statuses:
                upcoming_elections.append(election)
            elif status in ['closed', 'expired'] and 'closed' in selected_statuses:
                recently_closed_elections.append(election)
        
        # Sort each category
        ongoing_elections.sort(key=lambda x: x.end_date)  # Soonest ending first
        upcoming_elections.sort(key=lambda x: x.start_date)  # Soonest starting first
        recently_closed_elections.sort(key=lambda x: x.end_date, reverse=True)  # Most recently closed first
        
        # Combine all filtered elections into a single list
        all_filtered_elections = ongoing_elections + upcoming_elections + recently_closed_elections
        
        # Sort the combined list: ongoing first (by end date), then upcoming (by start date), then closed (by end date desc)
        def sort_key(election):
            status = election.get_status()
            if status == 'open':
                return (0, election.end_date)  # Ongoing elections first, sorted by end date
            elif status in ['scheduled', 'inactive']:
                return (1, election.start_date)  # Upcoming elections second, sorted by start date
            else:  # closed/expired
                return (2, -election.end_date.timestamp())  # Closed elections last, sorted by end date desc
        
        all_filtered_elections.sort(key=sort_key)
        
        # Add pagination
        paginator = Paginator(all_filtered_elections, 6)  # Show 6 elections per page (3 rows of 2)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Prepare query parameters for pagination
        query_params = {
            'status': status_filter,
            'search': search_term,
            'date_range': date_range
        }
        
        context.update({
            'elections': page_obj,  # Paginated elections for template
            'page_obj': page_obj,  # Page object for pagination controls
            'query_params': query_params,  # For pagination partial
            'ongoing_elections': ongoing_elections,
            'upcoming_elections': upcoming_elections,
            'recently_closed_elections': recently_closed_elections,
            'elections_count': {
                'ongoing': len(ongoing_elections),
                'upcoming': len(upcoming_elections),
                'recently_closed': len(recently_closed_elections),
                'total': len(all_filtered_elections)
            },
            'selected_statuses': selected_statuses,
            'selected_status': status_filter,  # Single status for dropdown
            'search_term': search_term,
            'selected_date_range': date_range
        })
        
        return context
    
    def get_queryset(self):
        """Return empty queryset since we handle all elections in get_context_data"""
        return Election.objects.none()


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
        # User can edit if they are an election manager or the creator
        has_permission = (user.is_election_manager() or 
                         election.created_by == user)
        return has_permission and election.is_editable()
    
    def _count_votes(self, election):
        """Count votes for each candidate in an election"""
        if not election.can_show_results():
            return None  # Don't show results unless election is closed after voting
        
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
        if not request.user.is_election_creator():
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


class ElectionUpdateView(LoginRequiredMixin, UpdateView):
    """Edit an existing election"""
    model = Election
    form_class = ElectionUpdateForm
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
        # User can edit if they are an election manager or the creator
        has_permission = (user.is_election_manager() or 
                         election.created_by == user)
        return has_permission and election.is_editable()
    
    def _is_official(self, user):
        """Check if user is an official who can edit elections"""
        return user.is_election_manager()