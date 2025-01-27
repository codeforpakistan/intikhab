from django.contrib import admin, messages
from app.models import Election, Candidate, Party, Vote
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


admin.site.register(Election, ElectionAdmin)
admin.site.register(Candidate, CandidateAdmin)
admin.site.register(Party, PartyAdmin)
admin.site.register(Vote, VoteAdmin)
