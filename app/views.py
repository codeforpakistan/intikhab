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
        # TODO: get the decrypted total and show in the detail.html
        decrypted_total = []
        cleaned_public_key = election.public_key.replace("'", '"')
        cleaned_private_key = election.private_key.replace("'", '"')
        public_key = json.loads(cleaned_public_key)
        private_key = json.loads(cleaned_private_key)
        encryption = Encryption(public_key=f"{public_key['g']},{public_key['n']}", private_key=f"{private_key['phi']}")
        cleaned_encrypted_positive_total = election.encrypted_positive_total.replace("'", '"')
        encrypted_positive_total = json.loads(cleaned_encrypted_positive_total)
        for i in encrypted_positive_total:
            tally_ciphertext = Ciphertext.from_json(i)
            decrypted_total.append(encryption.decrypt(tally_ciphertext))
        return render(request, 'app/elections/detail.html', {'election': election, 'voted': votes.count, 'receipt': votes.first(), 'decrypted_total': decrypted_total})