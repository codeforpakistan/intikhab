from django.db import models
from django.contrib.auth.models import User
from encrypted_model_fields.fields import EncryptedCharField
from app.encryption import Encryption
import json
from hashlib import sha256

# Create your models here.
class Election(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    description = models.TextField()
    private_key = EncryptedCharField(max_length=500, default="", editable=True)
    public_key = EncryptedCharField(max_length=500, default="", editable=False)
    encrypted_positive_total = EncryptedCharField(max_length=5000, default="", editable=False)
    encrypted_negative_total = EncryptedCharField(max_length=5000, default="", editable=False)
    encrypted_zero_sum = EncryptedCharField(max_length=5000, default="", editable=False)
    zero_randomness = EncryptedCharField(max_length=5000, default="", editable=False)
    decrypted_total = EncryptedCharField(max_length=500, default="", editable=False)
    active = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Party(models.Model):
    class Meta:
        verbose_name = "Party"
        verbose_name_plural = "Parties"

    name = models.CharField(max_length=100)
    symbol = models.FileField(upload_to='uploads/')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Candidate(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    symbol = models.FileField(upload_to='uploads/', null=True, blank=True)
    party = models.ForeignKey(Party, on_delete=models.PROTECT, null=True, blank=True)
    election = models.ForeignKey(Election, on_delete=models.PROTECT, related_name='candidates')
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user.get_full_name()

class Vote(models.Model):
    class Meta:
        unique_together = ('user', 'election')
    
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='votes')
    election = models.ForeignKey(Election, on_delete=models.PROTECT, related_name='votes')
    ballot = EncryptedCharField(max_length=5000, default="", editable=False)
    hashed = models.CharField(max_length=128, default="", editable=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + " - " + self.election.name

    def save(self, *args, **kwargs):
        if not self.ballot and hasattr(self, '_candidate'):
            try:
                candidates = self.election.candidates.order_by('id')
                candidate_ids = [candidate.id for candidate in candidates]
                unencrypted_ballot = [1 if x == self._candidate.id else 0 for x in candidate_ids]
                cleaned_key = self.election.public_key.replace("'", '"')
                public_key = json.loads(cleaned_key)
                encryption = Encryption(public_key=f"{public_key['g']},{public_key['n']}")
                
                encrypted_ballot = []
                for vote in unencrypted_ballot:
                    encrypted_vote = encryption.encrypt(vote)
                    encrypted_ballot.append(encrypted_vote.ciphertext)
                self.ballot = encrypted_ballot
                print(f"Encrypted ballot: {encrypted_ballot}")
                # Hash the vote for receipt
                data_to_hash = str(encrypted_ballot)
                self.hashed = sha256(data_to_hash.encode()).hexdigest()
                print(f"Hashed vote: {self.hashed}")
                delattr(self, '_candidate')
            except json.JSONDecodeError as e:
                print(f"Error decoding public key: {e}")
                print(f"Raw public key: {self.election.public_key}")
                print(f"Cleaned public key: {cleaned_key}")
                raise
            except Exception as e:
                print(f"Error during encryption: {e}")
                raise
            
        super().save(*args, **kwargs)

