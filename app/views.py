import uuid
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count
from collections import defaultdict
from app.models import Election, Candidate, Vote
from app.encryption import Encryption
from app.email_utils import send_vote_confirmation

# Create your views here.
def index(request):
    elections = Election.objects.all()
    return render(request, 'app/index.html', {'elections': elections})

@login_required
def profile(request):
    votes = Vote.objects.filter(user=request.user)
    return render(request, 'app/profile.html', {'votes': votes})

@login_required
def vote(request, election_id, candidate_id):
    try:
        election = Election.objects.get(pk=election_id)
        candidate = Candidate.objects.get(pk=candidate_id)
        
        # Check if voting is open for this election
        if not election.is_voting_open():
            return redirect('election_detail', pk=election.pk)
        
        # Check if user has already voted in this election
        existing_vote = Vote.objects.filter(user=request.user, election=election).first()
        if existing_vote:
            return redirect('election_detail', pk=election.pk)
        
        # Verify candidate belongs to this election
        if candidate.election != election:
            return redirect('election_detail', pk=election.pk)
        
        # Create encrypted ballot
        # For now, we'll use a simple format: candidate_id + random UUID
        # In a full implementation, this would use homomorphic encryption
        ballot_data = f"{candidate_id}:{uuid.uuid4().hex}"
        
        # If election has a public key, we could encrypt here
        if election.public_key:
            # TODO: Implement homomorphic encryption using the Encryption class
            encrypted_ballot = ballot_data  # Placeholder
        else:
            encrypted_ballot = ballot_data
        
        vote = Vote(user=request.user, election=election, ballot=encrypted_ballot)
        vote.save()
        
        # Send vote confirmation email
        if request.user.email:
            send_vote_confirmation(request.user, election)
        
        return redirect('election_detail', pk=election.pk)
    except (Election.DoesNotExist, Candidate.DoesNotExist):
        return redirect('election_list')
    except Exception as e:
        # Log the error in a real application
        return redirect('election_detail', pk=election.pk)

class ElectionListView(View):
    def get(self, request):
        elections = Election.objects.all()
        return render(request, 'app/elections/list.html', {'elections': elections})

def count_votes(election):
    """Count votes for each candidate in an election"""
    if election.active:
        return None  # Don't show results for active elections
    
    votes = Vote.objects.filter(election=election)
    vote_counts = defaultdict(int)
    
    # Parse ballot data to count votes
    for vote in votes:
        try:
            # Extract candidate_id from ballot format: "candidate_id:uuid"
            candidate_id_str = vote.ballot.split(':')[0]
            candidate_id = int(candidate_id_str)
            vote_counts[candidate_id] += 1
        except (ValueError, IndexError):
            # Skip invalid ballot data
            continue
    
    # Create results with candidate details
    results = []
    candidates = Candidate.objects.filter(election=election)
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

class ElectionDetailView(View):
    def get(self, request, pk):
        try:
            election = Election.objects.get(pk=pk)
            votes = Vote.objects.filter(election=election, user=request.user)
            
            # Get vote counting results if election is closed
            vote_results = count_votes(election)
            
            return render(request, 'app/elections/detail.html', {
                'election': election, 
                'voted': votes.count(),
                'vote_results': vote_results
            })
        except Election.DoesNotExist:
            return redirect('election_list')

@login_required
def close_election(request, pk):
    if not request.user.is_superuser:
        messages.error(request, "You don't have permission to close elections.")
        return redirect('election_detail', pk=pk)
    
    try:
        election = Election.objects.get(pk=pk)
        if not election.active:
            messages.warning(request, "Election is already closed.")
        else:
            election.active = False
            election.save()
            messages.success(request, f"Election '{election.name}' has been closed successfully.")
        return redirect('election_detail', pk=pk)
    except Election.DoesNotExist:
        messages.error(request, "Election not found.")
        return redirect('election_list')