from django.contrib import messages
import json
from app.encryption import Encryption, Ciphertext

def start_election(self, request, queryset):
        for election in queryset:
            if election.active:
                self.message_user(
                    request,
                    f"Election '{election.name}' is already started",
                    messages.INFO
                )
                continue
            # We can have the key generation logic here if we want.
            election.active = True
            election.save()

            self.message_user(
                request,
                f"Successfully started election '{election.name}'",
                messages.SUCCESS
            ) 

def end_election(modeladmin, request, queryset):
    for election in queryset:
        if not election.active:
            modeladmin.message_user(
                request,
                f"Election '{election.name}' is already ended",
                messages.WARNING
            )
            continue
        try:
            votes = election.votes.all()
            if not votes.exists():
                modeladmin.message_user(
                    request,
                    f"No votes found for election '{election.name}'",
                    messages.WARNING
                )
                continue

            cleaned_key = election.public_key.replace("'", '"')
            public_key = json.loads(cleaned_key)
            encryption = Encryption(public_key=f"{public_key['g']},{public_key['n']}")
            candidates_length = len(json.loads(votes[0].ballot))
            encrypted_positive_total = [None] * candidates_length
            encrypted_negative_total = [None] * candidates_length
            encrypted_zero_sum = [None] * candidates_length
            
            for i in range(len(votes)):
                ballot = json.loads(votes[i].ballot)
                negative_ballot = json.loads(votes[i].negative_ballot)
                for j in range(len(ballot)):
                    json_str_positive = json.dumps({'ciphertext': ballot[j], 'randomness': None})
                    json_str_negative = json.dumps({'ciphertext': negative_ballot[j], 'randomness': None})
                    ct_temp_positive = Ciphertext.from_json(json_str_positive)
                    ct_temp_negative = Ciphertext.from_json(json_str_negative)
                    if i == 0:
                        encrypted_positive_total[j] = ct_temp_positive    
                        encrypted_negative_total[j] = ct_temp_negative
                    else:
                        encrypted_positive_total[j] = encryption.add(encrypted_positive_total[j], ct_temp_positive)
                        encrypted_negative_total[j] = encryption.add(encrypted_negative_total[j], ct_temp_negative)
            
            for i in range(len(encrypted_positive_total)):
                encrypted_zero_sum[i] = encryption.add(encrypted_positive_total[i], encrypted_negative_total[i])
            # Convert Ciphertext objects to JSON-serializable format
            serialized_positive_total = [ct.to_json() for ct in encrypted_positive_total]
            serialized_negative_total = [ct.to_json() for ct in encrypted_negative_total]
            serialized_zero_sum = [ct.to_json() for ct in encrypted_zero_sum]

            election.encrypted_positive_total = json.dumps(serialized_positive_total)
            election.encrypted_negative_total = json.dumps(serialized_negative_total)
            election.encrypted_zero_sum = json.dumps(serialized_zero_sum)
            
            # End the election
            election.active = False
            election.save()
            
            modeladmin.message_user(
                request,
                f"Successfully ended election '{election.name}'",
                messages.SUCCESS
            )
            
        except Exception as e:
            modeladmin.message_user(
                request,
                f"Error ending election '{election.name}': {str(e)}",
                messages.ERROR
            )   

# Add a description for the admin interface
end_election.short_description = "End selected elections"
start_election.short_description = "Start selected elections"