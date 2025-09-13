from django.contrib import admin, messages
from app.models import Election, Candidate, Party, Vote, Profile
from app.encryption import Encryption, Ciphertext
import json
from app.actions.elections_actions import start_election, end_election

# Register your models here.
class ElectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'active', 'created')

    actions = [start_election, end_election]

class CandidateAdmin(admin.ModelAdmin):
    list_display = ('user', 'party', 'election', 'created')

class PartyAdmin(admin.ModelAdmin):
    list_display = ('name', 'created')

class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'election', 'ballot', 'created', 'hashed')
    # readonly_fields = ('created', 'user', 'election', 'ballot')

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_display_name', 'get_age', 'location', 'gender', 'created')
    list_filter = ('gender', 'created')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'location')
    readonly_fields = ('created', 'updated')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'avatar')
        }),
        ('Personal Details', {
            'fields': ('date_of_birth', 'location', 'gender')
        }),
        ('Profile Content', {
            'fields': ('profile', 'manifesto')
        }),
        ('Metadata', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',)
        }),
    )


admin.site.register(Election, ElectionAdmin)
admin.site.register(Candidate, CandidateAdmin)
admin.site.register(Party, PartyAdmin)
admin.site.register(Vote, VoteAdmin)
admin.site.register(Profile, ProfileAdmin)
