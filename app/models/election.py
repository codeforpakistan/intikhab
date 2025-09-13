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
        # Elections are only open when active = True and today is between start and end
        return self.active and self.start_date <= now <= self.end_date
    
    def is_editable(self):
        """Check if this election can be edited"""
        from django.utils import timezone
        now = timezone.now()
        # Election is NOT editable if they are active and today is between start and end
        if self.active and self.start_date <= now <= self.end_date:
            return False
        return True
    
    def can_show_results(self):
        """Check if results can be displayed for this election"""
        from django.utils import timezone
        now = timezone.now()
        # Election results are only available when election is closed after voting
        return not self.active and now > self.end_date
    
    def get_status(self):
        """Get the current status of the election"""
        from django.utils import timezone
        now = timezone.now()
        
        if not self.active:
            if now > self.end_date:
                return "closed"  # Election is closed and voting period has ended
            else:
                return "inactive"  # Election is inactive (not yet activated)
        else:
            if now < self.start_date:
                return "scheduled"  # Election is active but voting hasn't started
            elif now > self.end_date:
                return "expired"  # Election is active but voting period has ended (needs to be closed)
            else:
                return "open"  # Election is active and voting is open
    
    def get_status_display(self):
        """Get display-friendly status text with appropriate styling class"""
        status = self.get_status()
        status_map = {
            'open': {'text': 'Voting Open', 'class': 'bg-success'},
            'scheduled': {'text': 'Scheduled', 'class': 'bg-warning'},
            'inactive': {'text': 'Inactive', 'class': 'bg-secondary'},
            'expired': {'text': 'Voting Ended', 'class': 'bg-danger'},
            'closed': {'text': 'Closed', 'class': 'bg-secondary'}
        }
        return status_map.get(status, {'text': 'Unknown', 'class': 'bg-secondary'})
    
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