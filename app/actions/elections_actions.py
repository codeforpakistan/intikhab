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

        # Here you would:
        # 1. Calculate encrypted_positive_total
        # 2. Calculate encrypted_negative_total
        # 3. Calculate encrypted_zero_sum
        # 4. Decrypt the final total using private key
        # 5. Set active to False
        try:
            # Get all votes for this election
            # votes = election.votes.all()
            # if not votes.exists():
            #     self.message_user(
            #         request,
            #         f"No votes found for election '{election.name}'",
            #         messages.WARNING
            #     )
            #     continue

            # # Load the public key
            # cleaned_key = election.public_key.replace("'", '"')
            # public_key = json.loads(cleaned_key)
            # encryption = Encryption(public_key=f"{public_key['g']},{public_key['n']}")
            
            # # Calculate totals
            # encrypted_positive_total = None
            # encrypted_negative_total = None
            # encrypted_zero_sum = None
            
            # # Process each vote's ballot
            # for vote in votes:
            #     ballot = json.loads(vote.ballot)
            #     # Add your logic here to calculate encrypted totals
            #     # This will depend on your specific encryption implementation
            
            # # Store the results
            # election.encrypted_positive_total = encrypted_positive_total
            # election.encrypted_negative_total = encrypted_negative_total
            # election.encrypted_zero_sum = encrypted_zero_sum
            
            # # Decrypt final total using private key
            # private_key = json.loads(election.private_key.replace("'", '"'))
            # # Add your decryption logic here
            # election.decrypted_total = 0  # Replace with actual decrypted total
            
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