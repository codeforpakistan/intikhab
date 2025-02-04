import uuid
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from app.models import Election, Candidate, Vote
from app.encryption import Encryption, Ciphertext
import json

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
    election = Election.objects.get(pk=election_id)
    candidate = Candidate.objects.get(pk=candidate_id)
    try:
        vote = Vote(user=request.user, election=election)
        vote._candidate = candidate
        vote.save()
        return redirect('election_detail', pk=election.pk)
    except:
        return redirect('election_detail', pk=election.pk)

class ElectionListView(View):
    def get(self, request):
        elections = Election.objects.all()
        return render(request, 'app/elections/list.html', {'elections': elections})

class ElectionDetailView(View):
    def get(self, request, pk):
        election = Election.objects.get(pk=pk)
        votes = Vote.objects.filter(election=election, user=request.user)
        return render(request, 'app/elections/detail.html', {'election': election, 'voted': votes.count, 'receipt': votes.first()})

class VerifyResultsView(View):
    def get(self, request, election_id):
        election = Election.objects.get(pk=election_id)
        cleaned_key = election.public_key.replace("'", '"')
        public_key = json.loads(cleaned_key)
        encryption = Encryption(public_key=f"{public_key['g']},{public_key['n']}")
        
        # convert the decrypted total to negative vector
        decrypted_total = json.loads(election.decrypted_total)
        decrypted_negative_total = [-x for x in decrypted_total]
        encrypted_negative_total = []
        for i in decrypted_negative_total:
            encrypted_negative_total.append(encryption.encrypt(plaintext=i, rand=1))
        
        encrypted_positive_total = json.loads(election.encrypted_positive_total)
        encrypted_zero_sum = []
        for i in range(len(encrypted_positive_total)):
            temp_ept = Ciphertext.from_json(encrypted_positive_total[i])
            encrypted_zero_sum.append(encryption.add(temp_ept, encrypted_negative_total[i]))
        
        zero_randomness = json.loads(election.zero_randomness)
        recalculated_zero_sum = []
        for i in range(len(zero_randomness)):
            recalculated_zero_sum.append(encryption.encrypt(plaintext=0, rand=zero_randomness[i]))
        
        print(encrypted_zero_sum)
        print(recalculated_zero_sum)
        print(encrypted_zero_sum == recalculated_zero_sum)
        for i in range(len(encrypted_zero_sum)):
            if encrypted_zero_sum[i].ciphertext != recalculated_zero_sum[i].ciphertext:
                verified = False
                break
        else:
            verified = True
        return render(request, 'app/elections/verify_results.html', {'election': election, 'verified': verified})