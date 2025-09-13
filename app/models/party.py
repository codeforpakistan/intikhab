"""
Party model for managing political parties
"""
from django.db import models


class Party(models.Model):
    """Model representing a political party"""
    
    name = models.CharField(max_length=100)
    symbol = models.FileField(upload_to='uploads/')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Party"
        verbose_name_plural = "Parties"
        ordering = ['name']