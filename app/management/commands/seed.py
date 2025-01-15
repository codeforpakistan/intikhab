from django.core.management.base import BaseCommand, CommandError
from app.models import Election, Candidate, Party, Vote
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Group, Permission
from app.encryption import Encryption


class Command(BaseCommand):
    help = "Sets up a dummy election and candidates"

    def handle(self, *args, **options):

        try:
            # Create groups and assign permissions
            officials = Group.objects.create(name="Officials")
            content_types = ContentType.objects.filter(
                app_label="app", model__in=["Election", "Party"]
            )
            permissions = Permission.objects.filter(content_type__in=content_types)
            officials.permissions.set(list(permissions))
            officials.save()
            self.stdout.write(self.style.SUCCESS('Group created with permissions: "%s"' % officials.name))
            
            candidates = Group.objects.create(name="Candidates")
            content_types = ContentType.objects.filter(
                app_label="app", model__in=["Candidate"]
            )
            permissions = Permission.objects.filter(content_type__in=content_types)
            candidates.permissions.set(list(permissions))
            candidates.save()
            self.stdout.write(self.style.SUCCESS('Group created with permissions: "%s"' % candidates.name))

            citizens = Group.objects.create(name="Citizens")

            # Create superuser
            admin = User.objects.create_superuser(
                username="admin",
                email="admin@example.org",
                password="admin"
            )
            self.stdout.write(self.style.SUCCESS('User created: "%s"' % admin.username))

            # Create officials, candidates and citizens
            official = User.objects.create_user(
                username="official",
                email="official@example.org",
                password="official"
            )
            official.groups.add(officials)
            official.save()
            self.stdout.write(self.style.SUCCESS('User created: "%s"' % official.username))

            candidate = User.objects.create_user(
                username="candidate",
                email="candidate@example.org",
                password="candidate"
            )
            candidate.groups.add(candidates)
            candidate.save()
            self.stdout.write(self.style.SUCCESS('User created: "%s"' % candidate.username))
            
            citizen = User.objects.create_superuser(
                username="citizen",
                email="citizen@example.org",
                password="citizen"
            )
            citizen.groups.add(citizens)
            citizen.save()
            self.stdout.write(self.style.SUCCESS('User created: "%s"' % citizen.username))

            encryption = Encryption()
            public_key = encryption.paillier.keys['public_key']
            private_key = encryption.paillier.keys['private_key']

        except:
            pass

        
        election = Election.objects.create(
            name="Presidential Election",
            start_date="2022-01-01 00:00:00",
            end_date="2022-01-31 23:59:59",
            description="This is a dummy election",
            public_key=public_key,
            private_key=private_key,
            active=True,
        )

        rnc = Party.objects.create(
            name="Republican Party",
            symbol="uploads/republican.jpg",
        )

        dnc = Party.objects.create(
            name="Democratic Party",
            symbol="uploads/democrats.jpg",
        )


        self.stdout.write(self.style.SUCCESS("Successfully created dummy election and candidates"))