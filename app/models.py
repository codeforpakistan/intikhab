from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Election(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    description = models.TextField()
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
    ballot = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + " - " + self.election.name

