import uuid
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from app.models import Election, Candidate, Vote
from app.encryption import Encryption

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

class ElectionDetailView(View):
    def get(self, request, pk):
        try:
            election = Election.objects.get(pk=pk)
            votes = Vote.objects.filter(election=election, user=request.user)
            return render(request, 'app/elections/detail.html', {
                'election': election, 
                'voted': votes.count()
            })
        except Election.DoesNotExist:
            return redirect('election_list')