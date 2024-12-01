from django.contrib import admin
from app.models import Election, Candidate, Party, Vote

# Register your models here.
class ElectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'active', 'created')

class CandidateAdmin(admin.ModelAdmin):
    list_display = ('user', 'party', 'election', 'created')

class PartyAdmin(admin.ModelAdmin):
    list_display = ('name', 'created')

class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'election', 'ballot', 'created')
    # readonly_fields = ('created', 'user', 'election', 'ballot')


admin.site.register(Election, ElectionAdmin)
admin.site.register(Candidate, CandidateAdmin)
admin.site.register(Party, PartyAdmin)
admin.site.register(Vote, VoteAdmin)
