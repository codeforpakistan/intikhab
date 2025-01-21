from django.db import models
from django.contrib.auth.models import User
from encrypted_model_fields.fields import EncryptedCharField
from app.encryption import Encryption, Ciphertext
import json

class Election(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    description = models.TextField()
    private_key = EncryptedCharField(max_length=500, default="", editable=False)
    public_key = EncryptedCharField(max_length=500, default="", editable=False)
    active = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    encrypted_tally = models.JSONField(null=True, blank=True)
    decrypted_tally = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.name
    
    def get_encryption_instance(self):
        # Convert the stored JSON public_key into the expected format
        public_key_data = json.loads(self.public_key.replace("'", '"'))  # Parse JSON safely
        public_key = f"{public_key_data['g']},{public_key_data['n']}"

        # Parse private_key JSON string into a dictionary
        private_key_data = json.loads(self.private_key.replace("'", '"'))
        private_key = private_key_data['phi']  # Extract 'phi' as an integer

        # Pass the parsed keys to the Encryption class
        return Encryption(public_key=public_key, private_key=str(private_key))

    
    def homomorphic_addition(self):
        encryption = self.get_encryption_instance()
        votes = self.votes.all()  # Related name from the Vote model
        encrypted_ballots = []
        for vote in votes:
            try:
                ballot_list = json.loads(vote.ballot)
                parsed_ballots = [Ciphertext.from_json(item) for item in ballot_list]
                encrypted_ballots.append(parsed_ballots)
            except json.JSONDecodeError as e:
                print(f"Error decoding ballot for vote {vote.id}: {e}")
                continue

        if not encrypted_ballots:
            return None  # No votes to add

        # Perform homomorphic addition
        total = encrypted_ballots[0]
        for ballot in encrypted_ballots[1:]:
            total = [encryption.add(t, b) for t, b in zip(total, ballot)]

        self.encrypted_tally = [ct.to_json() for ct in total]

        decrypted_total =  [self.decrypt(ct) for ct in total]

        self.decrypted_tally = decrypted_total

        self.save()

        return decrypted_total
    
    def decrypt(self, encrypted_vote):
        encryption = self.get_encryption_instance()
        return encryption.decrypt(encrypted_vote)

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
    ballot = models.JSONField(default=list, editable=False)
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
                
                # Encrypt each vote
                encrypted_ballot = []
                for vote in unencrypted_ballot:
                    encrypted_vote = encryption.encrypt(vote)
                    encrypted_ballot.append(encrypted_vote.to_json())
                self.ballot = json.dumps(encrypted_ballot)
                print(f"Encrypted votes: {encrypted_ballot}")
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

