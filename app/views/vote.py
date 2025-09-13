"""
Class-based views for voting and result operations
"""
import uuid
import json
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404

from app.models import Election, Candidate, Vote
from app.encryption import Encryption
from app.email_utils import send_vote_confirmation


class VoteView(LoginRequiredMixin, View):
    """Handle user voting for a candidate"""
    
    def post(self, request, election_id, candidate_id):
        """Process a vote submission"""
        try:
            election = get_object_or_404(Election, pk=election_id)
            candidate = get_object_or_404(Candidate, pk=candidate_id)
            
            # Validate voting conditions
            if not self._can_vote(request.user, election, candidate):
                return redirect('election_detail', pk=election.pk)
            
            # Create encrypted ballot
            ballot_data = self._create_ballot(candidate)
            
            # Create and save the vote
            vote = Vote(
                user=request.user, 
                election=election, 
                ballot=ballot_data
            )
            vote._candidate = candidate  # Temporary attribute for encryption
            vote.save()
            
            # Send confirmation email
            if request.user.email:
                send_vote_confirmation(request.user, election)
            
            messages.success(request, "Your vote has been recorded successfully!")
            return redirect('election_detail', pk=election.pk)
            
        except (Election.DoesNotExist, Candidate.DoesNotExist):
            messages.error(request, "Invalid election or candidate.")
            return redirect('election_list')
        except Exception as e:
            messages.error(request, "An error occurred while processing your vote.")
            return redirect('election_detail', pk=election_id)
    
    def _can_vote(self, user, election, candidate):
        """Check if user can vote in this election for this candidate"""
        # Check if voting is open
        if not election.is_voting_open():
            messages.error(user, "Voting is not currently open for this election.")
            return False
        
        # Check if user already voted
        if Vote.objects.filter(user=user, election=election).exists():
            messages.error(user, "You have already voted in this election.")
            return False
        
        # Check if candidate belongs to this election
        if candidate.election != election:
            messages.error(user, "Invalid candidate for this election.")
            return False
        
        return True
    
    def _create_ballot(self, candidate):
        """Create ballot data for the vote"""
        # Simple format for now: candidate_id + random UUID
        return f"{candidate.id}:{uuid.uuid4().hex}"


class CloseElectionView(LoginRequiredMixin, View):
    """Close an election (only for officials)"""
    
    def post(self, request, pk):
        """Close the specified election"""
        if not self._is_official(request.user):
            messages.error(request, "You don't have permission to close elections.")
            return redirect('election_detail', pk=pk)
        
        try:
            election = get_object_or_404(Election, pk=pk)
            election.active = False
            election.save()
            
            messages.success(request, f"Election '{election.name}' has been closed.")
            return redirect('election_detail', pk=pk)
            
        except Election.DoesNotExist:
            messages.error(request, "Election not found.")
            return redirect('election_list')
    
    def _is_official(self, user):
        """Check if user is an official who can close elections"""
        return user.is_superuser or user.groups.filter(name='Officials').exists()


class VerifyResultsView(LoginRequiredMixin, View):
    """Verify election results using homomorphic encryption"""
    
    def get(self, request, election_id):
        """Display results verification page"""
        try:
            election = get_object_or_404(Election, pk=election_id)
            
            # Perform verification if election has encryption data
            verified = self._verify_results(election)
            
            return render(request, 'app/elections/verify_results.html', {
                'election': election, 
                'verified': verified
            })
            
        except Election.DoesNotExist:
            raise Http404("Election not found")
    
    def _verify_results(self, election):
        """Verify election results using homomorphic encryption"""
        try:
            if not election.public_key:
                return None  # No encryption data available
            
            # Parse public key
            cleaned_key = election.public_key.replace("'", '"')
            public_key = json.loads(cleaned_key)
            encryption = Encryption(public_key=f"{public_key['g']},{public_key['n']}")
            
            # Convert decrypted total to negative vector
            decrypted_total = json.loads(election.decrypted_total)
            decrypted_negative_total = [-x for x in decrypted_total]
            
            # Encrypt negative total
            encrypted_negative_total = []
            for i in decrypted_negative_total:
                encrypted_negative_total.append(encryption.encrypt(plaintext=i, rand=1))
            
            # Get encrypted positive total and compute zero sum
            encrypted_positive_total = json.loads(election.encrypted_positive_total)
            encrypted_zero_sum = []
            
            for i in range(len(encrypted_positive_total)):
                from app.encryption import Ciphertext
                temp_ept = Ciphertext.from_json(encrypted_positive_total[i])
                encrypted_zero_sum.append(encryption.add(temp_ept, encrypted_negative_total[i]))
            
            # Recalculate zero sum with stored randomness
            zero_randomness = json.loads(election.zero_randomness)
            recalculated_zero_sum = []
            for i in range(len(zero_randomness)):
                recalculated_zero_sum.append(encryption.encrypt(plaintext=0, rand=zero_randomness[i]))
            
            # Verify if sums match
            for i in range(len(encrypted_zero_sum)):
                if encrypted_zero_sum[i].ciphertext != recalculated_zero_sum[i].ciphertext:
                    return False
            
            return True
            
        except (json.JSONDecodeError, KeyError, IndexError, ValueError) as e:
            # Return None if verification cannot be performed
            return None