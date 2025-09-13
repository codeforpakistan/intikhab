"""
Election model for managing elections in the voting system
"""
from django.db import models
from django.contrib.auth.models import User


class Election(models.Model):
    """Model representing an election with its details and status"""
    
    name = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    description = models.TextField()
    created_by = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='created_elections', 
        null=True, 
        blank=True
    )
    
    # Encryption-related fields
    private_key = models.CharField(max_length=500, default="", editable=False)
    public_key = models.CharField(max_length=500, default="", editable=False)
    encrypted_positive_total = models.CharField(max_length=5000, default="", editable=False)
    encrypted_negative_total = models.CharField(max_length=5000, default="", editable=False)
    encrypted_zero_sum = models.CharField(max_length=5000, default="", editable=False)
    zero_randomness = models.CharField(max_length=5000, default="", editable=False)
    decrypted_total = models.CharField(max_length=500, default="", editable=False)
    
    # Status fields
    active = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    def is_voting_open(self):
        """Check if voting is currently open for this election"""
        from django.utils import timezone
        now = timezone.now()
        return self.active and self.start_date <= now <= self.end_date
    
    def get_status(self):
        """Get the current status of the election"""
        if not self.active:
            return "Inactive"
        
        from django.utils import timezone
        now = timezone.now()
        
        if now < self.start_date:
            return "Scheduled"
        elif now > self.end_date:
            return "Closed"
        else:
            return "Active"
    
    def get_total_votes(self):
        """Get the total number of votes cast in this election"""
        return self.votes.count()
    
    def get_candidates_count(self):
        """Get the number of candidates in this election"""
        return self.candidates.count()
    
    def can_be_edited_by(self, user):
        """Check if a user can edit this election"""
        return (user.is_superuser or 
                self.created_by == user or 
                user.groups.filter(name='Officials').exists())
    
    class Meta:
        ordering = ['-created']
        verbose_name = "Election"
        verbose_name_plural = "Elections"